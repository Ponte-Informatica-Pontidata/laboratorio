# Sprints

Cada sprint tem uma pasta `sprint-NN/` com:
- `README.md`: objetivo em uma frase, datas, issues, Definition of Done da sprint e rituais;
- `issues/*.md`: uma issue por arquivo, pronta para publicar no GitHub.

## Formato de uma issue

```markdown
---
id: S1-03                       # identificador estável (sprint-sequência)
repositorio: radar-licitacoes   # onde a issue é criada
titulo: "[dev] Implementar normalizar_texto() para objeto e itens"
labels: [dev, ia]
estimativa: P                   # P (≤ 2 h) | M (3–5 h) | G (6–8 h)
prazo: 2026-11-04
sprint: 1
---
## Contexto
## O que fazer
## Critérios de aceite
## Conteúdo da faculdade praticado
## Arquivos e TODOs relacionados
## Dica de por onde começar
```

## Publicação

O MCP de gestão (`gestao/`) publica as issues de uma sprint (ferramenta `publicar_sprint`). A publicação
é idempotente: cada issue leva o marcador oculto `<!-- lab-id: S1-03 -->` e não é criada duas vezes.
A milestone `Sprint NN` é criada (com prazo na sexta) nos repositórios envolvidos.

Também dá para publicar pela linha de comando:

```bash
cd gestao/mcp-laboratorio
uv run laboratorio-publicar --sprint 1            # mostra o que faria (dry-run)
uv run laboratorio-publicar --sprint 1 --executar # cria de verdade
```

Referências entre issues: escreva `{{S0-03}}` no corpo e a publicação troca pelo link da issue
(quando ela já existir).
