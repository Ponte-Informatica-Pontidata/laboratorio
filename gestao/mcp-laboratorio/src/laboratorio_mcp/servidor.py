"""Servidor MCP do laboratório (transporte stdio).

Rodar:  docker compose -f gestao/docker-compose.yml run --rm -T mcp-laboratorio
(o .mcp.json da raiz do repositório laboratorio já faz isso pelo Claude Code)
"""

from __future__ import annotations

from datetime import date
from functools import lru_cache
from typing import Any

from mcp.server import MCPServer

from laboratorio_mcp import analises, publicacao
from laboratorio_mcp.calendario import carregar_roadmap, resumo_sprint_atual, semana_em
from laboratorio_mcp.config import Config
from laboratorio_mcp.github import GitHub
from laboratorio_mcp.rubrica import CRITERIOS, EXPECTATIVA_POR_FASE
from laboratorio_mcp.rubrica import montar_avaliacao as _montar_avaliacao

INSTRUCOES = """Você é o "cérebro" de gestão do Laboratório Pontidata (estágio em Big Data e IA).
O GitHub é a única fonte de verdade: issues, PRs, milestones (sprints), daily e quadro.
- Ferramentas de leitura (sprint_atual, status_sprint, dailies, prs_em_revisao, metricas_sprint, rubrica) podem ser usadas à vontade.
- publicar_sprint e garantir_daily só alteram o GitHub com executar=true: mostre antes a prévia (executar=false)
  ao tech lead e só execute depois da confirmação dele.
- Nunca copie dados pessoais (CPF, nomes de pessoas físicas, dados de saúde) para issues, PRs ou respostas.
- Avalie o trabalho, nunca a pessoa; use as evidências (links) e a rubrica."""

servidor = MCPServer("laboratorio", instructions=INSTRUCOES)


@lru_cache
def _config() -> Config:
    return Config.do_ambiente()


@lru_cache
def _github() -> GitHub:
    cfg = _config()
    return GitHub(cfg.token, cfg.org)


def _hoje() -> date:
    return date.today()


def _sprint_padrao() -> int:
    semana = semana_em(carregar_roadmap(_config().diretorio_lab), _hoje())
    if not semana or "sprint" not in semana:
        raise ValueError("Hoje não há sprint em andamento: informe o número da sprint")
    return semana["sprint"]


@servidor.tool()
def sprint_atual() -> dict[str, Any]:
    """Sprint em andamento hoje segundo o roadmap.yml: datas, objetivo, fase, temas e dias úteis restantes."""
    return resumo_sprint_atual(carregar_roadmap(_config().diretorio_lab), _hoje())


@servidor.tool()
def status_sprint(numero: int | None = None) -> dict[str, Any]:
    """Issues da sprint (padrão: a atual) em todos os repositórios: estado, prazo, atrasos e bloqueios no quadro."""
    return analises.status_sprint(
        _github(), _config(), numero if numero is not None else _sprint_padrao(), _hoje()
    )


@servidor.tool()
def dailies(dias: int = 7) -> dict[str, Any]:
    """Comentários da issue de daily dos últimos `dias` dias, dias úteis sem daily e bloqueios relatados."""
    return analises.dailies(_github(), _config(), dias, _hoje())


@servidor.tool()
def prs_em_revisao() -> dict[str, Any]:
    """PRs abertos com checagens do processo: título, Closes #, seções de IA e explicação, CI e revisões."""
    return analises.prs_em_revisao(_github(), _config(), _hoje())


@servidor.tool()
def metricas_sprint(numero: int) -> dict[str, Any]:
    """Métricas de uma sprint: issues no prazo, lead time, PRs mergeados e rodadas de ajuste por PR."""
    return analises.metricas_sprint(_github(), _config(), numero)


@servidor.tool()
def publicar_sprint(numero: int, executar: bool = False) -> dict[str, Any]:
    """Publica as issues de sprints/sprint-NN/issues no GitHub (idempotente).

    Com executar=false (padrão) só devolve o plano. Só use executar=true depois que o tech lead aprovar o plano.
    """
    plano = publicacao.planejar(_github(), _config(), numero)
    resposta: dict[str, Any] = {"plano": plano.resumo()}
    if executar:
        resposta["resultado"] = publicacao.executar(_github(), _config(), plano)
    return resposta


@servidor.tool()
def garantir_daily(executar: bool = False) -> dict[str, Any]:
    """Garante a issue fixa "Daily assíncrona" no repositório laboratorio (cria e fixa se faltar)."""
    return publicacao.garantir_daily(_github(), _config(), executar)


@servidor.tool()
def rubrica() -> dict[str, Any]:
    """Critérios da rubrica (1 a 5) e a expectativa por fase do laboratório."""
    return {"criterios": CRITERIOS, "expectativa_por_fase": EXPECTATIVA_POR_FASE, "documento": "RUBRICA.md"}


@servidor.tool()
def montar_avaliacao(
    sprint: int,
    notas: dict[str, int],
    evidencias: dict[str, str],
    destaques: str,
    combinado: str,
    fase: int | None = None,
) -> str:
    """Valida as notas (1 a 5 nos 7 critérios) e devolve o markdown para avaliacoes/sprint-NN.md."""
    return _montar_avaliacao(sprint, notas, evidencias, destaques, combinado, fase)


def main() -> None:
    servidor.run("stdio")


if __name__ == "__main__":
    main()
