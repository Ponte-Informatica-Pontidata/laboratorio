"""Leituras do GitHub que o "cérebro" usa para acompanhar o laboratório."""

from __future__ import annotations

import re
from collections import Counter
from datetime import date, datetime, timedelta
from typing import Any

from laboratorio_mcp.calendario import carregar_roadmap, dias_uteis, sprint_por_numero, titulo_milestone
from laboratorio_mcp.config import Config
from laboratorio_mcp.github import ErroGitHub, GitHub
from laboratorio_mcp.publicacao import mapa_existentes

RE_PRAZO = re.compile(r"\*\*Prazo:\*\* (\d{2})/(\d{2})/(\d{4})")
RE_CONVENTIONAL = re.compile(
    r"^(feat|fix|docs|test|refactor|perf|build|ci|chore|style|revert)(\([\w-]+\))?!?: \S"
)
RE_FECHA_ISSUE = re.compile(r"(?i)\b(closes|fixes|resolves)\s+#\d+")
RE_COMENTARIO_HTML = re.compile(r"<!--.*?-->", re.DOTALL)


def _data_local(iso: str) -> date:
    """Data em Brasília (UTC-3) de um timestamp ISO do GitHub."""
    return (datetime.fromisoformat(iso.replace("Z", "+00:00")) - timedelta(hours=3)).date()


def prazo_da_issue(issue: dict) -> date | None:
    achado = RE_PRAZO.search(issue.get("body") or "")
    if not achado:
        return None
    dia, mes, ano = (int(x) for x in achado.groups())
    return date(ano, mes, dia)


def numero_milestone(gh: GitHub, repo: str, titulo: str) -> int | None:
    return next((m["number"] for m in gh.milestones(repo) if m["title"] == titulo), None)


def status_sprint(gh: GitHub, cfg: Config, numero: int, hoje: date) -> dict[str, Any]:
    titulo = titulo_milestone(numero)
    aviso = None
    quadro: dict[tuple[str, int], str] = {}
    if cfg.projeto_numero:
        try:
            quadro = gh.status_no_quadro(cfg.projeto_numero)
        except ErroGitHub as exc:
            aviso = f"Não li o quadro (Projects): {exc}"
    linhas = []
    for repo in cfg.repos:
        milestone = numero_milestone(gh, repo, titulo)
        if milestone is None:
            continue
        for issue in gh.issues(repo, milestone=milestone, state="all"):
            prazo = prazo_da_issue(issue)
            aberta = issue["state"] == "open"
            linhas.append(
                {
                    "repositorio": repo,
                    "numero": issue["number"],
                    "titulo": issue["title"],
                    "estado": issue["state"],
                    "status_quadro": quadro.get((repo, issue["number"])),
                    "labels": [label["name"] for label in issue.get("labels", [])],
                    "responsaveis": [a["login"] for a in issue.get("assignees", [])],
                    "prazo": prazo.isoformat() if prazo else None,
                    "atrasada": bool(aberta and prazo and prazo < hoje),
                    "url": issue.get("html_url"),
                }
            )
    return {
        "sprint": numero,
        "milestone": titulo,
        "resumo": {
            "total": len(linhas),
            "fechadas": sum(1 for x in linhas if x["estado"] == "closed"),
            "abertas": sum(1 for x in linhas if x["estado"] == "open"),
            "atrasadas": [f"{x['repositorio']}#{x['numero']}" for x in linhas if x["atrasada"]],
            "bloqueadas": [
                f"{x['repositorio']}#{x['numero']}" for x in linhas if x["status_quadro"] == "Bloqueado"
            ],
        },
        "issues": linhas,
        "aviso": aviso,
    }


def _quem_e_a_estagiaria(cfg: Config, comentarios: list[dict]) -> str | None:
    if cfg.estagiaria:
        return cfg.estagiaria
    autores = Counter(
        c["user"]["login"]
        for c in comentarios
        if c["user"]["login"] != cfg.tech_lead and not c["user"]["login"].endswith("[bot]")
    )
    return autores.most_common(1)[0][0] if autores else None


def dailies(gh: GitHub, cfg: Config, dias: int, hoje: date) -> dict[str, Any]:
    mapa = mapa_existentes(gh, ["laboratorio"])
    if "DAILY" not in mapa:
        return {"erro": "Issue da daily não encontrada (marcador lab-id: DAILY). Rode garantir_daily."}
    numero = mapa["DAILY"][1]
    desde = hoje - timedelta(days=dias)
    comentarios = gh.comentarios("laboratorio", numero, desde=f"{desde.isoformat()}T00:00:00Z")
    estagiaria = _quem_e_a_estagiaria(cfg, comentarios)
    dela = [c for c in comentarios if c["user"]["login"] == estagiaria]
    dias_com_daily = {_data_local(c["created_at"]) for c in dela}
    esperados = [d for d in dias_uteis(desde, hoje - timedelta(days=1))]
    bloqueios = []
    for c in dela:
        for linha in (c.get("body") or "").splitlines():
            if "bloqueio" in linha.lower() and "nenhum" not in linha.lower():
                bloqueios.append(
                    {"data": _data_local(c["created_at"]).isoformat(), "texto": linha.strip()[:300]}
                )
    return {
        "issue": numero,
        "estagiaria": estagiaria,
        "periodo": {"de": desde.isoformat(), "ate": hoje.isoformat()},
        "dias_uteis_sem_daily": [d.isoformat() for d in esperados if d not in dias_com_daily],
        "bloqueios_relatados": bloqueios,
        "dailies": [
            {
                "autor": c["user"]["login"],
                "data": _data_local(c["created_at"]).isoformat(),
                "texto": (c.get("body") or "")[:1500],
            }
            for c in comentarios
        ],
    }


def secao_preenchida(corpo: str, titulo: str) -> bool:
    """A seção `titulo` do template de PR tem conteúdo de verdade (além de comentários e rótulos)?"""
    if titulo not in corpo:
        return False
    trecho = corpo.split(titulo, 1)[1].split("\n## ", 1)[0]
    trecho = RE_COMENTARIO_HTML.sub("", trecho)
    uteis = []
    for linha in trecho.splitlines():
        texto = linha.strip().lstrip("-*0123456789.[] x").strip()
        if not texto or texto.endswith(":"):
            continue
        uteis.append(texto)
    return len(" ".join(uteis)) >= 20


def prs_em_revisao(gh: GitHub, cfg: Config, hoje: date) -> dict[str, Any]:
    itens = []
    for repo in cfg.repos:
        for pr in gh.pulls(repo, "open"):
            corpo = pr.get("body") or ""
            checks = gh.checks(repo, pr["head"]["sha"])
            revisoes = gh.revisoes(repo, pr["number"])
            itens.append(
                {
                    "repositorio": repo,
                    "numero": pr["number"],
                    "titulo": pr["title"],
                    "autor": pr["user"]["login"],
                    "rascunho": pr.get("draft", False),
                    "dias_aberto": (hoje - _data_local(pr["created_at"])).days,
                    "url": pr.get("html_url"),
                    "titulo_conventional_commits": bool(RE_CONVENTIONAL.match(pr["title"])),
                    "fecha_issue": bool(RE_FECHA_ISSUE.search(corpo)),
                    "secao_uso_de_ia_preenchida": secao_preenchida(corpo, "## Uso de IA"),
                    "secao_explicacao_preenchida": secao_preenchida(corpo, "## Explique com suas palavras"),
                    "checks": dict(Counter((c.get("conclusion") or c.get("status") or "?") for c in checks)),
                    "ultima_revisao": revisoes[-1]["state"] if revisoes else None,
                    "rodadas_de_ajuste": sum(1 for r in revisoes if r["state"] == "CHANGES_REQUESTED"),
                }
            )
    return {"total": len(itens), "prs": itens}


def metricas_sprint(gh: GitHub, cfg: Config, numero: int) -> dict[str, Any]:
    semana = sprint_por_numero(carregar_roadmap(cfg.diretorio_lab), numero)
    inicio, fim = semana["inicio"], semana["fim"] + timedelta(days=2)
    titulo = titulo_milestone(numero)
    no_prazo = atrasadas = abertas = 0
    lead_times: list[float] = []
    prs_mergeados = 0
    rodadas: list[int] = []
    for repo in cfg.repos:
        milestone = numero_milestone(gh, repo, titulo)
        if milestone is not None:
            for issue in gh.issues(repo, milestone=milestone, state="all"):
                prazo = prazo_da_issue(issue)
                if issue["state"] != "closed":
                    abertas += 1
                    continue
                fechada = _data_local(issue["closed_at"])
                if prazo is None or fechada <= prazo:
                    no_prazo += 1
                else:
                    atrasadas += 1
                criada = datetime.fromisoformat(issue["created_at"].replace("Z", "+00:00"))
                fechada_em = datetime.fromisoformat(issue["closed_at"].replace("Z", "+00:00"))
                lead_times.append((fechada_em - criada).total_seconds() / 3600)
        for pr in gh.pulls(repo, "closed"):
            if pr.get("merged_at") and inicio <= _data_local(pr["merged_at"]) <= fim:
                prs_mergeados += 1
                rodadas.append(
                    sum(1 for r in gh.revisoes(repo, pr["number"]) if r["state"] == "CHANGES_REQUESTED")
                )
    fechadas = no_prazo + atrasadas
    return {
        "sprint": numero,
        "issues": {"fechadas_no_prazo": no_prazo, "fechadas_com_atraso": atrasadas, "ainda_abertas": abertas},
        "taxa_no_prazo": round(no_prazo / fechadas, 2) if fechadas else None,
        "lead_time_medio_horas": round(sum(lead_times) / len(lead_times), 1) if lead_times else None,
        "prs_mergeados": prs_mergeados,
        "rodadas_de_ajuste_por_pr": round(sum(rodadas) / len(rodadas), 2) if rodadas else None,
    }
