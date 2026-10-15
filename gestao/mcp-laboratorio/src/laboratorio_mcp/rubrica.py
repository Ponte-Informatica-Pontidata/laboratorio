"""Rubrica de avaliação (espelha RUBRICA.md) e montagem do registro da sprint."""

from __future__ import annotations

CRITERIOS: dict[str, str] = {
    "qualidade_tecnica": "Qualidade técnica",
    "prazo": "Prazo",
    "qualidade_dados": "Qualidade dos dados",
    "documentacao": "Documentação",
    "uso_ia": "Uso consciente de IA",
    "comunicacao": "Comunicação",
    "autonomia": "Autonomia",
}

EXPECTATIVA_POR_FASE: dict[int, str] = {
    1: "maioria em 2–3: aprender o fluxo importa mais que velocidade",
    2: "maioria em 3",
    3: "3, com algum 4 em dados ou IA",
    4: "3–4, autonomia em 4",
    5: "consolidação: a média final considera a evolução",
}


def montar_avaliacao(
    sprint: int,
    notas: dict[str, int],
    evidencias: dict[str, str],
    destaques: str,
    combinado: str,
    fase: int | None = None,
) -> str:
    """Valida as notas (1 a 5 nos 7 critérios) e devolve o markdown de avaliacoes/sprint-NN.md."""
    faltando = set(CRITERIOS) - set(notas)
    sobrando = set(notas) - set(CRITERIOS)
    if faltando or sobrando:
        raise ValueError(f"critérios faltando {sorted(faltando)} / desconhecidos {sorted(sobrando)}")
    for chave, nota in notas.items():
        if not isinstance(nota, int) or not 1 <= nota <= 5:
            raise ValueError(f"nota de {chave} deve ser inteiro de 1 a 5 (recebi {nota!r})")
    media = sum(notas.values()) / len(notas)
    linhas = [
        f"# Avaliação — Sprint {sprint:02d}",
        "",
        f"Média: **{media:.1f}**"
        + (f" · Expectativa da fase {fase}: {EXPECTATIVA_POR_FASE[fase]}" if fase else ""),
        "",
        "| Critério | Nota | Evidências |",
        "|---|---|---|",
    ]
    for chave, nome in CRITERIOS.items():
        linhas.append(f"| {nome} | {notas[chave]} | {evidencias.get(chave, '').strip() or '—'} |")
    linhas += [
        "",
        "## Destaques",
        "",
        destaques.strip(),
        "",
        "## Combinado para a próxima sprint",
        "",
        combinado.strip(),
        "",
    ]
    linhas += [
        "",
        "## Comentário da estagiária",
        "",
        "_(espaço para ela concordar, discordar ou trazer contexto)_",
        "",
    ]
    return "\n".join(linhas)
