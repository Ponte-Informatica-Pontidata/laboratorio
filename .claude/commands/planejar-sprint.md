---
description: Planeja a próxima sprint (issues + TODOs e testes no Radar) a partir do roadmap
argument-hint: <numero-da-sprint>
---
Planeje a sprint $ARGUMENTS.

1. Leia:
   - `roadmap.yml` (objetivo, temas, observações e fase);
   - `ROADMAP.md` ("Como a assistência diminui");
   - a avaliação e a retro da sprint anterior;
   - o `status_sprint` da sprint anterior (o que ficou aberto volta para o planejamento).
2. Proponha de 3 a 4 issues (cerca de 10 h no total, P/M; G só a partir da fase 3), mais 1 desafio opcional.
   A maioria deve ser de dados, com alguma de desenvolvimento assistido por IA, documentação e, quando couber, `sem-ia`.
3. Para cada issue, escreva `sprints/sprint-NN/issues/SNN-XX-*.md` no formato de `sprints/README.md`.
   Inclua contexto, passos, critérios de aceite, conteúdo da faculdade, arquivos/TODOs, estimativa, prazo,
   labels e uma dica que não entrega a resposta. Use `{{numero}}` para a própria issue e `{{SNN-XX}}` para referências.
4. Escreva `sprints/sprint-NN/README.md` (objetivo em 1 frase, tabela, DoD da sprint e rituais).
5. No `radar-licitacoes`, prepare numa branch `chore/planejar-sprint-NN`:
   - os stubs com `TODO(estagiaria): #SNN-XX`;
   - os testes com `@todo_estagiaria(issue="SNN-XX")` que falham do jeito esperado.

   Garanta que o CI fica verde (os testes viram XFAIL).
6. Mostre o plano. Depois do OK:
   - `publicar_sprint(numero, executar=false)` → revisar → `executar=true`;
   - troque os placeholders `SNN-XX` pelos números reais das issues;
   - abra o PR de preparação.
