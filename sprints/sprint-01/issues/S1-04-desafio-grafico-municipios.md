---
id: S1-04
repositorio: radar-licitacoes
titulo: "[desafio] Gráfico de licitações abertas por município"
labels: [desafio, dev]
estimativa: P
prazo: 2026-11-06
sprint: 1
---
## Contexto

**Desafio opcional.** Faça só se as outras issues da sprint estiverem prontas.

Ver onde estão as oportunidades ajuda quem usa o Radar e prepara o painel da Sprint 2.

## O que fazer

1. Crie a branch `feat/{{numero}}-grafico-municipios`.
2. Crie um método novo no Repository (Postgres **e** memória) que devolve os N municípios com mais
   licitações abertas, e um método no Service que o usa.
3. Escreva um teste unitário do Service com o `RepositorioMemoria`.
4. Mostre um gráfico de barras com os 15 municípios no app, em `app/Inicio.py` ou numa página nova
   `app/pages/1_Municipios.py`.

## Critérios de aceite

- [ ] Gráfico no app com título e eixos legíveis (print no PR).
- [ ] A consulta passa por Service → Repository (nada de SQL dentro do Streamlit).
- [ ] Teste unitário novo passando.
- [ ] CI verde.

## Conteúdo da faculdade praticado

Visualização de dados e arquitetura em camadas, na prática.

## Arquivos e TODOs relacionados

- `src/radar/persistencia/postgres.py`, `src/radar/persistencia/memoria.py`, `src/radar/servicos/licitacoes.py` e `app/`.

## Dica de por onde começar

`st.bar_chart` aceita um DataFrame cujo índice é a categoria (o município). Se a {{S1-01}} já estiver
pronta, a view `vw_licitacoes_abertas` deixa a consulta bem curta.
