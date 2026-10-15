"""Linha de comando para publicar sprints sem passar pelo MCP.

laboratorio-publicar --sprint 1              # prévia (não altera nada)
laboratorio-publicar --sprint 1 --executar   # cria labels, milestone e issues
laboratorio-publicar --daily --executar      # cria e fixa a issue da daily
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import replace
from pathlib import Path

from laboratorio_mcp import publicacao
from laboratorio_mcp.config import Config
from laboratorio_mcp.github import GitHub


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(
        prog="laboratorio-publicar", description="Publica sprints do laboratório no GitHub"
    )
    ap.add_argument("--sprint", type=int, help="número da sprint (pasta sprints/sprint-NN)")
    ap.add_argument("--daily", action="store_true", help="garante a issue fixa da daily")
    ap.add_argument("--executar", action="store_true", help="aplica de verdade (sem isso, só mostra o plano)")
    ap.add_argument("--lab", type=Path, help="pasta do repositório laboratorio (padrão: LAB_DIR ou /lab)")
    args = ap.parse_args(argv)

    cfg = Config.do_ambiente()
    if args.lab:
        cfg = replace(cfg, diretorio_lab=args.lab)
    gh = GitHub(cfg.token, cfg.org)

    if args.daily:
        print(json.dumps(publicacao.garantir_daily(gh, cfg, args.executar), ensure_ascii=False, indent=2))
    if args.sprint is not None:
        plano = publicacao.planejar(gh, cfg, args.sprint)
        print(json.dumps(plano.resumo(), ensure_ascii=False, indent=2))
        if args.executar:
            print(json.dumps(publicacao.executar(gh, cfg, plano), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
