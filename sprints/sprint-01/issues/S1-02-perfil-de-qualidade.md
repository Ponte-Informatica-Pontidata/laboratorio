---
id: S1-02
repositorio: radar-licitacoes
titulo: "[dados] Implementar perfil_qualidade() e publicar o diagnóstico da base"
labels: [dados, estudo]
estimativa: M
prazo: 2026-11-06
sprint: 1
---
## Contexto

Antes de limpar, **medir**. A `perfil_qualidade()` é a primeira ferramenta de qualidade do projeto: para
cada coluna, mostra quantos valores faltam, quantos são distintos e qual é o mais comum. Com ela você faz o
diagnóstico da base real, e esse diagnóstico vai guiar a limpeza na Sprint 3. Os testes em
`tests/unit/test_qualidade.py` são a especificação.

## O que fazer

1. Crie a branch `feat/{{numero}}-perfil-qualidade`.
2. Implemente `perfil_qualidade()` em `src/radar/tratamento/qualidade.py`, seguindo a docstring.
3. Apague os `@todo_estagiaria` dos 4 testes e rode `docker compose run --rm dev pytest tests/unit/test_qualidade.py`.
4. Rode o perfil nas tabelas `radar.contratacao`, `radar.contratacao_item` e `radar.contrato`.
5. Escreva `docs/qualidade/diagnostico-sprint-01.md` com:
   - o perfil das 3 tabelas;
   - **5 achados**: o que está estranho, por que importa e o que você sugere fazer.
6. Abra o PR.

## Critérios de aceite

- [ ] 4 testes passando sem `@todo_estagiaria`.
- [ ] Diagnóstico com o perfil das 3 tabelas e 5 achados.
- [ ] Pelo menos 1 achado sobre **valores** (ex.: zeros, extremos) e 1 sobre **textos**.
- [ ] Prompts de IA registrados no PR (se usou).
- [ ] CI verde.

## Conteúdo da faculdade praticado

Estatística descritiva, dimensões de qualidade de dados (completude, unicidade, validade) e pandas.

## Arquivos e TODOs relacionados

- `src/radar/tratamento/qualidade.py` — `TODO(estagiaria): #{{numero}}`
- `tests/unit/test_qualidade.py` — `@todo_estagiaria(issue={{numero}})`
- `docs/qualidade/diagnostico-sprint-01.md` (arquivo novo)

## Dica de por onde começar

Para contar texto só com espaços como nulo, transforme esses valores em ausentes **antes** de contar:
veja `Series.str.strip()` e `Series.replace()`. Para levar uma tabela para o pandas dentro do container:

```python
import pandas as pd
from radar.persistencia.conexao import conectar
with conectar() as conn:
    df = pd.DataFrame(conn.execute("select * from radar.contratacao").fetchall())
```
