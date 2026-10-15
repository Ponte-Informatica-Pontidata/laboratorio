# Rubrica de avaliação

Ao fim de cada sprint, o tech lead dá uma nota de **1 a 5** em cada critério, sempre com evidências
(links de PRs, issues e dailies). A avaliação fica em `avaliacoes/sprint-NN.md`.

**A nota não é sobre a pessoa:** é sobre o trabalho daquela semana, comparado com o esperado para a fase.

## Critérios e níveis

| Critério | 1 — Inicial | 2 — Em desenvolvimento | 3 — Esperado | 4 — Acima do esperado | 5 — Referência |
|---|---|---|---|---|---|
| **Qualidade técnica** | código não roda ou não passa nos testes | passa nos testes com ajustes grandes na revisão | passa nos testes, legível, poucos ajustes | limpo, com testes extras e casos de borda | soluções elegantes que viram padrão no projeto |
| **Prazo** | entregas atrasadas sem aviso | atrasos avisados em cima da hora | entrega no prazo ou avisa com antecedência | entrega antes e ajuda a replanejar | antecipa riscos da sprint inteira |
| **Qualidade dos dados** | não confere resultados | confere só quando pedem | valida contagens, nulos e tipos por conta própria | documenta problemas encontrados e propõe correções | cria checagens automáticas que pegam erros reais |
| **Documentação** | não documenta | documenta só o pedido | PR, dicionário e docs atualizados | explicações claras, com exemplos | docs que outra pessoa usa sem perguntar nada |
| **Uso consciente de IA** | não registra prompts, não explica o código | registra, mas explica com dificuldade | registra, explica e testa o que a IA gerou | usa IA para explorar alternativas e justifica escolhas | ensina boas práticas de IA no PR e na review |
| **Comunicação** | some sem daily | daily irregular, bloqueios escondidos | daily em dia, bloqueios avisados cedo | perguntas boas e objetivas, contexto claro | facilita o trabalho de quem lê (resumos, links, prints) |
| **Autonomia** | precisa de ajuda em cada passo | segue a dica, mas trava nos imprevistos | resolve a issue com a dica e pesquisa própria | quebra problemas e propõe caminhos | propõe issues novas e melhorias de produto |

## O que se espera em cada fase

| Fase | Sprints | Expectativa |
|---|---|---|
| 1 — Base de dados | 0–3 | maioria em **2–3**; aprender o fluxo importa mais que velocidade |
| 2 — Ingestão e LGPD | 4–7 | maioria em **3** |
| 3 — IA aplicada | 8–13 | **3**, com algum **4** em dados ou IA |
| 4 — Produto e autonomia | 14–19 | **3–4**, autonomia em **4** |
| 5 — Encerramento | 20–21 | consolidação: a média final conta a evolução, não só a última nota |

## Como usar a avaliação

1. O tech lead (com o apoio do comando `/avaliar` no Claude Code) preenche notas e evidências.
2. A estagiária lê e comenta: concorda, discorda, traz contexto.
3. Uma combinação concreta de melhoria entra na próxima sprint.
