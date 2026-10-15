# snapshot_pncp — base real do Radar (ferramenta do tech lead)

Gera os CSVs de `radar-licitacoes/dados/csv/` a partir da API pública do PNCP, com a **LGPD aplicada
antes de gravar** e uma validação final que impede a gravação se sobrar dado pessoal.

```bash
cd ferramentas/snapshot_pncp
uv run snapshot_pncp.py --uf MG --referencia 2026-10-15 \
    --saida ../../../radar-licitacoes/dados/csv --cache ../../../.cache/pncp
# depois, no radar-licitacoes:
python scripts/gerar_sql_carga.py     # atualiza staging, 01_staging.sql e 03_validar.sql
```

| Parâmetro | Padrão | Para quê |
|---|---|---|
| `--uf` | `MG` | UF do recorte (troque para `GO`, `SP`...) |
| `--referencia` | hoje | data de referência (deixa a extração reprodutível) |
| `--dias-proposta` | 365 | teto do encerramento das propostas (365 = todas as abertas) |
| `--dias-contratos` | 30 | janela de publicação dos contratos |
| `--intervalo` | 0.8 | segundos mínimos entre chamadas (aumenta sozinho a cada 429) |
| `--etapas` | todas | `contratacoes,itens,contratos,csv`. Rode só `csv` para regerar offline a partir do cache |
| `--limite-itens` | 0 | só para teste: busca itens de N contratações |

## O que aprendemos com a API (15/10/2026)

- A API de **consultas** devolve **HTTP 429 depois de ~20 chamadas em menos de 1 minuto**. Com 3 s
  entre chamadas, nenhum 429 em 362 páginas. O ritmo adaptativo (AIMD) do cliente resolve sozinho.
- A API de **itens** (`/api/pncp/v1/...`) aguentou 1 chamada por segundo sem 429.
- Sem `tamanhoPagina`, o endpoint de itens devolve **só 10 itens**.
- `/contratos` não filtra UF e o filtro de data é pela **publicação**.
- O tempo total para MG ficou em cerca de 2 h (5,3 mil contratações, mais de 5 mil chamadas de itens e 30 dias de contratos).

## LGPD (resumo; detalhes em `radar-licitacoes/dados/ORIGEM.md`)

- PF/PE sem documento e sem nome; chave `PF-<hmac>` com *pepper* secreto em `.cache/pncp/.pepper`
  (**não versionar**: sem ele não dá para regerar as mesmas chaves).
- CPF (formatado, parcial ou 11 dígitos com DV válido), processo judicial (CNJ), nomes após "paciente",
  "Sra.", "em favor de" etc. e nomes de PF conhecidos são mascarados.
- A varredura final recusa gravar se sobrar qualquer ocorrência.
