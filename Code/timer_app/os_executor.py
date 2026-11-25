"""Deteccao do sistema operacional, validacao e execucao segura dos scripts."""

from __future__ import annotations

import logging
import platform
import subprocess
from pathlib import Path

from timer_app.config import SCRIPT_FILENAMES
from timer_app.models import ExecutionResult, OperatingSystem, PowerAction

logger = logging.getLogger(__name__)


def detect_os() -> OperatingSystem:
    """Identifica o sistema operacional atual via platform.system()."""
    system_name = platform.system()
    if system_name == "Windows":
        return OperatingSystem.WINDOWS
    if system_name == "Linux":
        return OperatingSystem.LINUX
    return OperatingSystem.UNSUPPORTED


def get_scripts_base_dir() -> Path:
    """Retorna o diretorio raiz Code/scripts relativo a localizacao do pacote."""
    return Path(__file__).resolve().parent.parent / "scripts"


def resolve_script_path(
    action: PowerAction,
    os_type: OperatingSystem,
    base_dir: Path | None = None,
) -> Path:
    """Resolve o caminho completo do script correspondente ao SO e a acao."""
    if os_type == OperatingSystem.UNSUPPORTED or os_type not in SCRIPT_FILENAMES:
        raise ValueError(
            "Sistema operacional nao suportado. Apenas Windows e Linux sao suportados."
        )
    scripts_root = base_dir if base_dir is not None else get_scripts_base_dir()
    relative_script = SCRIPT_FILENAMES[os_type][action]
    return scripts_root / relative_script


def validate_scripts(
    os_type: OperatingSystem,
    base_dir: Path | None = None,
) -> list[Path]:
    """Verifica se todos os scripts esperados para o SO existem; retorna os ausentes."""
    if os_type == OperatingSystem.UNSUPPORTED or os_type not in SCRIPT_FILENAMES:
        return []
    missing: list[Path] = []
    for action in PowerAction:
        script_path = resolve_script_path(action, os_type, base_dir=base_dir)
        if not script_path.is_file():
            missing.append(script_path)
    return missing


def build_command(script_path: Path, os_type: OperatingSystem) -> list[str]:
    """Monta a lista de argumentos de invocacao para subprocess.run()."""
    if os_type == OperatingSystem.WINDOWS:
        return [str(script_path)]
    if os_type == OperatingSystem.LINUX:
        return ["bash", str(script_path)]
    raise ValueError(f"Sistema operacional nao suportado para comando: {os_type}")


def execute_power_action(
    action: PowerAction,
    os_type: OperatingSystem | None = None,
    dry_run: bool = False,
    base_dir: Path | None = None,
) -> ExecutionResult:
    """Valida e executa (ou simula via dry_run) a acao de energia no SO."""
    resolved_os = os_type if os_type is not None else detect_os()

    try:
        script_path = resolve_script_path(action, resolved_os, base_dir=base_dir)
    except ValueError as exc:
        logger.error("Erro de SO nao suportado ao resolver script: %s", exc)
        return ExecutionResult(
            success=False,
            os_type=resolved_os,
            action=action,
            script_path=None,
            command=[],
            dry_run=dry_run,
            error_message=str(exc),
        )

    if not script_path.is_file():
        message = f"Script de acao nao encontrado: {script_path}"
        logger.error(message)
        return ExecutionResult(
            success=False,
            os_type=resolved_os,
            action=action,
            script_path=script_path,
            command=[],
            dry_run=dry_run,
            error_message=message,
        )

    command = build_command(script_path, resolved_os)

    if dry_run:
        logger.info(
            "[DRY-RUN] Simulando acao '%s' em %s com comando: %s",
            action.value,
            resolved_os.value,
            command,
        )
        return ExecutionResult(
            success=True,
            os_type=resolved_os,
            action=action,
            script_path=script_path,
            command=command,
            returncode=0,
            dry_run=True,
        )

    run_kwargs: dict[str, object] = {
        "capture_output": True,
        "text": True,
        "check": False,
    }
    if resolved_os == OperatingSystem.WINDOWS:
        run_kwargs["creationflags"] = getattr(subprocess, "CREATE_NO_WINDOW", 0)

    logger.info(
        "Executando acao '%s' em %s: %s",
        action.value,
        resolved_os.value,
        command,
    )

    try:
        completed = subprocess.run(command, **run_kwargs)
    except (FileNotFoundError, PermissionError, subprocess.SubprocessError, OSError) as exc:
        message = f"Falha ao executar o script '{script_path}': {exc}"
        logger.exception(message)
        return ExecutionResult(
            success=False,
            os_type=resolved_os,
            action=action,
            script_path=script_path,
            command=command,
            dry_run=False,
            error_message=message,
        )

    stdout = completed.stdout or ""
    stderr = completed.stderr or ""

    if completed.returncode == 0:
        logger.info("Script concluido com sucesso (codigo 0).")
        return ExecutionResult(
            success=True,
            os_type=resolved_os,
            action=action,
            script_path=script_path,
            command=command,
            returncode=0,
            stdout=stdout,
            stderr=stderr,
            dry_run=False,
        )

    details = stderr.strip() or stdout.strip() or "Sem detalhes adicionais."
    message = (
        f"O script '{script_path.name}' retornou erro (codigo {completed.returncode}).\n"
        f"Detalhes: {details}"
    )
    logger.error(message)
    return ExecutionResult(
        success=False,
        os_type=resolved_os,
        action=action,
        script_path=script_path,
        command=command,
        returncode=completed.returncode,
        stdout=stdout,
        stderr=stderr,
        dry_run=False,
        error_message=message,
    )
