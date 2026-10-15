# Regras de uso de IA

Você **pode e deve** usar IA (ChatGPT, Claude, Gemini, Copilot…), como uma profissional usa.
As regras abaixo existem para você aprender mais rápido, e não para te vigiar.

## As 5 regras

1. **Registre no PR os principais prompts** que você usou, na seção "Uso de IA" do template.
2. **Explique com suas palavras** todo código que você entregar. Se não consegue explicar, ainda não terminou.
3. **Revise e teste** o que a IA gerou antes de abrir o PR: rode os testes, leia linha por linha, confira os nomes.
4. **Tarefas `sem-ia` são sem IA.** Elas treinam fundamentos (SQL, lógica, algoritmos). Pode consultar
   documentação oficial, livros e anotações da faculdade.
5. **Privacidade primeiro:** nunca cole numa ferramenta de IA:
   - senhas, tokens, chaves, o arquivo `.env`;
   - dados pessoais (nomes, CPFs, textos com pacientes), mesmo do PNCP;
   - código ou dados que não são públicos.

## Como pedir bem (e aprender no processo)

| Em vez de… | Tente… |
|---|---|
| "faz a função normalizar_texto" | "Tenho esta docstring e estes testes [cole]. Qual abordagem você usaria e por quê? Não escreva o código ainda." |
| "corrige esse erro" | "Este teste falha com [erro]. O que a mensagem quer dizer? Quais são 2 hipóteses?" |
| aceitar a primeira resposta | "Quais casos de borda essa solução não cobre?" |
| copiar um SQL pronto | "Explique o que cada JOIN desta consulta faz e por que não usar LEFT JOIN." |

Boas práticas:
- Dê contexto: o objetivo, as regras (docstring/testes), as restrições (Python 3.13, sem bibliotecas novas).
- Peça explicação e alternativas, não só código.
- Desconfie de funções, parâmetros ou bibliotecas que você não encontra na documentação oficial
  (a IA às vezes **inventa**).
- Se a IA sugeriu uma dependência nova, pergunte ao tech lead antes de adicionar.

## Como o uso de IA é avaliado

O critério "Uso consciente de IA" da [rubrica](RUBRICA.md) observa:
- os prompts estão registrados e mostram raciocínio (contexto, perguntas, verificação);
- você explica o código com as próprias palavras na review e no PR;
- você corrigiu ou descartou sugestões erradas, e disse por quê;
- você respeitou as tarefas `sem-ia` e a privacidade.

Usar muita IA não tira nota. Entregar o que não entende, sim.
