---
description: Rascunho da avaliação da sprint pela rubrica (1 a 5), com evidências
argument-hint: <numero-da-sprint>
---
Avalie a sprint $ARGUMENTS:

1. MCP `laboratorio`:
   - `rubrica`;
   - `sprint_atual` (para saber a fase);
   - `status_sprint`, `metricas_sprint` e `dailies` (dias=7).
2. MCP `github`: PRs da sprint (descrição, revisões, respostas aos comentários) e a issue de review/retro.
3. Leia `RUBRICA.md` (descritores de cada nível) e a avaliação anterior em `avaliacoes/`, se existir.

Para cada um dos 7 critérios, proponha uma nota de 1 a 5 com **evidência linkada**. Respeite a expectativa
da fase: nota 3 significa "esperado para a fase", não "médio".

Gere o markdown com `montar_avaliacao`. Mostre ao tech lead para revisão e, só depois do OK, salve em
`avaliacoes/sprint-NN.md` e proponha o commit (`docs: avaliação da sprint NN`), sem assinatura do Claude.
