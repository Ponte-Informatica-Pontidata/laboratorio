# 🧪 Laboratório Pontidata

[![CI](https://github.com/Ponte-Informatica-Pontidata/laboratorio/actions/workflows/ci.yml/badge.svg)](https://github.com/Ponte-Informatica-Pontidata/laboratorio/actions/workflows/ci.yml)

Programa de estágio em **Big Data e Inteligência Artificial** da Ponte Informática (Pontidata).
O laboratório simula uma empresa de tecnologia de verdade: produto real, dados reais, prazos,
revisão de código, rituais de equipe e avaliação.

> **Como funciona:** o tech lead monta, a estagiária completa.
> Cada aplicação nasce estruturada e funcionando. As partes que a estagiária constrói ficam marcadas
> no código com `TODO(estagiaria): #<issue>` e têm um teste esperando. A cada sprint fica menos coisa
> pronta e mais responsabilidade com ela.

## Mapa

| Repositório | Para quê |
|---|---|
| [`laboratorio`](https://github.com/Ponte-Informatica-Pontidata/laboratorio) (este) | regras, onboarding, rubrica, roadmap, sprints, daily e a gestão |
| [`radar-licitacoes`](https://github.com/Ponte-Informatica-Pontidata/radar-licitacoes) | o primeiro produto: licitações abertas do PNCP, busca por significado e resumos por IA |

| Documento | Leia quando |
|---|---|
| [ONBOARDING.md](ONBOARDING.md) | primeira semana (Sprint 0) |
| [PROCESSO.md](PROCESSO.md) | para entender como uma semana funciona |
| [REGRAS-IA.md](REGRAS-IA.md) | antes de usar IA em qualquer tarefa |
| [RUBRICA.md](RUBRICA.md) | para saber como você é avaliada |
| [ROADMAP.md](ROADMAP.md) | para ver as 24 semanas |
| [sprints/](sprints/) | detalhes de cada sprint e das issues |

## Calendário

- **26/10/2026 a 09/04/2027:** 24 semanas, com 22 sprints de 1 semana e 2 semanas de recesso no fim do ano.
- Até **12 horas por semana**.
- Toda a gestão acontece no GitHub: issues, Pull Requests, milestones (sprints) e o quadro do
  GitHub Projects (**Backlog → Em desenvolvimento → Em revisão → Bloqueado → Pronto**).

## A semana em uma tabela

| Quando | O quê | Onde |
|---|---|---|
| Segunda | Planejamento: ler as issues da sprint e comentar dúvidas | milestone da sprint |
| Todo dia de trabalho | **Daily assíncrona**: fiz / vou fazer / bloqueios | issue fixada "Daily assíncrona" |
| Durante a semana | branch → commits → Pull Request → revisão → merge | `radar-licitacoes` |
| Sexta | **Review** (demo, com link quando publicado) e **retrospectiva** | issue da review da sprint |

## Gestão (para o tech lead)

A pasta [`gestao/`](gestao/) roda no Docker local do tech lead. Ela traz um servidor MCP com as ferramentas
do laboratório e o MCP oficial do GitHub, para o **Claude Code** atuar como "cérebro" do laboratório:
ele lê dailies e PRs, aponta riscos, revisa código e prepara a próxima sprint, com o GitHub como
única fonte de verdade. Veja [`gestao/README.md`](gestao/README.md).
