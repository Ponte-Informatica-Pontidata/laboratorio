# Sprint 1 — Conhecer a base (03/11 a 06/11/2026)

**Objetivo:** conhecer a base com consultas, um diagnóstico de qualidade e o primeiro tratamento de texto.

Semana de 4 dias: segunda, 02/11, é feriado de Finados.

| ID | Issue | Labels | Est. | Prazo |
|---|---|---|---|---|
| S1-01 | [dados] Criar as views do painel via migration (licitações abertas e resumo por modalidade/UF) | dados, sem-ia | M | 05/11 |
| S1-02 | [dados] Implementar perfil_qualidade() e publicar o diagnóstico da base | dados, estudo | M | 06/11 |
| S1-03 | [dev] Implementar normalizar_texto() para objeto e itens | dev, ia | P | 04/11 |
| S1-04 | [desafio] Gráfico de licitações abertas por município | desafio, dev | P | 06/11 (opcional) |

Todas as issues são do `radar-licitacoes`. Carga planejada: cerca de 10 h, mais o desafio opcional.

Equilíbrio da sprint:
- **dados:** S1-01 (SQL puro, `sem-ia`) e S1-02 (pandas e análise);
- **desenvolvimento assistido por IA:** S1-03, com os prompts registrados;
- **documentação:** o diagnóstico (S1-02) e as views no dicionário (S1-01);
- **desafio extra:** S1-04, opcional.

## Definition of Done da Sprint 1

- [ ] Views criadas por migration **nova** (nenhuma migration antiga editada) e documentadas no dicionário.
- [ ] `perfil_qualidade()` implementada e o diagnóstico publicado em `docs/qualidade/diagnostico-sprint-01.md`.
- [ ] `normalizar_texto()` implementada, com exemplos reais antes/depois no PR.
- [ ] Nenhum `@todo_estagiaria` restante para as issues S1-01, S1-02 e S1-03.
- [ ] CI verde em todos os PRs, inclusive o job "Banco do zero".
- [ ] Daily em todos os dias de trabalho, com a retrospectiva da Sprint 0 aplicada (1 ação).

## Rituais

| Quando | O quê |
|---|---|
| Ter 03/11 | Planejamento: ler as issues e comentar dúvidas |
| Todos os dias | Daily |
| Sex 06/11 | Review (mostrar as views e o diagnóstico) e retrospectiva na issue "Review e retro — Sprint 01" |
