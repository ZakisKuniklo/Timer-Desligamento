"""Ponto de entrada CLI e grafico do aplicativo Timer-Desligamento."""

from __future__ import annotations

import argparse
import logging
import sys
import tkinter as tk
from pathlib import Path

CODE_DIR = Path(__file__).resolve().parent
if str(CODE_DIR) not in sys.path:
    sys.path.insert(0, str(CODE_DIR))

from timer_app.os_executor import detect_os  # noqa: E402
from timer_app.ui.app_window import TimerShutdownApp  # noqa: E402


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Interpreta os argumentos de linha de comando."""
    parser = argparse.ArgumentParser(
        prog="timer-desligamento",
        description=(
            "Aplicativo de contagem regressiva para desligar, reiniciar "
            "ou encerrar a sessao no Windows ou Linux."
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simula o disparo final sem executar desligamento/reinicio/logoff.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Ativa logs detalhados no terminal.",
    )
    return parser.parse_args(argv)


def configure_logging(verbose: bool) -> None:
    """Configura o nivel e o formato padrao de logging."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )


def main(argv: list[str] | None = None) -> int:
    """Inicializa a interface grafica e executa o loop principal."""
    args = parse_args(argv)
    configure_logging(args.verbose)

    os_type = detect_os()
    logging.getLogger(__name__).info(
        "Iniciando Timer-Desligamento (SO=%s, dry_run=%s)",
        os_type.value,
        args.dry_run,
    )

    root = tk.Tk()
    app = TimerShutdownApp(root, os_type=os_type, dry_run=args.dry_run)
    app.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
