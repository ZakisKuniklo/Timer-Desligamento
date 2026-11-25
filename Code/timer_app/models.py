"""Modelos de dominio e contratos compartilhados do Timer-Desligamento."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class PowerAction(str, Enum):
    """Acao de energia executada ao termino da contagem regressiva."""

    DESLIGAR = "desligar"
    REINICIAR = "reiniciar"
    LOGOFF = "logoff"


class OperatingSystem(str, Enum):
    """Sistema operacional detectado em tempo de execucao."""

    WINDOWS = "Windows"
    LINUX = "Linux"
    UNSUPPORTED = "Unsupported"


class AppScreen(str, Enum):
    """Telas principais da interface grafica."""

    SETUP = "setup"
    COUNTDOWN = "countdown"


class TimerState(str, Enum):
    """Estados da maquina de estados do temporizador."""

    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    FINISHED = "finished"


@dataclass(frozen=True)
class ExecutionResult:
    """Resultado estruturado da tentativa de execucao de um script de energia."""

    success: bool
    os_type: OperatingSystem
    action: PowerAction
    script_path: Path | None
    command: list[str]
    returncode: int | None = None
    stdout: str = ""
    stderr: str = ""
    dry_run: bool = False
    error_message: str = ""
