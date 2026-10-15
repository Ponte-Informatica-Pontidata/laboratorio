from __future__ import annotations

from datetime import date

from laboratorio_mcp import analises, publicacao
from laboratorio_mcp.rubrica import montar_avaliacao


def test_status_sprint_aponta_atraso(gh, cfg):
    publicacao.executar(gh, cfg, publicacao.planejar(gh, cfg, 0))
    status = analises.status_sprint(gh, cfg, 0, hoje=date(2026, 10, 29))
    assert status["resumo"]["total"] == 6
    atrasadas = status["resumo"]["atrasadas"]
    assert len(atrasadas) == 2  # S0-01 (27/10) e S0-02 (28/10) seguem abertas
    assert all(a.startswith(("laboratorio#", "radar-licitacoes#")) for a in atrasadas)


def test_dailies_aponta_dia_util_sem_daily(gh, cfg):
    numero = publicacao.garantir_daily(gh, cfg, executar_agora=True)["numero"]
    gh._comentarios[("laboratorio", numero)] = [
        {
            "user": {"login": "estagiaria"},
            "created_at": "2026-10-26T13:00:00Z",
            "body": "**Fiz:** setup\n**Bloqueios:** nenhum",
        },
        {
            "user": {"login": "estagiaria"},
            "created_at": "2026-10-28T13:00:00Z",
            "body": "**Bloqueios:** Docker não sobe no Windows",
        },
        {"user": {"login": "techlead"}, "created_at": "2026-10-28T15:00:00Z", "body": "Vamos olhar juntos"},
    ]
    resultado = analises.dailies(gh, cfg, dias=4, hoje=date(2026, 10, 29))
    assert resultado["estagiaria"] == "estagiaria"
    assert resultado["dias_uteis_sem_daily"] == ["2026-10-27"]
    assert resultado["bloqueios_relatados"][0]["texto"].endswith("Docker não sobe no Windows")


def test_prs_em_revisao_checa_o_template(gh, cfg):
    gh._pulls["radar-licitacoes"] = [
        {
            "number": 9,
            "title": "feat: normaliza textos",
            "state": "open",
            "draft": False,
            "user": {"login": "estagiaria"},
            "created_at": "2026-11-03T12:00:00Z",
            "head": {"sha": "abc"},
            "body": "## O que mudou\nCloses #7\n\n## Explique com suas palavras\nA função troca qualquer espaço repetido por um só e remove controles.\n\n## Uso de IA\n- Ferramenta(s):\n- Principais prompts (cole os 2 ou 3 mais importantes):\n  1.\n",
        },
        {
            "number": 10,
            "title": "Ajustes",
            "state": "open",
            "draft": True,
            "user": {"login": "estagiaria"},
            "created_at": "2026-11-04T12:00:00Z",
            "head": {"sha": "def"},
            "body": "",
        },
    ]
    gh._checks["abc"] = [{"conclusion": "success"}, {"conclusion": "success"}]
    gh._revisoes[("radar-licitacoes", 9)] = [{"state": "CHANGES_REQUESTED"}, {"state": "APPROVED"}]
    prs = {p["numero"]: p for p in analises.prs_em_revisao(gh, cfg, hoje=date(2026, 11, 5))["prs"]}
    assert prs[9]["titulo_conventional_commits"] and prs[9]["fecha_issue"]
    assert prs[9]["secao_explicacao_preenchida"] is True
    assert prs[9]["secao_uso_de_ia_preenchida"] is False  # só os rótulos do template
    assert prs[9]["checks"] == {"success": 2}
    assert prs[9]["rodadas_de_ajuste"] == 1
    assert not prs[10]["titulo_conventional_commits"] and not prs[10]["fecha_issue"]


def test_avaliacao_valida_notas():
    notas = dict.fromkeys(
        [
            "qualidade_tecnica",
            "prazo",
            "qualidade_dados",
            "documentacao",
            "uso_ia",
            "comunicacao",
            "autonomia",
        ],
        3,
    )
    texto = montar_avaliacao(
        0, notas, {"prazo": "todas no prazo"}, "Banco carregado", "Daily antes das 10h", fase=1
    )
    assert "Média: **3.0**" in texto and "| Prazo | 3 | todas no prazo |" in texto
    notas["prazo"] = 6
    try:
        montar_avaliacao(0, notas, {}, "", "")
    except ValueError as exc:
        assert "1 a 5" in str(exc)
    else:
        raise AssertionError("nota 6 deveria ser recusada")
