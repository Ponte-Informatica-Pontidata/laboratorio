"""Configuração lida do ambiente (gestao/.env no Docker)."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Config:
    token: str
    org: str = "Ponte-Informatica-Pontidata"
    repos: tuple[str, ...] = ("laboratorio", "radar-licitacoes")
    diretorio_lab: Path = Path("/lab")
    tech_lead: str = "pedro-canedo"
    estagiaria: str | None = None
    projeto_numero: int | None = None

    @classmethod
    def do_ambiente(cls) -> Config:
        token = os.environ.get("GITHUB_PERSONAL_ACCESS_TOKEN") or os.environ.get("GH_TOKEN") or ""
        repos = tuple(
            r.strip() for r in os.environ.get("LAB_REPOS", "laboratorio,radar-licitacoes").split(",")
        )
        projeto = os.environ.get("LAB_PROJETO_NUMERO")
        return cls(
            token=token,
            org=os.environ.get("LAB_ORG", "Ponte-Informatica-Pontidata"),
            repos=tuple(r for r in repos if r),
            diretorio_lab=Path(os.environ.get("LAB_DIR", "/lab")),
            tech_lead=os.environ.get("LAB_TECH_LEAD", "pedro-canedo"),
            estagiaria=os.environ.get("LAB_ESTAGIARIA") or None,
            projeto_numero=int(projeto) if projeto else None,
        )
