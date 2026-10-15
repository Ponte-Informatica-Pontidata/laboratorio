---
id: S1-03
repositorio: radar-licitacoes
titulo: "[dev] Implementar normalizar_texto() para objeto e itens"
labels: [dev, ia]
estimativa: P
prazo: 2026-11-04
sprint: 1
---
## Contexto

Os textos do PNCP chegam com espaços duplos, quebras de linha no meio da frase e caracteres invisíveis.
Isso atrapalha a busca, a exibição no app e, na fase 3, a qualidade dos embeddings.

Esta é uma tarefa de **desenvolvimento assistido por IA**: use a IA como par de programação, entenda cada
linha e registre os prompts no PR.

## O que fazer

1. Crie a branch `feat/{{numero}}-normalizar-texto`.
2. Leia a docstring de `normalizar_texto()` e os 6 testes em `tests/unit/test_limpeza.py`.
3. Implemente a função.
4. Apague os `@todo_estagiaria` e rode `docker compose run --rm dev pytest tests/unit/test_limpeza.py`.
5. Teste em 5 objetos reais da base. Cole no PR o antes e o depois.
6. Abra o PR com a seção "Uso de IA" completa.

## Critérios de aceite

- [ ] 6 testes passando sem `@todo_estagiaria`.
- [ ] 5 exemplos reais com o antes e o depois no PR.
- [ ] Prompts registrados e cada linha da função explicada com suas palavras.
- [ ] `ruff check` e `ruff format --check` sem erros.
- [ ] CI verde.

## Conteúdo da faculdade praticado

Programação: strings, Unicode, expressões regulares e testes automatizados.

## Arquivos e TODOs relacionados

- `src/radar/tratamento/limpeza.py` — `TODO(estagiaria): #{{numero}}`
- `tests/unit/test_limpeza.py` — `@todo_estagiaria(issue={{numero}})`

## Dica de por onde começar

Pergunte à IA qual a diferença entre `" ".join(texto.split())` e uma expressão regular com `\s+`, e o que
`unicodedata.category()` devolve para um caractere de controle. Depois decida qual combinação passa nos
6 testes, e por quê.
