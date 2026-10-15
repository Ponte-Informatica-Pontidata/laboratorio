---
id: S0-05
repositorio: radar-licitacoes
titulo: "[docs] Primeiro PR: completar o dicionário de contratacao_item"
labels: [docs, dados]
estimativa: P
prazo: 2026-10-30
sprint: 0
---
## Contexto

O dicionário de dados é o contrato entre quem produz e quem consome os dados. Em `dados/DICIONARIO.md`,
a tabela `contratacao_item` está com as descrições faltando (`TODO(estagiaria)`). O teste
`test_dicionario_de_contratacao_item_completo` espera por você.

Este é o seu **primeiro Pull Request**: o conteúdo é pequeno de propósito, para você praticar o fluxo
inteiro (branch → commit → PR → revisão → merge).

## O que fazer

1. Atualize a `main` e crie a branch `docs/{{numero}}-dicionario-itens`.
2. Para cada coluna de `contratacao_item` marcada com TODO, descubra o significado:
   - olhe os dados (`select ... from radar.contratacao_item`);
   - olhe as tabelas `dominio_*`;
   - olhe a documentação da API do PNCP.
3. Escreva descrições curtas e úteis: o que é, unidade, valores possíveis e pegadinhas.
4. Apague o `@todo_estagiaria` do teste e rode `docker compose run --rm dev pytest`.
5. Faça o commit (`docs: completa o dicionário de contratacao_item`), dê push e abra o PR com o template
   completo e `Closes #{{numero}}`.
6. Responda os comentários da revisão com commits novos na mesma branch.

## Critérios de aceite

- [ ] Nenhuma coluna de `contratacao_item` com TODO no dicionário.
- [ ] `@todo_estagiaria` removido e o teste passando.
- [ ] PR com título em Conventional Commits (`docs: ...`), template preenchido e `Closes #`.
- [ ] CI verde.
- [ ] Pelo menos uma **pegadinha** que você descobriu olhando os dados está documentada.

## Conteúdo da faculdade praticado

Governança de dados, metadados, documentação técnica e controle de versão (Git e Pull Request).

## Arquivos e TODOs relacionados

- `dados/DICIONARIO.md` — `TODO(estagiaria): #{{numero}}`
- `tests/unit/test_dicionario.py` — `@todo_estagiaria(issue={{numero}})`

## Dica de por onde começar

Compare `valor_unitario_estimado * quantidade` com `valor_total` em algumas linhas: o resultado bate
sempre? E o que acontece com essas colunas quando `orcamento_sigiloso` é `true`?
