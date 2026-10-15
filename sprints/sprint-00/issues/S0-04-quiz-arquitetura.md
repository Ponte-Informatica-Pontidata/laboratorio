---
id: S0-04
repositorio: laboratorio
titulo: "[docs] Ler a arquitetura e responder o quiz de entendimento"
labels: [docs, estudo]
estimativa: P
prazo: 2026-10-29
sprint: 0
---
## Contexto

Antes de mexer no código, entender o desenho evita retrabalho. O `docs/arquitetura.md` e os ADRs
(`docs/adr/`) do `radar-licitacoes` explicam **como** o sistema está organizado e **por quê**.

## O que fazer

1. Leia `docs/arquitetura.md` e os 8 ADRs do `radar-licitacoes`.
2. Responda o quiz num comentário desta issue:
   1. Qual camada conhece o formato JSON do PNCP? Por que isso é bom?
   2. Por que os serviços dependem de um *Repository* e não direto do Postgres? Dê um exemplo nos testes.
   3. O que é a *Strategy* de IA e o que muda quando a variável `RADAR_EMBEDDINGS` troca de valor?
   4. Por que `halfvec(384)` e não `vector(384)`?
   5. Cite 2 comportamentos estranhos da API do PNCP e como o projeto lida com eles.
   6. O que significa `XFAIL` no resumo do pytest? O que você deve fazer quando um teste seu virar `XPASS`?
   7. Por que o app vai para o Streamlit Community Cloud e não para a Vercel?
   8. **A sua pergunta:** o que ficou confuso? (obrigatória: sempre tem algo)

## Critérios de aceite

- [ ] As 8 respostas estão num comentário.
- [ ] As respostas estão com suas palavras. Pode usar IA para tirar dúvidas, mas registre os prompts no comentário.
- [ ] Pelo menos 1 dúvida real levantada na pergunta 8.

## Conteúdo da faculdade praticado

Engenharia de software (padrões de projeto, arquitetura em camadas), bancos vetoriais e computação em nuvem.

## Arquivos e TODOs relacionados

- `radar-licitacoes/docs/arquitetura.md` e `radar-licitacoes/docs/adr/*.md`.

## Dica de por onde começar

Não precisa decorar. Para cada pergunta, ache o trecho do documento que responde e reescreva como você
explicaria para alguém da sua turma. Se a resposta precisar de código, cite o arquivo e a função.
