---
description: Prepara a review da sprint (métricas, demonstração) e a issue de review/retro
argument-hint: <numero-da-sprint>
---
Para a sprint $ARGUMENTS (padrão: a atual, via `sprint_atual`):

1. MCP `laboratorio`: `status_sprint`, `metricas_sprint` e `dailies` (dias=7).
2. MCP `github`: PRs mergeados na semana (títulos e links).
3. Leia `sprints/sprint-NN/README.md`: objetivo e Definition of Done.

Entregue o **rascunho da issue "Review e retro — Sprint NN"** no formato de `templates/review-retro.md`:
- objetivo cumprido? (sim, parcial ou não, com o porquê);
- entregas por issue, com links;
- métricas (no prazo, lead time, rodadas de ajuste, dailies);
- itens da DoD não atendidos;
- 3 perguntas para a demonstração dela (o que mostrar, o que explicar).

A partir da Sprint 7, inclua o link do app publicado. Mostre o rascunho e só crie a issue (milestone da
sprint, label `estudo`) depois do OK.
