# Onboarding — Sprint 0

Bem-vinda! Esta primeira semana tem um objetivo só: **deixar seu ambiente funcionando, entender o
projeto e fazer o primeiro Pull Request.** Siga a ordem abaixo e registre o progresso na daily.

## 1. Contas (issue S0-01)

- [ ] Conta no GitHub com **autenticação em dois fatores (2FA)** ligada.
- [ ] Convite da organização `Ponte-Informatica-Pontidata` aceito (chega por e-mail).
- [ ] Notificações do GitHub configuradas para você ver menções (@) e revisões.

## 2. Ferramentas (issue S0-01)

| Ferramenta | Para quê | Observação |
|---|---|---|
| Git | versionar código | No Windows, o Git for Windows já traz o Git Bash |
| Docker Desktop | rodar banco, app e testes em containers | No Windows, ative o WSL2 quando o instalador pedir |
| VS Code | editar código | Abra o projeto e aceite as extensões recomendadas |

Teste no terminal (PowerShell ou bash):

```bash
git --version
docker version
docker compose version
```

> **Windows:** se o Docker reclamar de virtualização, ative "Virtualização" na BIOS e o recurso
> "Plataforma de Máquina Virtual" do Windows. Se travar por mais de 1 hora, mova a issue para
> **Bloqueado** e avise na daily.

## 3. Subir o Radar (issue S0-02)

```bash
git clone https://github.com/Ponte-Informatica-Pontidata/radar-licitacoes.git
cd radar-licitacoes
docker compose up -d --build
```

A primeira vez demora alguns minutos (download das imagens). No fim, abra http://localhost:8501:
o app vai avisar que **o banco está vazio**. Isso é esperado e fica resolvido no próximo passo.

## 4. Criar o banco e carregar a base real (issue S0-03)

Aqui você é a **executora**: os scripts já estão prontos e o seu trabalho é rodar, entender e conferir.

```bash
docker compose run --rm dev bash banco/migrar.sh                      # DDL: cria schemas e tabelas
docker compose run --rm dev psql -f banco/carga/01_staging.sql        # CSV -> staging
docker compose run --rm dev psql -f banco/carga/02_transformar.sql    # staging -> radar
docker compose run --rm dev psql -f banco/carga/03_validar.sql        # confere com o MANIFESTO
```

Antes de cada comando, **abra o arquivo e leia**. O que cada passo faz está explicado em
`banco/README.md`. Depois atualize o app (http://localhost:8501) e veja as licitações abertas de MG.

## 5. Rodar os testes

```bash
docker compose run --rm dev pytest
```

Você vai ver `passed` (testes que já passam) e `xfailed` (testes que **esperam por você**). O resumo no
fim lista as tarefas pendentes por issue. Isso é normal: são as suas próximas tarefas.

## 6. Ler a arquitetura (issue S0-04)

Leia `docs/arquitetura.md` e os ADRs em `docs/adr/` no repositório do Radar. Depois responda o quiz na issue.

## 7. Primeiro Pull Request (issue S0-05)

O fluxo que você vai repetir o laboratório inteiro:

```bash
git switch -c docs/<numero-da-issue>-dicionario-itens     # 1. branch a partir da main atualizada
# ... edite os arquivos ...
docker compose run --rm dev pytest                         # 2. testes passando
git add dados/DICIONARIO.md tests/unit/test_dicionario.py
git commit -m "docs: completa o dicionário de contratacao_item"   # 3. Conventional Commits
git push -u origin docs/<numero-da-issue>-dicionario-itens        # 4. envia a branch
```

5. Abra o Pull Request no GitHub, preencha o template (inclusive **Uso de IA** e **Explique com suas
   palavras**) e escreva `Closes #<numero>` na descrição.
6. Espere o CI ficar verde e a revisão do tech lead. Responda os comentários com commits novos na mesma branch.
7. Depois da aprovação, o merge é feito com **squash**.

## 8. Daily assíncrona

Todo dia de trabalho, comente na issue fixada **"Daily assíncrona"** do repositório `laboratorio`:

```markdown
**Fiz:** ...
**Vou fazer:** ...
**Bloqueios:** nenhum | <o que está travando e o que já tentou>
```

Curto e honesto. Bloqueio não é falha: esconder bloqueio é.
