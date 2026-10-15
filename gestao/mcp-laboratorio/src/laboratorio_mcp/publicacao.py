"""Publicação idempotente das issues de uma sprint (e da issue fixa da daily) no GitHub.

Idempotência: cada issue leva o marcador oculto `<!-- lab-id: S0-01 -->`. Antes de criar, todas as issues
dos repositórios do laboratório são lidas; o que já tem marcador não é criado de novo.

Placeholders no corpo:
  {{numero}}  -> número da própria issue (preenchido logo depois de criar)
  {{S0-03}}   -> referência à issue S0-03 (org/repo#N), se ela já existir
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from laboratorio_mcp.calendario import carregar_roadmap, sprint_por_numero, titulo_milestone
from laboratorio_mcp.config import Config
from laboratorio_mcp.github import GitHub
from laboratorio_mcp.sprints import IssuePlanejada, ler_issues_da_sprint

RE_MARCADOR = re.compile(r"<!-- lab-id: ([A-Za-z0-9-]+) -->")
RE_REFERENCIA = re.compile(r"\{\{(S\d+-\d+|DAILY)\}\}")
TITULO_DAILY = "📅 Daily assíncrona"


def carregar_labels(diretorio_lab: Path) -> list[dict[str, str]]:
    return json.loads((diretorio_lab / "scripts" / "labels.json").read_text(encoding="utf-8"))


def mapa_existentes(gh: GitHub, repos: tuple[str, ...] | list[str]) -> dict[str, tuple[str, int]]:
    """{lab-id: (repositório, número)} de todas as issues que já têm marcador."""
    mapa: dict[str, tuple[str, int]] = {}
    for repo in repos:
        for issue in gh.issues(repo, state="all"):
            achado = RE_MARCADOR.search(issue.get("body") or "")
            if achado:
                mapa[achado.group(1)] = (repo, issue["number"])
    return mapa


def rodape(issue: IssuePlanejada) -> str:
    return (
        f"\n---\n**Estimativa:** {issue.estimativa} · **Prazo:** {issue.prazo:%d/%m/%Y} · "
        f"**Sprint:** {issue.sprint:02d}\n\n<!-- lab-id: {issue.id} -->\n"
    )


def resolver_referencias(texto: str, mapa: dict[str, tuple[str, int]], org: str) -> str:
    def trocar(m: re.Match[str]) -> str:
        alvo = mapa.get(m.group(1))
        return f"{org}/{alvo[0]}#{alvo[1]}" if alvo else m.group(1)

    return RE_REFERENCIA.sub(trocar, texto)


@dataclass
class Plano:
    sprint: int
    milestone: str
    prazo: date
    objetivo: str
    issues: list[IssuePlanejada]
    existentes: dict[str, tuple[str, int]]
    labels_faltando: dict[str, list[str]]
    milestones_faltando: list[str]

    @property
    def repos(self) -> list[str]:
        return sorted({i.repositorio for i in self.issues})

    def resumo(self) -> dict[str, Any]:
        return {
            "sprint": self.sprint,
            "milestone": self.milestone,
            "prazo_milestone": self.prazo.isoformat(),
            "objetivo": self.objetivo,
            "milestones_a_criar": self.milestones_faltando,
            "labels_a_criar": self.labels_faltando,
            "issues": [
                {
                    "id": i.id,
                    "repositorio": i.repositorio,
                    "titulo": i.titulo,
                    "labels": list(i.labels),
                    "estimativa": i.estimativa,
                    "prazo": i.prazo.isoformat(),
                    "acao": "já existe" if i.id in self.existentes else "criar",
                    "numero": self.existentes[i.id][1] if i.id in self.existentes else None,
                }
                for i in self.issues
            ],
        }


def planejar(gh: GitHub, cfg: Config, numero: int) -> Plano:
    semana = sprint_por_numero(carregar_roadmap(cfg.diretorio_lab), numero)
    issues = ler_issues_da_sprint(cfg.diretorio_lab, numero)
    nomes_labels = {label["nome"] for label in carregar_labels(cfg.diretorio_lab)}
    repos = sorted({i.repositorio for i in issues})
    titulo = titulo_milestone(numero)

    labels_faltando: dict[str, list[str]] = {}
    milestones_faltando: list[str] = []
    for repo in repos:
        existentes = {label["name"] for label in gh.labels(repo)}
        usadas = {label for i in issues if i.repositorio == repo for label in i.labels}
        faltam = sorted((usadas | nomes_labels) - existentes)
        if faltam:
            labels_faltando[repo] = faltam
        if not any(m["title"] == titulo for m in gh.milestones(repo)):
            milestones_faltando.append(repo)

    mapa = mapa_existentes(gh, cfg.repos)
    return Plano(
        sprint=numero,
        milestone=titulo,
        prazo=semana["fim"],
        objetivo=semana["objetivo"],
        issues=issues,
        existentes={i.id: mapa[i.id] for i in issues if i.id in mapa},
        labels_faltando=labels_faltando,
        milestones_faltando=milestones_faltando,
    )


def executar(gh: GitHub, cfg: Config, plano: Plano) -> list[dict[str, Any]]:
    definicoes = {label["nome"]: label for label in carregar_labels(cfg.diretorio_lab)}
    for repo, faltam in plano.labels_faltando.items():
        for nome in faltam:
            definicao = definicoes.get(nome, {"cor": "ededed", "descricao": ""})
            gh.criar_label(repo, nome, definicao["cor"], definicao["descricao"])

    numeros_milestone: dict[str, int] = {}
    for repo in plano.repos:
        milestone = next((m for m in gh.milestones(repo) if m["title"] == plano.milestone), None)
        if milestone is None:
            milestone = gh.criar_milestone(
                repo, plano.milestone, plano.objetivo, f"{plano.prazo.isoformat()}T12:00:00Z"
            )
        numeros_milestone[repo] = milestone["number"]

    mapa = mapa_existentes(gh, cfg.repos)
    resultados: list[dict[str, Any]] = []
    for issue in plano.issues:
        if issue.id in mapa:
            repo, numero = mapa[issue.id]
            resultados.append({"id": issue.id, "repositorio": repo, "numero": numero, "status": "já existia"})
            continue
        corpo = resolver_referencias(issue.corpo, mapa, cfg.org) + rodape(issue)
        criada = gh.criar_issue(
            issue.repositorio, issue.titulo, corpo, list(issue.labels), numeros_milestone[issue.repositorio]
        )
        numero = criada["number"]
        if "{{numero}}" in corpo:
            gh.editar_issue(issue.repositorio, numero, body=corpo.replace("{{numero}}", str(numero)))
        mapa[issue.id] = (issue.repositorio, numero)
        resultados.append(
            {
                "id": issue.id,
                "repositorio": issue.repositorio,
                "numero": numero,
                "url": criada.get("html_url"),
                "status": "criada",
            }
        )
    return resultados


def garantir_daily(gh: GitHub, cfg: Config, executar_agora: bool) -> dict[str, Any]:
    """Cria (e fixa) a issue da daily assíncrona no repositório laboratorio, se ainda não existir."""
    mapa = mapa_existentes(gh, ["laboratorio"])
    if "DAILY" in mapa:
        return {"status": "já existia", "numero": mapa["DAILY"][1]}
    if not executar_agora:
        return {"status": "seria criada", "titulo": TITULO_DAILY}
    corpo = (cfg.diretorio_lab / "templates" / "daily-issue.md").read_text(encoding="utf-8")
    criada = gh.criar_issue("laboratorio", TITULO_DAILY, corpo + "\n<!-- lab-id: DAILY -->\n", [], None)
    gh.fixar_issue(criada["node_id"])
    return {"status": "criada e fixada", "numero": criada["number"], "url": criada.get("html_url")}
