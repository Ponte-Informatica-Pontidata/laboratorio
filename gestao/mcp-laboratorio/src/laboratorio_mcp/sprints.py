"""Leitura das issues planejadas em sprints/sprint-NN/issues/*.md (front-matter YAML + corpo)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path

import yaml


@dataclass(frozen=True)
class IssuePlanejada:
    id: str
    repositorio: str
    titulo: str
    labels: tuple[str, ...]
    estimativa: str
    prazo: date
    sprint: int
    corpo: str
    arquivo: str


def separar_front_matter(texto: str) -> tuple[dict, str]:
    if not texto.startswith("---"):
        raise ValueError("arquivo de issue sem front-matter (bloco --- no início)")
    _, cabecalho, corpo = texto.split("---", 2)
    return yaml.safe_load(cabecalho) or {}, corpo.strip() + "\n"


def ler_issue(caminho: Path) -> IssuePlanejada:
    meta, corpo = separar_front_matter(caminho.read_text(encoding="utf-8"))
    faltando = {"id", "repositorio", "titulo", "labels", "estimativa", "prazo", "sprint"} - meta.keys()
    if faltando:
        raise ValueError(f"{caminho.name}: faltam campos no front-matter: {sorted(faltando)}")
    if meta["estimativa"] not in ("P", "M", "G"):
        raise ValueError(f"{caminho.name}: estimativa deve ser P, M ou G")
    return IssuePlanejada(
        id=str(meta["id"]),
        repositorio=str(meta["repositorio"]),
        titulo=str(meta["titulo"]),
        labels=tuple(meta["labels"]),
        estimativa=meta["estimativa"],
        prazo=meta["prazo"],
        sprint=int(meta["sprint"]),
        corpo=corpo,
        arquivo=caminho.name,
    )


def ler_issues_da_sprint(diretorio_lab: Path, numero: int) -> list[IssuePlanejada]:
    pasta = diretorio_lab / "sprints" / f"sprint-{numero:02d}" / "issues"
    if not pasta.exists():
        raise FileNotFoundError(f"Pasta {pasta} não existe: a sprint {numero} ainda não foi planejada")
    issues = [ler_issue(p) for p in sorted(pasta.glob("*.md"))]
    ids = [i.id for i in issues]
    if len(ids) != len(set(ids)):
        raise ValueError(f"ids repetidos na sprint {numero}: {ids}")
    return issues
