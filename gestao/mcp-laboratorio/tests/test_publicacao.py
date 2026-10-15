from __future__ import annotations

from laboratorio_mcp import publicacao


def test_planejar_sem_nada_no_github_cria_tudo(gh, cfg):
    plano = publicacao.planejar(gh, cfg, 0)
    resumo = plano.resumo()
    assert resumo["milestone"] == "Sprint 00"
    assert sorted(resumo["milestones_a_criar"]) == ["laboratorio", "radar-licitacoes"]
    assert all(i["acao"] == "criar" for i in resumo["issues"])
    assert "sem-ia" in resumo["labels_a_criar"]["radar-licitacoes"]


def test_executar_cria_issues_com_marcador_e_resolve_placeholders(gh, cfg):
    resultados = publicacao.executar(gh, cfg, publicacao.planejar(gh, cfg, 0))
    assert [r["status"] for r in resultados] == ["criada"] * 6
    numeros = {r["id"]: (r["repositorio"], r["numero"]) for r in resultados}

    dicionario = next(i for i in gh.issues("radar-licitacoes") if "dicionário" in i["title"])
    assert "<!-- lab-id: S0-05 -->" in dicionario["body"]
    assert "{{numero}}" not in dicionario["body"]
    assert f"Closes #{numeros['S0-05'][1]}" in dicionario["body"]
    assert "**Prazo:** 30/10/2026" in dicionario["body"]

    desafio = next(i for i in gh.issues("radar-licitacoes") if i["title"].startswith("[desafio]"))
    repo, numero = numeros["S0-03"]
    assert f"Org/{repo}#{numero}" in desafio["body"]  # {{S0-03}} virou referência
    assert {label["name"] for label in gh.labels("radar-licitacoes")} >= {"dados", "sem-ia", "desafio"}


def test_publicar_duas_vezes_nao_duplica(gh, cfg):
    publicacao.executar(gh, cfg, publicacao.planejar(gh, cfg, 0))
    segundo = publicacao.planejar(gh, cfg, 0)
    assert all(i["acao"] == "já existe" for i in segundo.resumo()["issues"])
    resultados = publicacao.executar(gh, cfg, segundo)
    assert {r["status"] for r in resultados} == {"já existia"}
    assert len(gh.issues("radar-licitacoes")) + len(gh.issues("laboratorio")) == 6


def test_daily_e_criada_uma_vez_e_fixada(gh, cfg):
    assert publicacao.garantir_daily(gh, cfg, executar_agora=False)["status"] == "seria criada"
    criada = publicacao.garantir_daily(gh, cfg, executar_agora=True)
    assert criada["status"] == "criada e fixada"
    assert gh.fixadas == [f"I_laboratorio_{criada['numero']}"]
    assert publicacao.garantir_daily(gh, cfg, executar_agora=True)["status"] == "já existia"
