---
id: S0-06
repositorio: radar-licitacoes
titulo: "[desafio] Consultar os CSVs com DuckDB e comparar com o Postgres"
labels: [desafio, dados]
estimativa: P
prazo: 2026-10-30
sprint: 0
---
## Contexto

**Desafio opcional.** Faça só se as outras issues da sprint estiverem prontas.

Nem toda análise precisa de um banco rodando. O DuckDB consulta CSV e Parquet direto do arquivo, muito
rápido, e já está no ambiente (dependência de desenvolvimento). Saber quando usar cada ferramenta é parte
do trabalho de dados.

## O que fazer

1. Abra um Python no container: `docker compose run --rm dev python`.
2. Rode `import duckdb` e depois `duckdb.sql("select count(*) from 'dados/csv/contratacao.csv'")`.
3. Repita 2 das suas consultas da {{S0-03}} no DuckDB, lendo os CSVs. Compare os resultados e o tempo.
4. Converta `contratacao_item` para Parquet dentro de `dados/local/` (essa pasta não vai para o git) e
   compare o tamanho do Parquet com o do CSV.

## Critérios de aceite

- [ ] As mesmas respostas no DuckDB e no Postgres, ou uma explicação da diferença.
- [ ] Tamanhos de CSV × Parquet comparados.
- [ ] Três linhas suas: quando você usaria DuckDB e quando usaria Postgres.

## Conteúdo da faculdade praticado

Formatos de dados (CSV × colunar), OLTP × OLAP e processamento analítico local.

## Arquivos e TODOs relacionados

- `dados/csv/*.csv`. Não há TODO no código.

## Dica de por onde começar

Procure na documentação do DuckDB o comando `COPY ... TO ... (FORMAT parquet)`. Antes de comitar
qualquer coisa, confira com `git status` que nenhum arquivo `.parquet` entrou.
