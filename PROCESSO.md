# Processo de trabalho

Um Scrum enxuto, assíncrono e 100% no GitHub, ajustado a uma estagiária com até 12 h por semana.

## Papéis

| Papel | Quem | Responsabilidades |
|---|---|---|
| Tech lead / Scrum Master | Pedro | prioriza, monta a estrutura, escreve as issues, revisa PRs, avalia, remove bloqueios |
| Desenvolvedora (estagiária) | estagiária | executa as issues, faz a daily, abre PRs, demonstra na review, propõe melhorias |
| "Cérebro" de gestão | Claude Code + MCP (`gestao/`) | lê o GitHub, resume dailies e PRs, aponta riscos, rascunha revisões e sprints para o tech lead aprovar |

## Cadência (sprint de 1 semana)

| Momento | O quê | Saída |
|---|---|---|
| Segunda (até 1 h) | **Planejamento:** a sprint já está no milestone; ela lê cada issue e comenta dúvidas | dúvidas respondidas, issue movida para "Em desenvolvimento" |
| Cada dia de trabalho | **Daily assíncrona** na issue fixada | fiz / vou fazer / bloqueios |
| Durante a semana | issue → branch → PR → revisão → merge | PRs revisados em até 1 dia útil |
| Sexta (até 45 min) | **Review:** demonstração (com link do app publicado a partir da Sprint 7) | comentário na issue da review |
| Sexta | **Retrospectiva:** o que funcionou, o que melhorar, **1 ação concreta** | ação vira item da próxima sprint |
| Fim da sprint | **Avaliação** pela rubrica (1 a 5) | registro em `avaliacoes/` |

## Quadro (GitHub Projects)

**Backlog → Em desenvolvimento → Em revisão → Bloqueado → Pronto**

- No máximo **1 issue em "Em desenvolvimento"** por vez (foco termina tarefas).
- Abriu o PR, a issue vai para **Em revisão**.
- Travou por mais de 1 hora sem avançar: **Bloqueado** e avise na daily o que já tentou.
- **Pronto** = PR mergeado + critérios de aceite marcados.

## Definition of Ready (a issue está pronta para começar quando…)

- [ ] tem contexto, passos, critérios de aceite, estimativa e prazo;
- [ ] os arquivos e TODOs relacionados estão indicados;
- [ ] cabe na sprint (P ≤ 2 h, M 3–5 h, G 6–8 h).

## Definition of Done (geral)

- [ ] critérios de aceite da issue marcados;
- [ ] CI verde (lint, testes, banco do zero, gitleaks, título do PR);
- [ ] `@todo_estagiaria` removido dos testes da issue;
- [ ] PR com template completo (inclui prompts de IA e explicação com suas palavras);
- [ ] revisado e aprovado pelo tech lead, merge com squash;
- [ ] documentação atualizada quando muda comportamento, dados ou comandos.

Cada sprint pode acrescentar itens à DoD (veja `sprints/sprint-NN/README.md`).

## Git

- `main` protegida: só entra por Pull Request aprovado e com CI verde.
- Uma branch por issue: `tipo/<numero>-descricao-curta` (`feat/7-normalizar-texto`, `docs/3-dicionario-itens`).
- Commits e título do PR em **Conventional Commits**:

| Tipo | Quando |
|---|---|
| `feat` | funcionalidade nova |
| `fix` | correção de bug |
| `docs` | só documentação |
| `test` | só testes |
| `refactor` | muda código sem mudar comportamento |
| `chore` / `ci` / `build` | manutenção, CI, dependências |

Exemplo: `feat: normaliza textos do objeto da contratação`.

- Merge sempre com **squash** (um commit por issue na `main`, com o título do PR).

## Revisão de código

- O tech lead revisa em até **1 dia útil**. Comentários são sobre o código, nunca sobre a pessoa.
- Você responde cada comentário: corrige com um commit novo ou explica por que não. Não apague a discussão.
- "Aprovar com sugestões" = pode mergear; as sugestões viram issue se forem grandes.

## Estimativas e prazos

- P ≤ 2 h · M 3–5 h · G 6–8 h. Na fase 1, nada de G.
- Prazo estourado não é punição: é dado. Avise **antes** do prazo, na daily, se vai atrasar.

## Lei do Estágio (Lei 11.788/2008)

- Jornada máxima de 6 h/dia e 30 h/semana. Aqui o combinado é **até 12 h/semana**.
- **Semana de provas:** a carga cai pelo menos pela metade (art. 10, §2º). Avise o calendário da faculdade
  e a sprint é replanejada.
- **Recesso:** 30 dias por ano, proporcional. Previsto entre 21/12/2026 e 01/01/2027 (a confirmar).

## Comunicação

- Tudo que é trabalho fica no GitHub (issue, PR, daily). Combinado em conversa privada vira comentário na issue.
- Dúvida? Comente na issue e mencione `@pedro-canedo`.
- **Nunca** cole senhas, tokens, `.env` ou dados pessoais em issue, PR, commit ou ferramenta de IA.
