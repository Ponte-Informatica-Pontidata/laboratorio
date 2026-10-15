# MCP do laboratório (stdio). Usado pelo Claude Code via docker compose (ver ../docker-compose.yml).
FROM python:3.13.13-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    PATH="/opt/venv/bin:${PATH}" \
    TZ=America/Sao_Paulo

COPY --from=ghcr.io/astral-sh/uv:0.13.1 /uv /uvx /usr/local/bin/

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project
COPY src ./src
RUN uv sync --frozen --no-dev

# O repositório laboratorio é montado em /lab (somente leitura): roadmap.yml, sprints/ e templates/
ENV LAB_DIR=/lab
ENTRYPOINT ["laboratorio-mcp"]
