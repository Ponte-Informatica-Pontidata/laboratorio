"""Cliente mínimo da API do GitHub (REST + GraphQL) usado pelas ferramentas do laboratório."""

from __future__ import annotations

from typing import Any

import httpx

API = "https://api.github.com"


class ErroGitHub(RuntimeError):
    pass


class GitHub:
    def __init__(self, token: str, org: str, http: httpx.Client | None = None) -> None:
        if not token and http is None:
            raise ErroGitHub("Sem token: defina GITHUB_PERSONAL_ACCESS_TOKEN em gestao/.env")
        self.org = org
        self.http = http or httpx.Client(
            base_url=API,
            timeout=30.0,
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "laboratorio-mcp",
            },
        )

    # -- básico -------------------------------------------------------------------
    def _req(self, metodo: str, caminho: str, **kwargs: Any) -> Any:
        resposta = self.http.request(metodo, caminho, **kwargs)
        if resposta.status_code >= 400:
            raise ErroGitHub(f"{metodo} {caminho}: HTTP {resposta.status_code} {resposta.text[:300]}")
        return resposta.json() if resposta.content else None

    def _paginado(self, caminho: str, params: dict[str, Any] | None = None) -> list[dict]:
        itens: list[dict] = []
        pagina = 1
        while True:
            lote = self._req("GET", caminho, params={**(params or {}), "per_page": 100, "page": pagina})
            itens.extend(lote)
            if len(lote) < 100:
                return itens
            pagina += 1

    def graphql(self, consulta: str, variaveis: dict[str, Any] | None = None) -> dict:
        dados = self._req("POST", "/graphql", json={"query": consulta, "variables": variaveis or {}})
        if dados.get("errors"):
            raise ErroGitHub(f"GraphQL: {dados['errors']}")
        return dados["data"]

    def _repo(self, repo: str) -> str:
        return f"/repos/{self.org}/{repo}"

    # -- issues ---------------------------------------------------------------------
    def issues(self, repo: str, **params: Any) -> list[dict]:
        """Issues (sem PRs) do repositório. Ex.: issues("radar-licitacoes", state="all", milestone=3)."""
        params.setdefault("state", "all")
        return [i for i in self._paginado(f"{self._repo(repo)}/issues", params) if "pull_request" not in i]

    def criar_issue(
        self, repo: str, titulo: str, corpo: str, labels: list[str], milestone: int | None
    ) -> dict:
        dados: dict[str, Any] = {"title": titulo, "body": corpo, "labels": labels}
        if milestone is not None:
            dados["milestone"] = milestone
        return self._req("POST", f"{self._repo(repo)}/issues", json=dados)

    def editar_issue(self, repo: str, numero: int, **campos: Any) -> dict:
        return self._req("PATCH", f"{self._repo(repo)}/issues/{numero}", json=campos)

    def comentarios(self, repo: str, numero: int, desde: str | None = None) -> list[dict]:
        params = {"since": desde} if desde else {}
        return self._paginado(f"{self._repo(repo)}/issues/{numero}/comments", params)

    def fixar_issue(self, node_id: str) -> None:
        self.graphql(
            "mutation($id: ID!) { pinIssue(input: {issueId: $id}) { issue { number } } }", {"id": node_id}
        )

    # -- milestones e labels ------------------------------------------------------------
    def milestones(self, repo: str) -> list[dict]:
        return self._paginado(f"{self._repo(repo)}/milestones", {"state": "all"})

    def criar_milestone(self, repo: str, titulo: str, descricao: str, prazo_iso: str) -> dict:
        return self._req(
            "POST",
            f"{self._repo(repo)}/milestones",
            json={"title": titulo, "description": descricao, "due_on": prazo_iso},
        )

    def labels(self, repo: str) -> list[dict]:
        return self._paginado(f"{self._repo(repo)}/labels")

    def criar_label(self, repo: str, nome: str, cor: str, descricao: str) -> dict:
        return self._req(
            "POST", f"{self._repo(repo)}/labels", json={"name": nome, "color": cor, "description": descricao}
        )

    # -- pull requests ----------------------------------------------------------------
    def pulls(self, repo: str, estado: str = "open") -> list[dict]:
        return self._paginado(f"{self._repo(repo)}/pulls", {"state": estado})

    def revisoes(self, repo: str, numero: int) -> list[dict]:
        return self._paginado(f"{self._repo(repo)}/pulls/{numero}/reviews")

    def checks(self, repo: str, sha: str) -> list[dict]:
        dados = self._req("GET", f"{self._repo(repo)}/commits/{sha}/check-runs", params={"per_page": 100})
        return dados.get("check_runs", [])

    # -- projects (precisa de permissão de Projects no token) ---------------------------------
    def status_no_quadro(self, numero_projeto: int) -> dict[tuple[str, int], str]:
        consulta = """
        query($org: String!, $n: Int!, $cursor: String) {
          organization(login: $org) {
            projectV2(number: $n) {
              items(first: 100, after: $cursor) {
                pageInfo { hasNextPage endCursor }
                nodes {
                  content { ... on Issue { number repository { name } } }
                  fieldValueByName(name: "Status") { ... on ProjectV2ItemFieldSingleSelectValue { name } }
                }
              }
            }
          }
        }"""
        status: dict[tuple[str, int], str] = {}
        cursor = None
        while True:
            dados = self.graphql(consulta, {"org": self.org, "n": numero_projeto, "cursor": cursor})
            itens = dados["organization"]["projectV2"]["items"]
            for no in itens["nodes"]:
                conteudo = no.get("content") or {}
                valor = no.get("fieldValueByName") or {}
                if conteudo.get("number") and valor.get("name"):
                    status[(conteudo["repository"]["name"], conteudo["number"])] = valor["name"]
            if not itens["pageInfo"]["hasNextPage"]:
                return status
            cursor = itens["pageInfo"]["endCursor"]
