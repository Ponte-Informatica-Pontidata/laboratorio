---
id: S0-03
repositorio: radar-licitacoes
titulo: "[dados] Criar o banco com as migrations e carregar a base CSV"
labels: [dados, sem-ia]
estimativa: M
prazo: 2026-10-29
sprint: 0
---
## Contexto

A base real do Radar está em `dados/csv`. É um recorte da API do PNCP para Minas Gerais, com todas as
licitações com proposta aberta em 15/10/2026, os itens delas e os contratos publicados nos 30 dias anteriores.
As contagens exatas estão em `dados/MANIFESTO.json`.

A estrutura do banco (DDL) está pronta em `supabase/migrations` e a carga (DML), em `banco/carga`.
**Nesta tarefa você é a executora:** roda cada passo, entende o que ele faz e confere o resultado.
É exatamente o que você vai repetir no Supabase de produção na Sprint 7.

## O que fazer

1. Leia `banco/README.md`.
2. Leia as migrations **em ordem** e anote, para cada uma, o que ela cria.
3. Crie a estrutura: `docker compose run --rm dev bash banco/migrar.sh`.
4. Rode a carga em três passos, **lendo cada arquivo antes de rodar**:
   - `docker compose run --rm dev psql -f banco/carga/01_staging.sql`
   - `docker compose run --rm dev psql -f banco/carga/02_transformar.sql`
   - `docker compose run --rm dev psql -f banco/carga/03_validar.sql`
5. Atualize o app (http://localhost:8501) e veja as licitações abertas. Na barra lateral, escolha a data 15/10/2026.
6. Escreva **3 consultas exploratórias** suas (sem IA) e cole as consultas com os resultados. Exemplos:
   - quantas contratações abertas por modalidade (com o nome da modalidade);
   - os 5 órgãos com mais contratações abertas;
   - a contratação com maior valor estimado.
7. Responda nesta issue, com suas palavras:
   - (a) por que a carga passa primeiro pelo schema `staging`, com tudo como texto?
   - (b) o que acontece se você rodar o `02_transformar.sql` duas vezes? Por quê?
   - (c) o que a constraint `fornecedor_lgpd_pf_sem_identificacao` impede, e por que ela existe?

## Critérios de aceite

- [ ] As 9 migrations aparecem em `supabase_migrations.schema_migrations`.
- [ ] O `03_validar.sql` termina com "Validação da carga OK".
- [ ] Print do app mostrando licitações abertas.
- [ ] 3 consultas SQL escritas por você, com os resultados, num comentário.
- [ ] Respostas (a), (b) e (c) com suas palavras.

## Conteúdo da faculdade praticado

Banco de dados: DDL × DML, chaves primárias e estrangeiras, constraints, transações, tipos de dados,
fuso horário (`timestamptz`) e importação de CSV.

## Arquivos e TODOs relacionados

- `supabase/migrations/*.sql`, `banco/carga/*.sql`, `banco/README.md`, `dados/MANIFESTO.json`, `dados/ORIGEM.md`.

## Dica de por onde começar

Para a pergunta (b), procure `ON CONFLICT` no `02_transformar.sql`. Para as consultas, comece com
`select modalidade_id, count(*) from radar.contratacao group by 1 order by 2 desc;`. Depois traga o nome
da modalidade com um `JOIN` em `radar.dominio_modalidade`. Para abrir o psql: `docker compose run --rm dev psql`.
