---
description: Revisão de PR da estagiária (técnica + processo), com rascunho dos comentários
argument-hint: <repositorio> <numero>
---
Revise o PR $ARGUMENTS (padrão do repositório: radar-licitacoes).

1. Com o MCP `github`, leia o PR, o diff, os arquivos alterados, os checks do CI e a issue ligada (`Closes #`).
2. Com o MCP `laboratorio`, rode `prs_em_revisao` para o checklist do processo.
3. Compare com a issue: todos os critérios de aceite foram atendidos? O `@todo_estagiaria` da issue saiu?

Avalie, nesta ordem:
- **Correção:** o código faz o que a issue pede? Casos de borda? SQL correto (JOINs, NULL, fuso, tipos)?
- **Testes:** passam? Cobrem o pedido? Ela adicionou algum?
- **Dados e LGPD:** algum dado pessoal no código, nos testes ou na descrição?
- **Arquitetura:** respeitou as camadas (nada de SQL no Streamlit, Adapter só na coleta etc.)?
- **Processo:** título em Conventional Commits, template completo, seção "Uso de IA" com prompts e
  "Explique com suas palavras" coerente com o código.

Entregue:
- Um **resumo** (aprovar / pedir ajustes) com justificativa.
- **Comentários de linha** em rascunho: arquivo, linha, comentário. Use tom de mentoria e faça perguntas
  que levem ao raciocínio ("o que acontece se valor_total vier nulo?") em vez de entregar a correção.
- 1 elogio específico e sincero.

Não publique a revisão sem o OK do tech lead.
