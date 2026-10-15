"""Valida os arquivos reais de planejamento (roadmap.yml e sprints/) do repositório laboratorio."""

from __future__ import annotations

import itertools
from datetime import date, timedelta

import pytest

from laboratorio_mcp.calendario import carregar_roadmap, resumo_sprint_atual, semana_em, sprint_por_numero
from laboratorio_mcp.sprints import ler_issues_da_sprint

from .conftest import RAIZ_LAB


def test_roadmap_tem_24_semanas_e_22_sprints():
    roadmap = carregar_roadmap(RAIZ_LAB)
    semanas = roadmap["semanas"]
    sprints = [s for s in semanas if "sprint" in s]
    assert [s["sprint"] for s in sprints] == list(range(22))
    duracao = roadmap["laboratorio"]["fim"] - roadmap["laboratorio"]["inicio"]
    assert duracao.days + 3 == 24 * 7  # de segunda a sexta da 24ª semana
    for anterior, atual in itertools.pairwise(semanas):
        assert atual["inicio"] > anterior["fim"], "semanas sobrepostas no roadmap"


@pytest.mark.parametrize("numero, quantidade", [(0, 6), (1, 4)])
def test_issues_planejadas_validas(numero, quantidade):
    roadmap = carregar_roadmap(RAIZ_LAB)
    semana = sprint_por_numero(roadmap, numero)
    issues = ler_issues_da_sprint(RAIZ_LAB, numero)
    assert len(issues) == quantidade
    for issue in issues:
        assert issue.sprint == numero
        assert issue.repositorio in roadmap["laboratorio"]["repositorios"]
        assert semana["inicio"] - timedelta(days=1) <= issue.prazo <= semana["fim"], issue.id
        assert issue.titulo.startswith("["), issue.id
        for secao in (
            "## Contexto",
            "## O que fazer",
            "## Critérios de aceite",
            "## Dica de por onde começar",
        ):
            assert secao in issue.corpo, f"{issue.id} sem a seção {secao}"


def test_sprint_atual_por_data():
    roadmap = carregar_roadmap(RAIZ_LAB)
    assert semana_em(roadmap, date(2026, 10, 28))["sprint"] == 0
    assert semana_em(roadmap, date(2026, 11, 1))["sprint"] == 0  # domingo conta para a sprint anterior
    assert semana_em(roadmap, date(2026, 12, 24)).get("recesso") is True
    assert resumo_sprint_atual(roadmap, date(2026, 10, 15))["situacao"] == "antes do início"
    resumo = resumo_sprint_atual(roadmap, date(2026, 11, 4))
    assert resumo["sprint"] == 1
    assert resumo["dias_uteis_restantes"] == 3
