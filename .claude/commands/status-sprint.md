---
description: Panorama da sprint (atual ou número informado) com atrasos, bloqueios e riscos
---
Use o MCP `laboratorio`: `sprint_atual` e `status_sprint` (numero=$ARGUMENTS, se informado), além de `prs_em_revisao`.

Responda com:
1. Objetivo da sprint e quanto falta (dias úteis).
2. Tabela das issues: repositório#número, título, estado/status no quadro, prazo, atrasada?
3. PRs abertos ligados à sprint, com o estado do CI e da revisão.
4. **Riscos** concretos (ex.: "S1-02 depende da carga e a daily de ontem citou erro no Docker").
5. **Ajustes sugeridos:** cortar escopo, mover o desafio, oferecer pareamento. Nada é aplicado sem o OK.
