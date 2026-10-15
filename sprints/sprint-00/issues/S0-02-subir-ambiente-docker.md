---
id: S0-02
repositorio: radar-licitacoes
titulo: "[infra] Subir o ambiente de desenvolvimento do Radar com Docker"
labels: [infra]
estimativa: P
prazo: 2026-10-28
sprint: 0
---
## Contexto

O Radar roda inteiro em containers:
- banco Postgres com pgvector;
- app em Streamlit;
- um container de trabalho (`dev`) com Python, psql e Supabase CLI.

O CI usa o mesmo ambiente, então "na minha máquina funciona" deixa de ser desculpa. E ninguém precisa
instalar Postgres ou Python direto no computador.

## O que fazer

1. Clone o repositório `radar-licitacoes`.
2. Leia a seção "Começando" do `README.md` e os comentários no topo do `docker-compose.yml`.
3. Suba o ambiente: `docker compose up -d --build`.
4. Confira: `docker compose ps` (o `db` deve estar `healthy` e o `app`, `running`).
5. Abra http://localhost:8501. O app deve avisar que o **banco está vazio** (isso se resolve na próxima issue).
6. Rode os testes: `docker compose run --rm dev pytest`.
7. Comente nesta issue, com suas palavras, para que serve cada serviço do compose: `db`, `app`, `dev`, `adminer` e `ollama`.

## Critérios de aceite

- [ ] Saída do `docker compose ps` colada num comentário (db `healthy`, app `running`).
- [ ] Print do app avisando que o banco está vazio.
- [ ] Linha final do pytest colada (quantos `passed` e quantos `xfailed`).
- [ ] Comentário explicando os 5 serviços com suas palavras.

## Conteúdo da faculdade praticado

Infraestrutura e containers, arquitetura cliente-servidor e redes (portas, serviços).

## Arquivos e TODOs relacionados

- `docker-compose.yml`, `Dockerfile` e `README.md` do `radar-licitacoes`.

## Dica de por onde começar

Os `xfailed` no pytest são esperados: são testes que **esperam por você** nas próximas issues (o resumo
no fim lista quais). Se a porta 54322 ou 8501 estiver ocupada, o `.env.example` mostra como mudar a do banco.
