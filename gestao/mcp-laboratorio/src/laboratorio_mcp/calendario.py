"""Calendário do laboratório a partir do roadmap.yml."""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path
from typing import Any

import yaml


def carregar_roadmap(diretorio_lab: Path) -> dict[str, Any]:
    return yaml.safe_load((diretorio_lab / "roadmap.yml").read_text(encoding="utf-8"))


def semana_em(roadmap: dict[str, Any], dia: date) -> dict[str, Any] | None:
    """Sprint (ou recesso) que contém `dia`. O fim de semana conta para a sprint que acabou de terminar."""
    for semana in roadmap["semanas"]:
        if semana["inicio"] <= dia <= semana["fim"] + timedelta(days=2):
            return semana
    return None


def sprint_por_numero(roadmap: dict[str, Any], numero: int) -> dict[str, Any]:
    for semana in roadmap["semanas"]:
        if semana.get("sprint") == numero:
            return semana
    raise ValueError(f"Sprint {numero} não está no roadmap.yml")


def dias_uteis(inicio: date, fim: date) -> list[date]:
    return [
        inicio + timedelta(days=i)
        for i in range((fim - inicio).days + 1)
        if (inicio + timedelta(days=i)).weekday() < 5
    ]


def titulo_milestone(numero: int) -> str:
    return f"Sprint {numero:02d}"


def resumo_sprint_atual(roadmap: dict[str, Any], hoje: date) -> dict[str, Any]:
    lab = roadmap["laboratorio"]
    if hoje < lab["inicio"]:
        return {
            "situacao": "antes do início",
            "inicio": lab["inicio"].isoformat(),
            "dias_para_comecar": (lab["inicio"] - hoje).days,
        }
    if hoje > lab["fim"]:
        return {"situacao": "laboratório encerrado", "fim": lab["fim"].isoformat()}
    semana = semana_em(roadmap, hoje)
    if semana is None:
        return {"situacao": "fora de sprint", "hoje": hoje.isoformat()}
    if semana.get("recesso"):
        return {
            "situacao": "recesso",
            "inicio": semana["inicio"].isoformat(),
            "fim": semana["fim"].isoformat(),
        }
    fases = {f["id"]: f for f in roadmap["fases"]}
    fase = fases.get(semana["fase"], {})
    restantes = [d for d in dias_uteis(hoje, semana["fim"])]
    return {
        "situacao": "em sprint",
        "sprint": semana["sprint"],
        "milestone": titulo_milestone(semana["sprint"]),
        "inicio": semana["inicio"].isoformat(),
        "fim": semana["fim"].isoformat(),
        "objetivo": semana["objetivo"],
        "fase": f"{fase.get('id')} — {fase.get('nome')} (assistência {fase.get('assistencia')})",
        "temas": semana.get("temas", []),
        "observacoes": semana.get("observacoes"),
        "dias_uteis_restantes": len(restantes),
    }
