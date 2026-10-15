"""O servidor MCP responde pelo protocolo (cliente em memória do SDK)."""

from __future__ import annotations

from datetime import date

import anyio
import pytest
from mcp import Client

from laboratorio_mcp import servidor as modulo


@pytest.fixture(autouse=True)
def configuracao_de_teste(monkeypatch, cfg):
    monkeypatch.setattr(modulo, "_config", lambda: cfg)
    monkeypatch.setattr(modulo, "_hoje", lambda: date(2026, 11, 4))


def test_lista_as_ferramentas_e_chama_sprint_atual():
    async def cenario():
        async with Client(modulo.servidor) as cliente:
            ferramentas = {f.name for f in (await cliente.list_tools()).tools}
            resultado = await cliente.call_tool("sprint_atual", {})
            return ferramentas, resultado

    ferramentas, resultado = anyio.run(cenario)
    assert {
        "sprint_atual",
        "status_sprint",
        "dailies",
        "prs_em_revisao",
        "metricas_sprint",
        "publicar_sprint",
        "garantir_daily",
        "rubrica",
        "montar_avaliacao",
    } <= ferramentas
    dados = resultado.structured_content
    assert dados["sprint"] == 1
    assert dados["milestone"] == "Sprint 01"
