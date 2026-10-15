# Sprint 0 — Onboarding (26/10 a 30/10/2026)

**Objetivo:** ambiente rodando, banco criado e carregado com a base real, arquitetura entendida e
primeiro Pull Request aprovado.

| ID | Repositório | Issue | Labels | Est. | Prazo |
|---|---|---|---|---|---|
| S0-01 | laboratorio | [infra] Configurar contas e ferramentas (GitHub 2FA, Docker/WSL2, VS Code) | infra, estudo | P | 27/10 |
| S0-02 | radar-licitacoes | [infra] Subir o ambiente de desenvolvimento do Radar com Docker | infra | P | 28/10 |
| S0-03 | radar-licitacoes | [dados] Criar o banco com as migrations e carregar a base CSV | dados, sem-ia | M | 29/10 |
| S0-04 | laboratorio | [docs] Ler a arquitetura e responder o quiz de entendimento | docs, estudo | P | 29/10 |
| S0-05 | radar-licitacoes | [docs] Primeiro PR: completar o dicionário de contratacao_item | docs, dados | P | 30/10 |
| S0-06 | radar-licitacoes | [desafio] Consultar os CSVs com DuckDB e comparar com o Postgres | desafio, dados | P | 30/10 (opcional) |

Carga planejada: cerca de 9 h, mais o desafio opcional. Sobra folga para instalação e imprevistos.

## Definition of Done da Sprint 0

- [ ] Ambiente Docker funcionando (db healthy, app no ar, pytest com `passed` e `xfailed`).
- [ ] Banco local criado pelas migrations e carregado, com `03_validar.sql` OK.
- [ ] Quiz de arquitetura respondido com as próprias palavras.
- [ ] Primeiro PR mergeado com squash, template completo e CI verde.
- [ ] Daily postada em todos os dias de trabalho.

## Rituais

| Quando | O quê |
|---|---|
| Seg 26/10 | Boas-vindas e planejamento: ler as 6 issues e comentar dúvidas |
| Todos os dias | Daily na issue fixada do `laboratorio` |
| Sex 30/10 | Review (mostrar o app com os dados carregados) e retrospectiva na issue "Review e retro — Sprint 00" |
