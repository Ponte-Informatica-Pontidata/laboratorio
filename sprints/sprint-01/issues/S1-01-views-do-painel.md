---
id: S1-01
repositorio: radar-licitacoes
titulo: "[dados] Criar as views do painel via migration (licitações abertas e resumo por modalidade/UF)"
labels: [dados, sem-ia]
estimativa: M
prazo: 2026-11-05
sprint: 1
---
## Contexto

O app e as análises vão fazer sempre as mesmas perguntas: "o que está aberto agora?" e "quanto se compra
por modalidade e UF?". Uma **view** guarda essa regra num lugar só, versionada em migration, em vez de
repetir o SQL em vários lugares. Os testes em `tests/integracao/test_views.py` já descrevem as colunas
esperadas.

## O que fazer

1. Crie a branch `feat/{{numero}}-views-painel`.
2. Crie uma migration **nova**: `docker compose run --rm dev supabase migration new criar_views_painel`.
3. Escreva a view `radar.vw_licitacoes_abertas`, com as colunas nesta ordem:
   - `numero_controle_pncp`
   - `orgao` (razão social)
   - `municipio`
   - `uf`
   - `modalidade` (nome)
   - `objeto_compra`
   - `valor_total_estimado`
   - `data_encerramento_proposta`
   - `dias_para_encerrar` (número inteiro de dias até o encerramento)
   - `link_pncp` (`https://pncp.gov.br/app/editais/{cnpj}/{ano}/{sequencial}`)

   Mostre só as contratações com encerramento a partir de agora.
4. Escreva a view `radar.vw_resumo_modalidade_uf`, com as colunas `uf`, `modalidade`, `quantidade`,
   `valor_total_estimado` (soma) e `valor_medio_estimado` (média). Ela considera **todas** as contratações.
5. Aplique com `docker compose run --rm dev bash banco/migrar.sh` e rode
   `docker compose run --rm dev pytest -m integracao`.
6. Apague os `@todo_estagiaria` dos dois testes de view e documente as views numa seção nova "Views" do
   `dados/DICIONARIO.md`.
7. Abra o PR.

## Critérios de aceite

- [ ] Migration nova criada; nenhuma migration existente foi editada.
- [ ] Os 2 testes de view passam sem `@todo_estagiaria`.
- [ ] `docker compose run --rm dev pytest -m integracao` verde.
- [ ] As views estão documentadas no dicionário.
- [ ] SQL escrito por você, sem IA (label `sem-ia`).
- [ ] CI verde, inclusive o job "Banco do zero", que aplica sua migration num banco novo.

## Conteúdo da faculdade praticado

SQL: views, JOIN entre várias tabelas, GROUP BY, funções de agregação, funções de data e concatenação de texto.

## Arquivos e TODOs relacionados

- `supabase/migrations/<sua-migration>.sql` (arquivo novo)
- `tests/integracao/test_views.py` — `@todo_estagiaria(issue={{numero}})`
- `dados/DICIONARIO.md`

## Dica de por onde começar

A consulta de `RepositorioPostgres.listar_abertas` (`src/radar/persistencia/postgres.py`) já faz os JOINs
de que você precisa. Para `dias_para_encerrar`, compare o resultado de subtrair duas datas (`date`) com o
de subtrair dois `timestamptz`. Qual dá um inteiro direto?
