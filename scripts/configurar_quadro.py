"""Cria e configura o quadro do laboratório no GitHub Projects.

Pré-requisito (uma vez):  gh auth refresh -s project
Uso:                      python scripts/configurar_quadro.py      (precisa de PyYAML: uv run --with pyyaml ...)

O que faz (pode rodar de novo sem duplicar nada):
  1. cria o projeto "Laboratório Pontidata — Quadro" na organização (ou reaproveita o existente);
  2. troca as colunas do campo Status por: Backlog → Em desenvolvimento → Em revisão → Bloqueado → Pronto;
  3. cria os campos Estimativa (P/M/G), Prazo (data) e Sprint (iterações semanais do roadmap.yml);
  4. liga os repositórios laboratorio e radar-licitacoes ao projeto;
  5. adiciona as issues do laboratório (marcador lab-id) com Status, Estimativa, Prazo e Sprint.

O que NÃO dá para fazer pela API (faça na interface do projeto, em "Workflows"):
  - "Auto-add to project" para os dois repositórios;
  - "Item closed" e "Pull request merged" → Pronto (confira se apontam para "Pronto").
"""

from __future__ import annotations

import json
import re
import subprocess
from datetime import date
from pathlib import Path

import yaml

ORG = "Ponte-Informatica-Pontidata"
TITULO = "Laboratório Pontidata — Quadro"
REPOS = ["laboratorio", "radar-licitacoes"]
# (nome, cor, descrição, nome da opção padrão do GitHub que esta substitui)
STATUS = [
    ("Backlog", "GRAY", "Planejado, ainda não começou", "Todo"),
    ("Em desenvolvimento", "BLUE", "Ela está trabalhando (máximo 1 por vez)", "In Progress"),
    ("Em revisão", "PURPLE", "PR aberto, esperando revisão", None),
    ("Bloqueado", "RED", "Travado há mais de 1 hora: ver daily", None),
    ("Pronto", "GREEN", "PR mergeado e critérios de aceite marcados", "Done"),
]
RE_MARCADOR = re.compile(r"<!-- lab-id: (S\d+-\d+) -->")
RE_RODAPE = re.compile(r"\*\*Estimativa:\*\* ([PMG]) · \*\*Prazo:\*\* (\d{2})/(\d{2})/(\d{4}) · \*\*Sprint:\*\* (\d+)")


class Enum(str):
    """Valor de enum GraphQL (vai sem aspas)."""


def literal(valor: object) -> str:
    """Converte dict/list/str/int/Enum em literal GraphQL (chaves sem aspas, enums sem aspas)."""
    if isinstance(valor, Enum):
        return str(valor)
    if isinstance(valor, dict):
        return "{" + ", ".join(f"{k}: {literal(v)}" for k, v in valor.items()) + "}"
    if isinstance(valor, list):
        return "[" + ", ".join(literal(v) for v in valor) + "]"
    return json.dumps(valor, ensure_ascii=False)


def gh(*args: str, entrada: str | None = None) -> str:
    return subprocess.run(
        ["gh", *args], check=True, capture_output=True, text=True, encoding="utf-8", input=entrada
    ).stdout


def graphql(consulta: str) -> dict:
    resposta = json.loads(gh("api", "graphql", "--input", "-", entrada=json.dumps({"query": consulta})))
    if resposta.get("errors"):
        raise RuntimeError(resposta["errors"])
    return resposta["data"]


def projeto() -> tuple[int, str]:
    existentes = json.loads(gh("project", "list", "--owner", ORG, "--format", "json", "--limit", "100"))
    for p in existentes.get("projects", []):
        if p["title"] == TITULO:
            return p["number"], p["id"]
    novo = json.loads(gh("project", "create", "--owner", ORG, "--title", TITULO, "--format", "json"))
    return novo["number"], novo["id"]


def campos(numero: int) -> dict[str, dict]:
    dados = json.loads(gh("project", "field-list", str(numero), "--owner", ORG, "--format", "json", "--limit", "100"))
    return {c["name"]: c for c in dados["fields"]}


def configurar_status(campo: dict) -> None:
    atuais = {o["name"]: o["id"] for o in campo.get("options", [])}

    def opcoes(com_id: bool) -> list[dict]:
        lista = []
        for nome, cor, descricao, antigo in STATUS:
            opcao: dict = {"name": nome, "color": Enum(cor), "description": descricao}
            existente = atuais.get(nome) or (atuais.get(antigo) if antigo else None)
            if com_id and existente:
                opcao["id"] = existente
            lista.append(opcao)
        return lista

    for com_id in (True, False):  # manter os ids preserva os workflows; se a API recusar, recria as opções
        try:
            graphql(
                f"""mutation {{ updateProjectV2Field(input: {{fieldId: {literal(campo["id"])},
                    singleSelectOptions: {literal(opcoes(com_id))}}}) {{ projectV2Field {{ __typename }} }} }}"""
            )
            return
        except (RuntimeError, subprocess.CalledProcessError):
            if not com_id:
                raise


def criar_campos(numero: int, id_projeto: str, roadmap: dict) -> None:
    existentes = campos(numero)
    if "Estimativa" not in existentes:
        gh("project", "field-create", str(numero), "--owner", ORG, "--name", "Estimativa",
           "--data-type", "SINGLE_SELECT", "--single-select-options", "P,M,G")
    if "Prazo" not in existentes:
        gh("project", "field-create", str(numero), "--owner", ORG, "--name", "Prazo", "--data-type", "DATE")
    if "Sprint" not in existentes:
        iteracoes = [
            {"startDate": s["inicio"].isoformat(), "duration": (s["fim"] - s["inicio"]).days + 3,
             "title": f"Sprint {s['sprint']:02d}"}
            for s in roadmap["semanas"] if "sprint" in s
        ]
        configuracao = {"startDate": roadmap["laboratorio"]["inicio"].isoformat(), "duration": 7, "iterations": iteracoes}
        graphql(
            f"""mutation {{ createProjectV2Field(input: {{projectId: {literal(id_projeto)}, dataType: ITERATION,
                name: "Sprint", iterationConfiguration: {literal(configuracao)}}}) {{ projectV2Field {{ __typename }} }} }}"""
        )


def iteracoes_do_campo(id_campo: str) -> dict[str, str]:
    dados = graphql(
        f"""query {{ node(id: {literal(id_campo)}) {{ ... on ProjectV2IterationField {{
              configuration {{ iterations {{ id title }} completedIterations {{ id title }} }} }} }} }}"""
    )
    configuracao = dados["node"]["configuration"]
    return {i["title"]: i["id"] for i in configuracao["iterations"] + configuracao["completedIterations"]}


def adicionar_issues(numero: int, id_projeto: str) -> int:
    todos = campos(numero)
    backlog = next(o["id"] for o in todos["Status"]["options"] if o["name"] == "Backlog")
    estimativas = {o["name"]: o["id"] for o in todos["Estimativa"]["options"]}
    sprints = iteracoes_do_campo(todos["Sprint"]["id"])
    adicionadas = 0
    for repo in REPOS:
        issues = json.loads(gh("issue", "list", "-R", f"{ORG}/{repo}", "--state", "all", "--limit", "500",
                               "--json", "url,body"))
        for issue in issues:
            corpo = issue.get("body") or ""
            if not RE_MARCADOR.search(corpo):
                continue
            item = json.loads(gh("project", "item-add", str(numero), "--owner", ORG, "--url", issue["url"],
                                 "--format", "json"))["id"]
            base = ["project", "item-edit", "--id", item, "--project-id", id_projeto]
            gh(*base, "--field-id", todos["Status"]["id"], "--single-select-option-id", backlog)
            rodape = RE_RODAPE.search(corpo)
            if rodape:
                estimativa, dia, mes, ano, sprint = rodape.groups()
                gh(*base, "--field-id", todos["Estimativa"]["id"], "--single-select-option-id", estimativas[estimativa])
                gh(*base, "--field-id", todos["Prazo"]["id"], "--date", date(int(ano), int(mes), int(dia)).isoformat())
                titulo = f"Sprint {int(sprint):02d}"
                if titulo in sprints:
                    gh(*base, "--field-id", todos["Sprint"]["id"], "--iteration-id", sprints[titulo])
            adicionadas += 1
    return adicionadas


def main() -> None:
    roadmap = yaml.safe_load((Path(__file__).resolve().parents[1] / "roadmap.yml").read_text(encoding="utf-8"))
    numero, id_projeto = projeto()
    print(f"Projeto #{numero}: {TITULO}")
    configurar_status(campos(numero)["Status"])
    print("Status: Backlog → Em desenvolvimento → Em revisão → Bloqueado → Pronto")
    criar_campos(numero, id_projeto, roadmap)
    print("Campos: Estimativa, Prazo e Sprint")
    for repo in REPOS:
        gh("project", "link", str(numero), "--owner", ORG, "--repo", f"{ORG}/{repo}")
    print(f"Issues no quadro: {adicionar_issues(numero, id_projeto)}")
    print(f"\nColoque LAB_PROJETO_NUMERO={numero} em gestao/.env.")
    print("Na interface do projeto (Workflows): Auto-add (2 repositórios), Item closed → Pronto, PR merged → Pronto.")


if __name__ == "__main__":
    main()
