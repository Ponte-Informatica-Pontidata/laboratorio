---
id: S0-01
repositorio: laboratorio
titulo: "[infra] Configurar contas e ferramentas (GitHub 2FA, Docker/WSL2, VS Code)"
labels: [infra, estudo]
estimativa: P
prazo: 2026-10-27
sprint: 0
---
## Contexto

Para trabalhar no laboratório você usa as mesmas ferramentas de uma equipe de engenharia de dados:
- **GitHub com 2FA**, porque a organização guarda código e dados da empresa;
- **Git**;
- **Docker**, porque todo o ambiente roda em containers e fica igual em qualquer máquina;
- **VS Code**.

## O que fazer

1. Ative a **autenticação em dois fatores (2FA)** na sua conta do GitHub.
2. Aceite o convite da organização `Ponte-Informatica-Pontidata` (chega por e-mail).
3. Instale o Git, o **Docker Desktop** (no Windows, aceite o WSL2) e o VS Code.
4. Configure o Git com seu nome e o mesmo e-mail da conta do GitHub:
   `git config --global user.name "Seu Nome"` e `git config --global user.email "seu@email"`.
5. Teste: `git --version`, `docker version` e `docker run hello-world`.
6. Poste sua **primeira daily** na issue fixada "Daily assíncrona".

## Critérios de aceite

- [ ] 2FA ativo na conta do GitHub.
- [ ] Você aparece como membro da organização.
- [ ] `docker run hello-world` funcionando (cole a mensagem final num comentário desta issue).
- [ ] Git configurado com nome e e-mail.
- [ ] Primeira daily postada.

## Conteúdo da faculdade praticado

Sistemas operacionais e virtualização (container × máquina virtual) e segurança da informação (autenticação em dois fatores).

## Arquivos e TODOs relacionados

- `ONBOARDING.md`, seções 1 e 2.

## Dica de por onde começar

O Docker Desktop no Windows usa o WSL2 por baixo. Se aparecer erro de virtualização, pesquise como
ativar "Virtualization Technology" (Intel VT-x ou AMD-V) na BIOS do seu modelo de notebook. Se travar
por mais de 1 hora, mova a issue para **Bloqueado** e conte na daily o que já tentou.
