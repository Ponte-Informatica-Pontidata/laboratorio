from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from typing import Any

import pytest

from laboratorio_mcp.config import Config

RAIZ_LAB = Path(__file__).resolve().parents[3]


class GitHubFalso:
    """Imita o cliente GitHub em memória: issues, labels, milestones, comentários e PRs."""

    def __init__(self) -> None:
        self.org = "Org"
        self._issues: dict[str, list[dict]] = {}
        self._labels: dict[str, list[dict]] = {}
        self._milestones: dict[str, list[dict]] = {}
        self._comentarios: dict[tuple[str, int], list[dict]] = {}
        self._pulls: dict[str, list[dict]] = {}
        self._revisoes: dict[tuple[str, int], list[dict]] = {}
        self._checks: dict[str, list[dict]] = {}
        self.fixadas: list[str] = []
        self._proximo: dict[str, int] = {}

    def _numero(self, repo: str) -> int:
        self._proximo[repo] = self._proximo.get(repo, 0) + 1
        return self._proximo[repo]

    def issues(self, repo: str, **params: Any) -> list[dict]:
        itens = self._issues.get(repo, [])
        if "milestone" in params:
            itens = [i for i in itens if (i.get("milestone") or {}).get("number") == params["milestone"]]
        return list(itens)

    def criar_issue(
        self, repo: str, titulo: str, corpo: str, labels: list[str], milestone: int | None
    ) -> dict:
        numero = self._numero(repo)
        issue = {
            "number": numero,
            "title": titulo,
            "body": corpo,
            "state": "open",
            "labels": [{"name": n} for n in labels],
            "assignees": [],
            "milestone": {"number": milestone} if milestone else None,
            "html_url": f"https://github.com/Org/{repo}/issues/{numero}",
            "node_id": f"I_{repo}_{numero}",
            "created_at": "2026-10-26T12:00:00Z",
        }
        self._issues.setdefault(repo, []).append(issue)
        return issue

    def editar_issue(self, repo: str, numero: int, **campos: Any) -> dict:
        issue = next(i for i in self._issues[repo] if i["number"] == numero)
        if "body" in campos:
            issue["body"] = campos["body"]
        issue.update({k: v for k, v in campos.items() if k != "body"})
        return issue

    def fixar_issue(self, node_id: str) -> None:
        self.fixadas.append(node_id)

    def labels(self, repo: str) -> list[dict]:
        return list(self._labels.get(repo, []))

    def criar_label(self, repo: str, nome: str, cor: str, descricao: str) -> dict:
        label = {"name": nome, "color": cor, "description": descricao}
        self._labels.setdefault(repo, []).append(label)
        return label

    def milestones(self, repo: str) -> list[dict]:
        return list(self._milestones.get(repo, []))

    def criar_milestone(self, repo: str, titulo: str, descricao: str, prazo_iso: str) -> dict:
        milestone = {"number": len(self._milestones.get(repo, [])) + 1, "title": titulo, "due_on": prazo_iso}
        self._milestones.setdefault(repo, []).append(milestone)
        return milestone

    def comentarios(self, repo: str, numero: int, desde: str | None = None) -> list[dict]:
        return [c for c in self._comentarios.get((repo, numero), []) if not desde or c["created_at"] >= desde]

    def pulls(self, repo: str, estado: str = "open") -> list[dict]:
        return [p for p in self._pulls.get(repo, []) if p["state"] == estado]

    def revisoes(self, repo: str, numero: int) -> list[dict]:
        return self._revisoes.get((repo, numero), [])

    def checks(self, repo: str, sha: str) -> list[dict]:
        return self._checks.get(sha, [])

    def status_no_quadro(self, numero_projeto: int) -> dict:
        return {}


@pytest.fixture
def gh() -> GitHubFalso:
    return GitHubFalso()


@pytest.fixture
def cfg() -> Config:
    return replace(Config(token="x"), org="Org", diretorio_lab=RAIZ_LAB, tech_lead="techlead")
