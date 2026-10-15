# /// script
# requires-python = ">=3.12"
# dependencies = ["httpx>=0.28,<1"]
# ///
"""Snapshot real da API do PNCP para o laboratório (MVP Radar de Licitações).

Gera os CSVs de `radar-licitacoes/dados/csv/` a partir da API pública do PNCP,
aplicando o tratamento de LGPD ANTES de gravar qualquer arquivo (o repositório é
público). Os textos ficam sem limpeza de propósito: limpar é tarefa da estagiária.

Etapas (cada uma retomável pelo cache em disco):
  contratacoes  contratações da UF com proposta aberta (/contratacoes/proposta)
  itens         itens de cada contratação (/orgaos/{cnpj}/compras/{ano}/{seq}/itens)
  contratos     contratos publicados na janela, filtrados pela UF no cliente
                (o endpoint /contratos não tem filtro de UF)
  csv           monta os CSVs, aplica LGPD, valida e escreve o MANIFESTO.json

Uso (a partir desta pasta):
  uv run snapshot_pncp.py --uf MG --saida ../../../radar-licitacoes/dados/csv \
      --cache ../../../.cache/pncp

O "pepper" usado para pseudonimizar pessoas físicas fica no cache (arquivo
`.pepper`) ou na variável SNAPSHOT_PEPPER. Ele NUNCA deve ser versionado.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import hmac
import io
import json
import os
import random
import re
import secrets
import sys
import time
import unicodedata
from collections import Counter, defaultdict
from collections.abc import Callable, Iterable
from datetime import date, datetime, timedelta
from functools import lru_cache
from pathlib import Path
from typing import Any

import httpx

API_CONSULTA = "https://pncp.gov.br/api/consulta/v1"
API_PNCP = "https://pncp.gov.br/api/pncp/v1"
USER_AGENT = (
    "pontidata-laboratorio-snapshot/1.0 "
    "(+https://github.com/Ponte-Informatica-Pontidata/laboratorio)"
)

# ---------------------------------------------------------------------------
# Cliente HTTP gentil: intervalo mínimo entre chamadas, backoff em 429/5xx
# ---------------------------------------------------------------------------


class ClientePncp:
    """Cliente com ritmo controlado. Em 429 aumenta o intervalo (AIMD)."""

    def __init__(self, intervalo: float, log: Callable[[str], None]) -> None:
        self.http = httpx.Client(
            timeout=httpx.Timeout(120.0, connect=20.0),
            headers={"Accept": "application/json", "User-Agent": USER_AGENT},
            follow_redirects=True,
        )
        self.intervalo_piso = intervalo
        self.intervalo = intervalo
        self._ultimo = 0.0
        self._sucessos_seguidos = 0
        self.log = log
        self.stats: Counter[str] = Counter()

    def _esperar_vez(self) -> None:
        espera = self.intervalo - (time.monotonic() - self._ultimo)
        if espera > 0:
            time.sleep(espera)
        self._ultimo = time.monotonic()

    def _backoff(self, tentativa: int, retry_after: str | None, motivo: str) -> None:
        if retry_after and retry_after.strip().isdigit():
            espera = float(retry_after.strip())
        else:
            espera = min(180.0, 2.0**tentativa) + random.uniform(0, 1.5)
        self.log(f"  ! {motivo}: aguardando {espera:.1f}s (tentativa {tentativa})")
        time.sleep(espera)

    def get_json(self, url: str, params: dict[str, Any] | None = None) -> Any:
        for tentativa in range(1, 10):
            self._esperar_vez()
            self.stats["requisicoes"] += 1
            try:
                resp = self.http.get(url, params=params)
            except (httpx.TimeoutException, httpx.TransportError) as exc:
                self.stats["erros_rede"] += 1
                self._backoff(tentativa, None, type(exc).__name__)
                continue
            if resp.status_code == 200:
                self._sucessos_seguidos += 1
                # Recupera o ritmo aos poucos depois de um 429 (aumento aditivo, redução multiplicativa)
                if self._sucessos_seguidos >= 50 and self.intervalo > self.intervalo_piso:
                    self.intervalo = max(self.intervalo_piso, self.intervalo * 0.85)
                    self._sucessos_seguidos = 0
                return resp.json() if resp.content else None
            if resp.status_code == 204:
                self.stats["http_204"] += 1
                return None
            if resp.status_code == 429 or resp.status_code >= 500:
                self.stats[f"http_{resp.status_code}"] += 1
                if resp.status_code == 429:
                    self.intervalo = min(6.0, self.intervalo * 1.5)
                    self._sucessos_seguidos = 0
                self._backoff(tentativa, resp.headers.get("Retry-After"), f"HTTP {resp.status_code}")
                continue
            self.stats[f"http_{resp.status_code}"] += 1
            raise ErroRequisicao(resp.status_code, str(resp.url), resp.text[:300])
        raise ErroRequisicao(0, url, f"desisti depois de 9 tentativas ({params})")


class ErroRequisicao(RuntimeError):
    def __init__(self, status: int, url: str, corpo: str) -> None:
        super().__init__(f"HTTP {status} em {url}: {corpo}")
        self.status = status


def com_cache(caminho: Path, buscar: Callable[[], Any]) -> Any:
    """Lê do cache ou busca e grava de forma atômica (retomável)."""
    if caminho.exists():
        return json.loads(caminho.read_text(encoding="utf-8"))
    dados = buscar()
    caminho.parent.mkdir(parents=True, exist_ok=True)
    tmp = caminho.with_suffix(".tmp")
    tmp.write_text(json.dumps(dados, ensure_ascii=False), encoding="utf-8")
    tmp.replace(caminho)
    return dados


# ---------------------------------------------------------------------------
# Etapas de extração
# ---------------------------------------------------------------------------


def etapa_contratacoes(cli: ClientePncp, cache: Path, uf: str, data_final: str, log) -> list[dict]:
    pasta = cache / "contratacoes" / f"{uf}_{data_final}"
    vistos: dict[str, dict] = {}
    pagina, total_paginas = 1, None
    while total_paginas is None or pagina <= total_paginas:
        def buscar(pagina: int = pagina) -> Any:
            resp = cli.get_json(
                f"{API_CONSULTA}/contratacoes/proposta",
                {"dataFinal": data_final, "uf": uf, "pagina": pagina, "tamanhoPagina": 50},
            )
            return resp or {"data": [], "totalPaginas": 0, "totalRegistros": 0}

        resp = com_cache(pasta / f"p{pagina:04d}.json", buscar)
        if total_paginas is None:
            total_paginas = int(resp.get("totalPaginas") or 0)
            log(f"contratacoes: {resp.get('totalRegistros')} registros em {total_paginas} páginas")
        for reg in resp.get("data") or []:
            chave = reg.get("numeroControlePNCP")
            anterior = vistos.get(chave)
            if anterior is None or (reg.get("dataAtualizacao") or "") >= (anterior.get("dataAtualizacao") or ""):
                vistos[chave] = reg
        if pagina % 20 == 0:
            log(f"  contratacoes: página {pagina}/{total_paginas}")
        pagina += 1
    log(f"contratacoes: {len(vistos)} únicas após deduplicar")
    return list(vistos.values())


def etapa_itens(
    cli: ClientePncp, cache: Path, contratacoes: list[dict], log, limite: int = 0, inversa: bool = False
) -> tuple[dict[str, list[dict]], list[dict]]:
    pasta = cache / "itens"
    itens: dict[str, list[dict]] = {}
    falhas: list[dict] = []
    # inversa=True permite um segundo processo começar do fim (os dois se encontram no meio, pelo cache)
    ordenadas = sorted(contratacoes, key=lambda r: r["numeroControlePNCP"], reverse=inversa)
    if limite:
        ordenadas = ordenadas[:limite]
    total = len(ordenadas)
    for i, c in enumerate(ordenadas, start=1):
        cnpj = c["orgaoEntidade"]["cnpj"]
        ano, seq = c["anoCompra"], c["sequencialCompra"]
        url = f"{API_PNCP}/orgaos/{cnpj}/compras/{ano}/{seq}/itens"

        def buscar(url: str = url) -> Any:
            todos: list[dict] = []
            pagina = 1
            while True:
                lote = cli.get_json(url, {"pagina": pagina, "tamanhoPagina": 500}) or []
                todos.extend(lote)
                if len(lote) < 500:
                    return todos
                pagina += 1

        try:
            itens[c["numeroControlePNCP"]] = com_cache(pasta / f"{cnpj}_{ano}_{seq}.json", buscar)
        except ErroRequisicao as exc:
            falhas.append({"numero_controle_pncp": c["numeroControlePNCP"], "status": exc.status})
        if i % 250 == 0 or i == total:
            log(f"  itens: {i}/{total} contratações (falhas: {len(falhas)}; intervalo {cli.intervalo:.2f}s)")
    return itens, falhas


def etapa_contratos(cli: ClientePncp, cache: Path, uf: str, inicio: date, fim: date, log) -> tuple[list[dict], dict]:
    pasta = cache / "contratos" / uf
    vistos: dict[str, dict] = {}
    resumo = {"registros_nacionais": 0, "dias": 0}
    dia = inicio
    while dia <= fim:
        d = dia.strftime("%Y%m%d")
        pagina, total_paginas = 1, None
        while total_paginas is None or pagina <= total_paginas:
            def buscar(d: str = d, pagina: int = pagina) -> Any:
                resp = cli.get_json(
                    f"{API_CONSULTA}/contratos",
                    {"dataInicial": d, "dataFinal": d, "pagina": pagina, "tamanhoPagina": 500},
                ) or {"data": [], "totalPaginas": 0, "totalRegistros": 0}
                filtrados = [r for r in resp.get("data") or [] if (r.get("unidadeOrgao") or {}).get("ufSigla") == uf]
                meta = {k: v for k, v in resp.items() if k != "data"}
                meta["registros_na_pagina"] = len(resp.get("data") or [])
                return {"meta": meta, "data": filtrados}

            resp = com_cache(pasta / d / f"p{pagina:04d}.json", buscar)
            if total_paginas is None:
                total_paginas = int(resp["meta"].get("totalPaginas") or 0)
                resumo["registros_nacionais"] += int(resp["meta"].get("totalRegistros") or 0)
            for reg in resp["data"]:
                chave = reg.get("numeroControlePNCP")
                anterior = vistos.get(chave)
                if anterior is None or (reg.get("dataAtualizacao") or "") >= (anterior.get("dataAtualizacao") or ""):
                    vistos[chave] = reg
            pagina += 1
        resumo["dias"] += 1
        log(f"  contratos {d}: acumulado {len(vistos)} de {uf} (intervalo {cli.intervalo:.2f}s)")
        dia += timedelta(days=1)
    return list(vistos.values()), resumo


# ---------------------------------------------------------------------------
# LGPD
# ---------------------------------------------------------------------------

RE_CPF_FORMATADO = re.compile(r"(?<!\d)\d{3}\.\d{3}\.\d{3}-\d{2}(?!\d)")
RE_CPF_PARCIAL = re.compile(r"[*xX]{3}\.\d{3}\.\d{3}-[*xX]{2}")
RE_ONZE_DIGITOS = re.compile(r"(?<!\d)\d{11}(?!\d)")
# Número único de processo judicial (CNJ): NNNNNNN-DD.AAAA.J.TR.OOOO. Em compras de saúde por ordem
# judicial ele leva ao nome do paciente (dado sensível, art. 11 da LGPD).
RE_PROCESSO_CNJ = re.compile(r"(?<!\d)\d{7}-?\d{2}\.?\d{4}\.?\d\.?\d{2}\.?\d{4}(?!\d)")
# Palavras que quase sempre antecedem o nome de uma pessoa. "menor", "criança" e "usuário" ficaram de
# fora de propósito: "Menor Preço Global" e "Programa Criança Feliz" seriam falsos positivos.
RE_CHAVE_PESSOA = re.compile(
    r"(?i:(?:\b(?:pacientes?|mun[ií]cipe|requerente|impetrante|benefici[aá]ri[oa]|genitora?)\b"
    r"|\bsra?\.|\bem\s+favor\s+d[aeo]s?\b))[\s:,.\-–]*"
)
# Nome em "Título" (Maria Aparecida dos Santos): 2+ palavras com inicial maiúscula e resto minúsculo
RE_NOME_TITULO = re.compile(r"[A-ZÀ-Ý][a-zà-ÿ'´]+(?:\s+(?:(?:d[aeo]s?|e)\s+)?[A-ZÀ-Ý][a-zà-ÿ'´]+){1,5}")
# Nome em MAIÚSCULAS (MARIA DA SILVA): só conta se a 1ª palavra for um prenome comum (lista abaixo)
RE_NOME_MAIUSCULO = re.compile(r"[A-ZÀ-Ý]{2,}(?:\s+(?:(?:D[AEO]S?|E)\s+)?[A-ZÀ-Ý]{2,}){1,4}")
PRIMEIROS_NOMES = set("""
maria jose ana joao antonio francisco carlos paulo pedro lucas luiz luis marcos gabriel rafael daniel marcelo
bruno eduardo felipe raimundo rodrigo manoel manuel mateus matheus andre fernando fabio leonardo gustavo
guilherme leandro tiago thiago anderson ricardo marcio jorge sebastiao alexandre roberto edson diego vitor
victor sergio claudio geraldo adriano luciano julio renato alex vinicius rogerio samuel ronaldo mario flavio
igor douglas davi david caio arthur artur enzo heitor bernardo miguel benedito joaquim valdir wellington
wagner wilson reginaldo nelson osvaldo milton otavio cesar hugo henrique murilo nicolas otavio emerson
francisca antonia adriana juliana marcia fernanda patricia aline sandra camila amanda bruna jessica leticia
julia luciana vanessa mariana gabriela vera vitoria larissa claudia beatriz luana rita sonia renata eliane
josefa simone natalia cristiane carla debora rosangela jaqueline rosa daniela isabel marlene terezinha
teresinha raimunda andreia fabiana lucia raquel angela roseli sabrina tatiane cleide irene helena alice
laura valentina sophia sofia isabella manuela livia giovanna luiza elisa cecilia clara aparecida conceicao
fatima lourdes benedita sebastiana geralda vania silvia regina eduarda heloisa yasmin emily lara kamila
""".split())
# 1ª palavra que indica instituição, e não pessoa ("em favor da Prefeitura Municipal")
NAO_SAO_NOMES = set("""
prefeitura secretaria camara municipio fundo fundacao consorcio hospital instituto universidade empresa
associacao santa santo estado uniao governo departamento policia corpo tribunal ministerio servico
sistema unidade centro programa rede escola clinica farmacia comissao conselho diretoria
""".split())
MARCA_CPF = "[CPF REMOVIDO]"
MARCA_PF = "[PESSOA FÍSICA]"
MARCA_PROCESSO = "[PROCESSO JUDICIAL]"
MARCA_NOME = "[NOME REMOVIDO]"


def cpf_valido(digitos: str) -> bool:
    if len(digitos) != 11 or not digitos.isdigit() or digitos == digitos[0] * 11:
        return False
    for n in (9, 10):
        soma = sum(int(digitos[i]) * (n + 1 - i) for i in range(n))
        if (soma * 10) % 11 % 10 != int(digitos[n]):
            return False
    return True


@lru_cache(maxsize=None)
def _sem_acento(ch: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", ch) if not unicodedata.combining(c)).lower()


def normalizar_com_mapa(texto: str) -> tuple[str, list[int]]:
    """Versão minúscula, sem acento e com espaços colapsados + mapa para o original."""
    saida: list[str] = []
    mapa: list[int] = []
    espaco_anterior = False
    for i, ch in enumerate(texto):
        if ch.isspace():
            if not espaco_anterior:
                saida.append(" ")
                mapa.append(i)
            espaco_anterior = True
            continue
        espaco_anterior = False
        for b in _sem_acento(ch):
            saida.append(b)
            mapa.append(i)
    return "".join(saida), mapa


def normalizar(texto: str) -> str:
    return normalizar_com_mapa(texto)[0].strip()


RE_TOKEN = re.compile(r"[a-z0-9]+")


def nomes_por_contexto(texto: str) -> list[tuple[int, int]]:
    """Trechos (início, fim) com cara de nome de pessoa logo após uma palavra-chave (paciente, Sra. ...)."""
    trechos: list[tuple[int, int]] = []
    for chave in RE_CHAVE_PESSOA.finditer(texto):
        inicio = chave.end()
        candidato = RE_NOME_TITULO.match(texto, inicio)
        if candidato is None:
            candidato = RE_NOME_MAIUSCULO.match(texto, inicio)
            if candidato and _sem_acento_texto(candidato.group(0).split()[0]) not in PRIMEIROS_NOMES:
                candidato = None
        if candidato and _sem_acento_texto(candidato.group(0).split()[0]) not in NAO_SAO_NOMES:
            if not trechos or candidato.start() >= trechos[-1][1]:
                trechos.append((candidato.start(), candidato.end()))
    return trechos


def _sem_acento_texto(palavra: str) -> str:
    return "".join(_sem_acento(c) for c in palavra)


class Anonimizador:
    """Remove identificação de pessoas físicas. Nomes são buscados por índice de 1ª palavra."""

    def __init__(self, pepper: bytes) -> None:
        self.pepper = pepper
        self.nomes_pf: set[str] = set()
        self._por_primeira: dict[str, list[str]] = defaultdict(list)
        self.contagem: Counter[str] = Counter()

    def chave_pessoa(self, prefixo: str, documento: str) -> str:
        digest = hmac.new(self.pepper, documento.encode(), hashlib.sha256).hexdigest()
        return f"{prefixo}-{digest[:16]}"

    def registrar_nome_pf(self, nome: str | None) -> None:
        if not nome:
            return
        n = normalizar(nome)
        if len(n) >= 8 and " " in n and n not in self.nomes_pf:
            self.nomes_pf.add(n)
            lista = self._por_primeira[n.split(" ", 1)[0]]
            lista.append(n)
            lista.sort(key=len, reverse=True)

    def encontrar_nomes(self, norm: str) -> list[tuple[int, int]]:
        """Trechos (início, fim) do texto normalizado que são nomes de PF registrados."""
        achados: list[tuple[int, int]] = []
        fim_anterior = -1
        for m in RE_TOKEN.finditer(norm):
            ini = m.start()
            if ini < fim_anterior:
                continue
            for nome in self._por_primeira.get(m.group(0), ()):
                fim = ini + len(nome)
                if norm.startswith(nome, ini) and (fim == len(norm) or not norm[fim].isalnum()):
                    achados.append((ini, fim))
                    fim_anterior = fim
                    break
        return achados

    def mascarar_cpfs(self, texto: str | None, so_formatados: bool = False) -> str | None:
        if not texto:
            return texto

        def troca(_m: re.Match[str]) -> str:
            self.contagem["cpfs_mascarados_em_texto"] += 1
            return MARCA_CPF

        texto = RE_CPF_FORMATADO.sub(troca, texto)
        texto = RE_CPF_PARCIAL.sub(troca, texto)
        if so_formatados:
            return texto

        def troca_digitos(m: re.Match[str]) -> str:
            if cpf_valido(m.group(0)):
                self.contagem["cpfs_mascarados_em_texto"] += 1
                return MARCA_CPF
            return m.group(0)

        return RE_ONZE_DIGITOS.sub(troca_digitos, texto)

    def mascarar_nomes(self, texto: str | None) -> str | None:
        if not texto or not self.nomes_pf:
            return texto
        norm, mapa = normalizar_com_mapa(texto)
        trechos = self.encontrar_nomes(norm)
        if not trechos:
            return texto
        partes: list[str] = []
        cursor = 0
        for ini_n, fim_n in trechos:
            ini, fim = mapa[ini_n], mapa[fim_n - 1] + 1
            partes.append(texto[cursor:ini])
            partes.append(MARCA_PF)
            cursor = fim
            self.contagem["nomes_pf_mascarados_em_texto"] += 1
        partes.append(texto[cursor:])
        return "".join(partes)

    def mascarar_processos(self, texto: str | None) -> str | None:
        if not texto:
            return texto

        def troca(_m: re.Match[str]) -> str:
            self.contagem["processos_judiciais_mascarados"] += 1
            return MARCA_PROCESSO

        return RE_PROCESSO_CNJ.sub(troca, texto)

    def mascarar_nomes_por_contexto(self, texto: str | None) -> str | None:
        if not texto:
            return texto
        trechos = nomes_por_contexto(texto)
        if not trechos:
            return texto
        partes, cursor = [], 0
        for ini, fim in trechos:
            partes += [texto[cursor:ini], MARCA_NOME]
            cursor = fim
            self.contagem["nomes_por_contexto_mascarados"] += 1
        partes.append(texto[cursor:])
        return "".join(partes)

    def texto(self, valor: str | None) -> str | None:
        """Texto livre: CPF, processo judicial, nome após palavra-chave e nomes de PF conhecidos."""
        if valor is None:
            return None
        valor = self.mascarar_cpfs(valor.replace("\x00", ""))
        valor = self.mascarar_processos(valor)
        valor = self.mascarar_nomes_por_contexto(valor)
        return self.mascarar_nomes(valor)

    def codigo(self, valor: Any) -> Any:
        """Campos semiestruturados (processo, número): CPF formatado e processo judicial."""
        if not isinstance(valor, str):
            return valor
        return self.mascarar_processos(self.mascarar_cpfs(valor.replace("\x00", ""), so_formatados=True))


RE_MEI = re.compile(r"^\s*\d{2}\.?\d{3}\.?\d{3}\s+\S")


def fornecedor(anon: Anonimizador, tipo: str | None, documento: str | None, nome: str | None) -> dict | None:
    """Converte (tipo, documento, nome) do PNCP numa linha de fornecedor segura."""
    if not documento and not nome:
        return None
    tipo = (tipo or "").strip().upper()
    doc = re.sub(r"\D", "", documento or "")
    if tipo == "PJ" and len(doc) == 14:
        # MEI costuma ter o nome (e às vezes o CPF) do dono na razão social: o CPF sai, o nome fica marcado
        razao = anon.mascarar_cpfs(nome.replace("\x00", "")) if nome else nome
        tinha_cpf = razao != nome
        return {
            "chave": f"PJ-{doc}",
            "tipo_pessoa": "PJ",
            "cnpj": doc,
            "razao_social": razao,
            "possivel_mei": "true" if tinha_cpf or (nome and RE_MEI.match(nome)) else "false",
        }
    # PF, PE (pessoa estrangeira) ou PJ com documento inconsistente: tratamento conservador
    if tipo not in ("PF", "PE"):
        anon.contagem["fornecedores_tipo_inconsistente"] += 1
    tipo_final = "PE" if tipo == "PE" else "PF"
    anon.registrar_nome_pf(nome)
    anon.contagem[f"fornecedores_{tipo_final.lower()}_anonimizados"] += 1
    return {
        "chave": anon.chave_pessoa(tipo_final, doc or normalizar(nome or "")),
        "tipo_pessoa": tipo_final,
        "cnpj": None,
        "razao_social": None,
        "possivel_mei": "false",
    }


# ---------------------------------------------------------------------------
# Montagem dos CSVs
# ---------------------------------------------------------------------------


def fmt(valor: Any) -> str | None:
    if valor is None:
        return None
    if isinstance(valor, bool):
        return "true" if valor else "false"
    if isinstance(valor, float):
        return repr(valor)
    return str(valor)


def obj(registro: dict, campo: str) -> dict:
    valor = registro.get(campo)
    return valor if isinstance(valor, dict) else {}


class Dominios:
    def __init__(self) -> None:
        self.valores: dict[str, dict[Any, Counter]] = defaultdict(lambda: defaultdict(Counter))
        self.descricoes: dict[str, dict[Any, str]] = defaultdict(dict)

    def add(self, dominio: str, codigo: Any, nome: Any, descricao: Any = None) -> Any:
        if codigo is None or codigo == "":
            return None
        if nome:
            self.valores[dominio][codigo][str(nome)] += 1
        else:
            self.valores[dominio].setdefault(codigo, Counter())
        if descricao:
            self.descricoes[dominio][codigo] = str(descricao)
        return codigo

    def linhas(self, dominio: str) -> list[dict]:
        saida = []
        for codigo in sorted(self.valores[dominio], key=lambda c: (str(type(c)), c)):
            nomes = self.valores[dominio][codigo]
            nome = nomes.most_common(1)[0][0] if nomes else None
            linha = {"codigo": codigo, "nome": nome}
            if dominio == "amparo_legal":
                linha["descricao"] = self.descricoes[dominio].get(codigo)
            saida.append(linha)
        return saida


COLUNAS = {
    "orgao": ["cnpj", "razao_social", "esfera_id", "poder_id"],
    "unidade": ["cnpj_orgao", "codigo_unidade", "nome_unidade", "uf_sigla", "uf_nome", "municipio_nome", "codigo_ibge"],
    "contratacao": [
        "numero_controle_pncp", "cnpj_orgao", "codigo_unidade", "ano_compra", "sequencial_compra",
        "numero_compra", "processo", "modalidade_id", "modo_disputa_id", "situacao_compra_id",
        "instrumento_convocatorio_id", "amparo_legal_codigo", "srp", "objeto_compra",
        "informacao_complementar", "valor_total_estimado", "valor_total_homologado",
        "data_publicacao_pncp", "data_abertura_proposta", "data_encerramento_proposta",
        "data_inclusao", "data_atualizacao", "data_atualizacao_global", "link_sistema_origem",
        "link_processo_eletronico", "justificativa_presencial", "usuario_nome",
    ],
    "contratacao_item": [
        "numero_controle_pncp", "numero_item", "descricao", "material_ou_servico", "quantidade",
        "unidade_medida", "valor_unitario_estimado", "valor_total", "orcamento_sigiloso",
        "criterio_julgamento_id", "situacao_item_id", "tipo_beneficio_id", "categoria_item_id",
        "tem_resultado", "ncm_nbs_codigo", "ncm_nbs_descricao", "catalogo_codigo_item",
        "informacao_complementar", "data_inclusao", "data_atualizacao",
    ],
    "fornecedor": ["chave", "tipo_pessoa", "cnpj", "razao_social", "possivel_mei"],
    "contrato": [
        "numero_controle_pncp", "numero_controle_pncp_compra", "numero_controle_pncp_ata",
        "cnpj_orgao", "codigo_unidade", "ano_contrato", "sequencial_contrato",
        "numero_contrato_empenho", "processo", "tipo_contrato_id", "categoria_processo_id",
        "receita", "objeto_contrato", "informacao_complementar", "fornecedor_chave",
        "subcontratado_chave", "valor_inicial", "valor_parcela", "numero_parcelas",
        "valor_global", "valor_acumulado", "data_assinatura", "data_vigencia_inicio",
        "data_vigencia_fim", "data_publicacao_pncp", "data_atualizacao",
        "data_atualizacao_global", "numero_retificacao", "usuario_nome",
    ],
}

DOMINIOS = [
    "modalidade", "modo_disputa", "situacao_compra", "instrumento_convocatorio", "amparo_legal",
    "criterio_julgamento", "situacao_item", "tipo_beneficio", "categoria_item",
    "tipo_contrato", "categoria_processo",
]


def montar_tabelas(contratacoes, itens_por_compra, contratos, anon: Anonimizador, uf: str) -> tuple[dict, dict]:
    dom = Dominios()
    orgaos: dict[str, dict] = {}
    unidades: dict[tuple, dict] = {}
    fornecedores: dict[str, dict] = {}
    qualidade: Counter[str] = Counter()

    def reg_orgao(o: dict) -> str | None:
        cnpj = o.get("cnpj")
        if cnpj:
            orgaos[cnpj] = {
                "cnpj": cnpj,
                "razao_social": o.get("razaoSocial"),
                "esfera_id": o.get("esferaId"),
                "poder_id": o.get("poderId"),
            }
        return cnpj

    def reg_unidade(cnpj: str | None, u: dict) -> str | None:
        codigo = u.get("codigoUnidade")
        if cnpj and codigo:
            unidades[(cnpj, codigo)] = {
                "cnpj_orgao": cnpj,
                "codigo_unidade": codigo,
                "nome_unidade": u.get("nomeUnidade"),
                "uf_sigla": u.get("ufSigla"),
                "uf_nome": u.get("ufNome"),
                "municipio_nome": u.get("municipioNome"),
                "codigo_ibge": u.get("codigoIbge"),
            }
        return codigo

    # Contratos primeiro: registram os nomes de PF que precisam sumir de todos os textos
    linhas_contrato = []
    for r in sorted(contratos, key=lambda x: x["numeroControlePNCP"]):
        forn = fornecedor(anon, r.get("tipoPessoa"), r.get("niFornecedor"), r.get("nomeRazaoSocialFornecedor"))
        sub = fornecedor(
            anon, r.get("tipoPessoaSubContratada"), r.get("niFornecedorSubContratado"), r.get("nomeFornecedorSubContratado")
        )
        for f in (forn, sub):
            if f:
                fornecedores[f["chave"]] = f
        if forn is None:
            qualidade["contratos_sem_fornecedor"] += 1
        linhas_contrato.append((r, forn, sub))

    contratacao_rows = []
    divergencias_uf = 0
    for r in sorted(contratacoes, key=lambda x: x["numeroControlePNCP"]):
        u = obj(r, "unidadeOrgao")
        if u.get("ufSigla") != uf:
            divergencias_uf += 1
            continue
        cnpj = reg_orgao(obj(r, "orgaoEntidade"))
        codigo_unidade = reg_unidade(cnpj, u)
        amparo = obj(r, "amparoLegal")
        contratacao_rows.append({
            "numero_controle_pncp": r.get("numeroControlePNCP"),
            "cnpj_orgao": cnpj,
            "codigo_unidade": codigo_unidade,
            "ano_compra": r.get("anoCompra"),
            "sequencial_compra": r.get("sequencialCompra"),
            "numero_compra": anon.codigo(r.get("numeroCompra")),
            "processo": anon.codigo(r.get("processo")),
            "modalidade_id": dom.add("modalidade", r.get("modalidadeId"), r.get("modalidadeNome")),
            "modo_disputa_id": dom.add("modo_disputa", r.get("modoDisputaId"), r.get("modoDisputaNome")),
            "situacao_compra_id": dom.add("situacao_compra", r.get("situacaoCompraId"), r.get("situacaoCompraNome")),
            "instrumento_convocatorio_id": dom.add(
                "instrumento_convocatorio", r.get("tipoInstrumentoConvocatorioCodigo"), r.get("tipoInstrumentoConvocatorioNome")
            ),
            "amparo_legal_codigo": dom.add("amparo_legal", amparo.get("codigo"), amparo.get("nome"), amparo.get("descricao")),
            "srp": r.get("srp"),
            "objeto_compra": anon.texto(r.get("objetoCompra")),
            "informacao_complementar": anon.texto(r.get("informacaoComplementar")),
            "valor_total_estimado": r.get("valorTotalEstimado"),
            "valor_total_homologado": r.get("valorTotalHomologado"),
            "data_publicacao_pncp": r.get("dataPublicacaoPncp"),
            "data_abertura_proposta": r.get("dataAberturaProposta"),
            "data_encerramento_proposta": r.get("dataEncerramentoProposta"),
            "data_inclusao": r.get("dataInclusao"),
            "data_atualizacao": r.get("dataAtualizacao"),
            "data_atualizacao_global": r.get("dataAtualizacaoGlobal"),
            "link_sistema_origem": r.get("linkSistemaOrigem"),
            "link_processo_eletronico": r.get("linkProcessoEletronico"),
            "justificativa_presencial": anon.texto(r.get("justificativaPresencial")),
            "usuario_nome": r.get("usuarioNome"),
        })
    qualidade["contratacoes_fora_da_uf_descartadas"] = divergencias_uf

    item_rows = []
    numeros = {c["numero_controle_pncp"] for c in contratacao_rows}
    for numero in sorted(numeros):
        lista = itens_por_compra.get(numero)
        if lista is None:
            qualidade["contratacoes_sem_consulta_de_itens"] += 1
            continue
        if not lista:
            qualidade["contratacoes_com_zero_itens"] += 1
        vistos_itens: set[int] = set()
        for it in sorted(lista, key=lambda x: x.get("numeroItem") or 0):
            n = it.get("numeroItem")
            if n in vistos_itens:
                qualidade["itens_duplicados_descartados"] += 1
                continue
            vistos_itens.add(n)
            item_rows.append({
                "numero_controle_pncp": numero,
                "numero_item": n,
                "descricao": anon.texto(it.get("descricao")),
                "material_ou_servico": it.get("materialOuServico"),
                "quantidade": it.get("quantidade"),
                "unidade_medida": it.get("unidadeMedida"),
                "valor_unitario_estimado": it.get("valorUnitarioEstimado"),
                "valor_total": it.get("valorTotal"),
                "orcamento_sigiloso": it.get("orcamentoSigiloso"),
                "criterio_julgamento_id": dom.add("criterio_julgamento", it.get("criterioJulgamentoId"), it.get("criterioJulgamentoNome")),
                "situacao_item_id": dom.add("situacao_item", it.get("situacaoCompraItem"), it.get("situacaoCompraItemNome")),
                "tipo_beneficio_id": dom.add("tipo_beneficio", it.get("tipoBeneficio"), it.get("tipoBeneficioNome")),
                "categoria_item_id": dom.add("categoria_item", it.get("itemCategoriaId"), it.get("itemCategoriaNome")),
                "tem_resultado": it.get("temResultado"),
                "ncm_nbs_codigo": it.get("ncmNbsCodigo"),
                "ncm_nbs_descricao": it.get("ncmNbsDescricao"),
                "catalogo_codigo_item": it.get("catalogoCodigoItem"),
                "informacao_complementar": anon.texto(it.get("informacaoComplementar")),
                "data_inclusao": it.get("dataInclusao"),
                "data_atualizacao": it.get("dataAtualizacao"),
            })

    contrato_rows = []
    for r, forn, sub in linhas_contrato:
        cnpj = reg_orgao(obj(r, "orgaoEntidade"))
        codigo_unidade = reg_unidade(cnpj, obj(r, "unidadeOrgao"))
        tipo = obj(r, "tipoContrato")
        categoria = obj(r, "categoriaProcesso")
        contrato_rows.append({
            "numero_controle_pncp": r.get("numeroControlePNCP"),
            "numero_controle_pncp_compra": r.get("numeroControlePncpCompra"),
            "numero_controle_pncp_ata": r.get("numeroControlePncpAta"),
            "cnpj_orgao": cnpj,
            "codigo_unidade": codigo_unidade,
            "ano_contrato": r.get("anoContrato"),
            "sequencial_contrato": r.get("sequencialContrato"),
            "numero_contrato_empenho": anon.codigo(r.get("numeroContratoEmpenho")),
            "processo": anon.codigo(r.get("processo")),
            "tipo_contrato_id": dom.add("tipo_contrato", tipo.get("id"), tipo.get("nome")),
            "categoria_processo_id": dom.add("categoria_processo", categoria.get("id"), categoria.get("nome")),
            "receita": r.get("receita"),
            "objeto_contrato": anon.texto(r.get("objetoContrato")),
            "informacao_complementar": anon.texto(r.get("informacaoComplementar")),
            "fornecedor_chave": forn["chave"] if forn else None,
            "subcontratado_chave": sub["chave"] if sub else None,
            "valor_inicial": r.get("valorInicial"),
            "valor_parcela": r.get("valorParcela"),
            "numero_parcelas": r.get("numeroParcelas"),
            "valor_global": r.get("valorGlobal"),
            "valor_acumulado": r.get("valorAcumulado"),
            "data_assinatura": r.get("dataAssinatura"),
            "data_vigencia_inicio": r.get("dataVigenciaInicio"),
            "data_vigencia_fim": r.get("dataVigenciaFim"),
            "data_publicacao_pncp": r.get("dataPublicacaoPncp"),
            "data_atualizacao": r.get("dataAtualizacao"),
            "data_atualizacao_global": r.get("dataAtualizacaoGlobal"),
            "numero_retificacao": r.get("numeroRetificacao"),
            "usuario_nome": r.get("usuarioNome"),
        })

    tabelas = {
        "orgao": sorted(orgaos.values(), key=lambda x: x["cnpj"]),
        "unidade": sorted(unidades.values(), key=lambda x: (x["cnpj_orgao"], x["codigo_unidade"])),
        "contratacao": contratacao_rows,
        "contratacao_item": item_rows,
        "fornecedor": sorted(fornecedores.values(), key=lambda x: x["chave"]),
        "contrato": contrato_rows,
    }
    for d in DOMINIOS:
        tabelas[f"dominio_{d}"] = dom.linhas(d)
    return tabelas, dict(qualidade)


CAMPOS_TEXTO_LIVRE = {
    "objeto_compra", "informacao_complementar", "justificativa_presencial", "descricao", "objeto_contrato",
}
CAMPOS_IDENTIFICADORES = {
    "chave", "fornecedor_chave", "subcontratado_chave", "cnpj", "cnpj_orgao", "numero_controle_pncp",
    "numero_controle_pncp_compra", "numero_controle_pncp_ata", "link_sistema_origem", "link_processo_eletronico",
}


def validar_lgpd(tabelas: dict[str, list[dict]], anon: Anonimizador) -> list[str]:
    """Varredura final: nenhum CPF, nenhum nome de PF conhecido e PF/PE sem identificação."""
    problemas: list[str] = []
    for nome, linhas in tabelas.items():
        for linha in linhas:
            for campo, valor in linha.items():
                if not isinstance(valor, str) or not valor or campo in CAMPOS_IDENTIFICADORES:
                    continue
                if RE_CPF_FORMATADO.search(valor) or RE_CPF_PARCIAL.search(valor):
                    problemas.append(f"{nome}.{campo}: CPF formatado")
                if RE_PROCESSO_CNJ.search(valor):
                    problemas.append(f"{nome}.{campo}: número de processo judicial")
                if campo in CAMPOS_TEXTO_LIVRE:
                    if any(cpf_valido(m.group(0)) for m in RE_ONZE_DIGITOS.finditer(valor)):
                        problemas.append(f"{nome}.{campo}: 11 dígitos com DV de CPF")
                    if nomes_por_contexto(valor):
                        problemas.append(f"{nome}.{campo}: nome após palavra-chave de pessoa")
                if anon.nomes_pf and anon.encontrar_nomes(normalizar(valor)):
                    problemas.append(f"{nome}.{campo}: nome de pessoa física")
    for f in tabelas["fornecedor"]:
        if f["tipo_pessoa"] != "PJ" and (f["cnpj"] or f["razao_social"]):
            problemas.append(f"fornecedor {f['chave']}: PF/PE com identificação")
    return problemas


def contratos_do_cache(cache: Path, uf: str) -> list[dict]:
    vistos: dict[str, dict] = {}
    for arquivo in sorted((cache / "contratos" / uf).glob("*/p*.json")):
        for reg in json.loads(arquivo.read_text(encoding="utf-8"))["data"]:
            chave = reg.get("numeroControlePNCP")
            anterior = vistos.get(chave)
            if anterior is None or (reg.get("dataAtualizacao") or "") >= (anterior.get("dataAtualizacao") or ""):
                vistos[chave] = reg
    return list(vistos.values())


LIMITE_CARACTERES_POR_ARQUIVO = 40_000_000  # ~40 MB: abaixo do aviso de 50 MB do GitHub


def escrever_csvs(tabelas: dict[str, list[dict]], saida: Path) -> dict[str, dict]:
    """Grava um CSV por tabela; tabelas grandes viram partes (nome_parte1.csv, nome_parte2.csv...)."""
    saida.mkdir(parents=True, exist_ok=True)
    for antigo in saida.glob("*.csv"):
        antigo.unlink()
    manifesto: dict[str, dict] = {}
    for nome, linhas in tabelas.items():
        colunas = COLUNAS.get(nome) or (
            ["codigo", "nome", "descricao"] if nome == "dominio_amparo_legal" else ["codigo", "nome"]
        )
        partes: list[tuple[str, int]] = []
        buffer, n = io.StringIO(), 0

        def nova_parte(colunas: list[str] = colunas) -> tuple[io.StringIO, Any]:
            b = io.StringIO()
            w = csv.writer(b, lineterminator="\n")
            w.writerow(colunas)
            return b, w

        buffer, escritor = nova_parte()
        for linha in linhas:
            escritor.writerow([fmt(linha.get(c)) for c in colunas])
            n += 1
            if buffer.tell() >= LIMITE_CARACTERES_POR_ARQUIVO:
                partes.append((buffer.getvalue(), n))
                buffer, escritor = nova_parte()
                n = 0
        if n or not partes:
            partes.append((buffer.getvalue(), n))

        arquivos = []
        for i, (conteudo_texto, linhas_parte) in enumerate(partes, start=1):
            nome_arquivo = f"{nome}.csv" if len(partes) == 1 else f"{nome}_parte{i}.csv"
            conteudo = conteudo_texto.encode("utf-8")
            (saida / nome_arquivo).write_bytes(conteudo)
            arquivos.append({
                "arquivo": nome_arquivo,
                "linhas": linhas_parte,
                "bytes": len(conteudo),
                "sha256": hashlib.sha256(conteudo).hexdigest(),
            })
        manifesto[nome] = {"linhas": len(linhas), "colunas": colunas, "arquivos": arquivos}
    return manifesto


# ---------------------------------------------------------------------------
# Programa principal
# ---------------------------------------------------------------------------


def carregar_pepper(cache: Path) -> bytes:
    if os.environ.get("SNAPSHOT_PEPPER"):
        return os.environ["SNAPSHOT_PEPPER"].encode()
    arquivo = cache / ".pepper"
    if not arquivo.exists():
        cache.mkdir(parents=True, exist_ok=True)
        arquivo.write_text(secrets.token_hex(32), encoding="utf-8")
    return arquivo.read_text(encoding="utf-8").strip().encode()


def main(argv: Iterable[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--uf", default="MG")
    ap.add_argument("--referencia", default=date.today().isoformat(), help="data de referência (AAAA-MM-DD)")
    ap.add_argument("--dias-proposta", type=int, default=365, help="teto da data de encerramento das propostas")
    ap.add_argument("--dias-contratos", type=int, default=30, help="janela de publicação dos contratos")
    ap.add_argument("--saida", type=Path, required=True)
    ap.add_argument("--cache", type=Path, required=True)
    ap.add_argument("--intervalo", type=float, default=0.8, help="segundos mínimos entre requisições")
    ap.add_argument("--etapas", default="contratacoes,itens,contratos,csv")
    ap.add_argument("--limite-itens", type=int, default=0, help="só para teste: buscar itens de N contratações")
    ap.add_argument("--itens-do-fim", action="store_true", help="percorre as contratações de trás para frente")
    args = ap.parse_args(list(argv) if argv is not None else None)

    referencia = date.fromisoformat(args.referencia)
    data_final = (referencia + timedelta(days=args.dias_proposta)).strftime("%Y%m%d")
    fim_contratos = referencia - timedelta(days=1)
    inicio_contratos = referencia - timedelta(days=args.dias_contratos)
    etapas = set(args.etapas.split(","))
    args.cache.mkdir(parents=True, exist_ok=True)
    arquivo_log = (args.cache / "snapshot.log").open("a", encoding="utf-8")

    def log(msg: str) -> None:
        linha = f"[{datetime.now():%H:%M:%S}] {msg}"
        print(linha, flush=True)
        arquivo_log.write(linha + "\n")
        arquivo_log.flush()

    inicio = datetime.now().astimezone()
    log(f"snapshot PNCP uf={args.uf} referencia={referencia} etapas={sorted(etapas)}")
    cli = ClientePncp(args.intervalo, log)

    contratacoes = etapa_contratacoes(cli, args.cache, args.uf, data_final, log)
    itens: dict[str, list[dict]] = {}
    falhas_itens: list[dict] = []
    if "itens" in etapas or "csv" in etapas:
        if "itens" in etapas:
            itens, falhas_itens = etapa_itens(
                cli, args.cache, contratacoes, log, args.limite_itens, inversa=args.itens_do_fim
            )
        else:
            for c in contratacoes:
                p = args.cache / "itens" / f"{c['orgaoEntidade']['cnpj']}_{c['anoCompra']}_{c['sequencialCompra']}.json"
                if p.exists():
                    itens[c["numeroControlePNCP"]] = json.loads(p.read_text(encoding="utf-8"))
    contratos: list[dict] = []
    resumo_contratos: dict = {}
    if "contratos" in etapas:
        contratos, resumo_contratos = etapa_contratos(cli, args.cache, args.uf, inicio_contratos, fim_contratos, log)
    elif "csv" in etapas:
        contratos = contratos_do_cache(args.cache, args.uf)
        resumo_contratos = {"observacao": "montado a partir do cache, possivelmente parcial"}
    log(f"requisições: {dict(cli.stats)}")

    if "csv" not in etapas:
        return 0

    anon = Anonimizador(carregar_pepper(args.cache))
    tabelas, qualidade = montar_tabelas(contratacoes, itens, contratos, anon, args.uf)
    problemas = validar_lgpd(tabelas, anon)
    if problemas:
        log(f"LGPD: {len(problemas)} problemas encontrados; NADA foi gravado. Exemplos: {problemas[:10]}")
        return 2
    arquivos = escrever_csvs(tabelas, args.saida)
    manifesto = {
        "gerado_em": datetime.now().astimezone().isoformat(timespec="seconds"),
        "iniciado_em": inicio.isoformat(timespec="seconds"),
        "fonte": "API pública do PNCP (https://pncp.gov.br/api/consulta/v3/api-docs)",
        "parametros": {
            "uf": args.uf,
            "referencia": referencia.isoformat(),
            "contratacoes": {"endpoint": "/v1/contratacoes/proposta", "dataFinal": data_final, "uf": args.uf},
            "itens": {"endpoint": "/api/pncp/v1/orgaos/{cnpj}/compras/{ano}/{sequencial}/itens", "tamanhoPagina": 500},
            "contratos": {
                "endpoint": "/v1/contratos",
                "dataInicial": inicio_contratos.isoformat(),
                "dataFinal": fim_contratos.isoformat(),
                "filtro_uf": "no cliente, por unidadeOrgao.ufSigla",
                **resumo_contratos,
            },
        },
        "requisicoes": dict(cli.stats),
        "qualidade": {**qualidade, "falhas_ao_buscar_itens": len(falhas_itens)},
        "lgpd": {
            **dict(anon.contagem),
            "nomes_pf_distintos_mascarados": len(anon.nomes_pf),
            "metodo": "PF/PE sem documento e sem nome; chave = HMAC-SHA256 com pepper secreto não versionado",
        },
        "tabelas": arquivos,
    }
    (args.saida.parent / "MANIFESTO.json").write_text(
        json.dumps(manifesto, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    log("CSV gerados: " + ", ".join(f"{k}={v['linhas']}" for k, v in arquivos.items()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
