"""Cria (ou atualiza) os labels do laboratório nos repositórios, a partir de scripts/labels.json.

Uso (precisa do gh logado):
    python scripts/criar_labels.py                    # laboratorio e radar-licitacoes
    python scripts/criar_labels.py --remover-padrao   # também apaga os labels padrão do GitHub (bug, enhancement...)
"""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

ORG = "Ponte-Informatica-Pontidata"
REPOS = ["laboratorio", "radar-licitacoes"]
PADRAO_GITHUB = [
    "bug", "documentation", "duplicate", "enhancement", "good first issue",
    "help wanted", "invalid", "question", "wontfix", "accessibility",
]


def gh(*args: str) -> str:
    return subprocess.run(["gh", *args], check=True, capture_output=True, text=True, encoding="utf-8").stdout


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--remover-padrao", action="store_true")
    ap.add_argument("--repos", nargs="*", default=REPOS)
    args = ap.parse_args()
    labels = json.loads((Path(__file__).parent / "labels.json").read_text(encoding="utf-8"))
    for repo in args.repos:
        alvo = f"{ORG}/{repo}"
        if args.remover_padrao:
            existentes = {item["name"] for item in json.loads(gh("label", "list", "-R", alvo, "--json", "name", "-L", "200"))}
            for nome in PADRAO_GITHUB:
                if nome in existentes:
                    gh("label", "delete", nome, "-R", alvo, "--yes")
        for label in labels:
            gh("label", "create", label["nome"], "-R", alvo, "--color", label["cor"],
               "--description", label["descricao"], "--force")
        print(f"{alvo}: {len(labels)} labels prontos")


if __name__ == "__main__":
    main()
