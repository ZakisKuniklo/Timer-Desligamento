"""Testes unitarios seguros para deteccao de SO, scripts e os_executor."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

CODE_DIR = Path(__file__).resolve().parent.parent
if str(CODE_DIR) not in sys.path:
    sys.path.insert(0, str(CODE_DIR))

from timer_app.models import OperatingSystem, PowerAction  # noqa: E402
from timer_app.os_executor import (  # noqa: E402
    build_command,
    detect_os,
    execute_power_action,
    get_scripts_base_dir,
    resolve_script_path,
    validate_scripts,
)


class TestOsExecutor(unittest.TestCase):
    """Valida scripts .bat/.sh e execucao com mocks sem disparar acoes reais."""

    def test_detect_os(self) -> None:
        with mock.patch("timer_app.os_executor.platform.system", return_value="Windows"):
            self.assertEqual(detect_os(), OperatingSystem.WINDOWS)
        with mock.patch("timer_app.os_executor.platform.system", return_value="Linux"):
            self.assertEqual(detect_os(), OperatingSystem.LINUX)
        with mock.patch("timer_app.os_executor.platform.system", return_value="Darwin"):
            self.assertEqual(detect_os(), OperatingSystem.UNSUPPORTED)

    def test_all_scripts_exist_and_have_valid_line_endings_and_commands(self) -> None:
        base_dir = get_scripts_base_dir()
        self.assertEqual(validate_scripts(OperatingSystem.WINDOWS, base_dir=base_dir), [])
        self.assertEqual(validate_scripts(OperatingSystem.LINUX, base_dir=base_dir), [])

        expected_bat = {
            PowerAction.DESLIGAR: "shutdown /s /f /t 0",
            PowerAction.REINICIAR: "shutdown /r /f /t 0",
            PowerAction.LOGOFF: "shutdown /l",
        }
        for action, expected_cmd in expected_bat.items():
            bat_path = resolve_script_path(action, OperatingSystem.WINDOWS, base_dir)
            raw = bat_path.read_bytes()
            self.assertFalse(raw.startswith(b"\xef\xbb\xbf"), f"{bat_path} tem BOM UTF-8")
            self.assertIn(b"\r\n", raw, f"{bat_path} deve usar CRLF")
            # Nenhuma quebra LF isolada sem CR antes
            self.assertEqual(raw.replace(b"\r\n", b"").count(b"\n"), 0)
            text = raw.decode("utf-8")
            self.assertIn("@echo off", text)
            self.assertIn(expected_cmd, text)
            if action == PowerAction.LOGOFF:
                self.assertNotIn("/t", text)
                self.assertNotIn("/f", text)

        for action in PowerAction:
            sh_path = resolve_script_path(action, OperatingSystem.LINUX, base_dir)
            raw = sh_path.read_bytes()
            self.assertFalse(raw.startswith(b"\xef\xbb\xbf"), f"{sh_path} tem BOM UTF-8")
            self.assertNotIn(b"\r", raw, f"{sh_path} nao deve conter CR")
            text = raw.decode("utf-8")
            self.assertTrue(text.startswith("#!/usr/bin/env bash\n"))
            self.assertIn("set -euo pipefail", text)

    def test_validate_scripts_reports_missing_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            missing = validate_scripts(OperatingSystem.WINDOWS, base_dir=Path(tmp))
            self.assertEqual(len(missing), 3)

    def test_build_command(self) -> None:
        win_path = Path("C:/scripts/win/desligar.bat")
        lin_path = Path("/scripts/linux/desligar.sh")
        self.assertEqual(build_command(win_path, OperatingSystem.WINDOWS), [str(win_path)])
        self.assertEqual(
            build_command(lin_path, OperatingSystem.LINUX),
            ["bash", str(lin_path)],
        )
        with self.assertRaises(ValueError):
            build_command(win_path, OperatingSystem.UNSUPPORTED)

    def test_execute_power_action_dry_run_never_calls_subprocess(self) -> None:
        with mock.patch("timer_app.os_executor.subprocess.run") as mock_run:
            result = execute_power_action(
                PowerAction.DESLIGAR,
                os_type=OperatingSystem.WINDOWS,
                dry_run=True,
            )
            mock_run.assert_not_called()
            self.assertTrue(result.success)
            self.assertTrue(result.dry_run)
            self.assertEqual(result.returncode, 0)
            self.assertIsNotNone(result.script_path)
            self.assertEqual(result.command, [str(result.script_path)])

    def test_execute_power_action_windows_mocked(self) -> None:
        completed = subprocess.CompletedProcess(
            args=["desligar.bat"],
            returncode=0,
            stdout="",
            stderr="",
        )
        with mock.patch(
            "timer_app.os_executor.subprocess.run",
            return_value=completed,
        ) as mock_run:
            result = execute_power_action(
                PowerAction.DESLIGAR,
                os_type=OperatingSystem.WINDOWS,
                dry_run=False,
            )
            self.assertTrue(result.success)
            self.assertFalse(result.dry_run)
            mock_run.assert_called_once()
            _, kwargs = mock_run.call_args
            self.assertEqual(
                kwargs.get("creationflags"),
                getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )

    def test_execute_power_action_linux_mocked_success_and_failure(self) -> None:
        ok_proc = subprocess.CompletedProcess(
            args=["bash", "reiniciar.sh"],
            returncode=0,
            stdout="",
            stderr="",
        )
        with mock.patch(
            "timer_app.os_executor.subprocess.run",
            return_value=ok_proc,
        ) as mock_run:
            result = execute_power_action(
                PowerAction.REINICIAR,
                os_type=OperatingSystem.LINUX,
                dry_run=False,
            )
            self.assertTrue(result.success)
            args, kwargs = mock_run.call_args
            self.assertEqual(args[0][0], "bash")
            self.assertNotIn("creationflags", kwargs)

        fail_proc = subprocess.CompletedProcess(
            args=["bash", "desligar.sh"],
            returncode=1,
            stdout="",
            stderr="Interactive authentication required.",
        )
        with mock.patch(
            "timer_app.os_executor.subprocess.run",
            return_value=fail_proc,
        ):
            result = execute_power_action(
                PowerAction.DESLIGAR,
                os_type=OperatingSystem.LINUX,
                dry_run=False,
            )
            self.assertFalse(result.success)
            self.assertEqual(result.returncode, 1)
            self.assertIn("Interactive authentication required.", result.error_message)

    def test_execute_power_action_handles_missing_script_and_unsupported_os(self) -> None:
        res_unsupported = execute_power_action(
            PowerAction.DESLIGAR,
            os_type=OperatingSystem.UNSUPPORTED,
            dry_run=False,
        )
        self.assertFalse(res_unsupported.success)
        self.assertIsNone(res_unsupported.script_path)

        with tempfile.TemporaryDirectory() as tmp:
            res_missing = execute_power_action(
                PowerAction.LOGOFF,
                os_type=OperatingSystem.WINDOWS,
                dry_run=False,
                base_dir=Path(tmp),
            )
            self.assertFalse(res_missing.success)
            self.assertIn("nao encontrado", res_missing.error_message)

    def test_execute_power_action_handles_oserror(self) -> None:
        with mock.patch(
            "timer_app.os_executor.subprocess.run",
            side_effect=PermissionError("Permissao negada"),
        ):
            result = execute_power_action(
                PowerAction.LOGOFF,
                os_type=OperatingSystem.LINUX,
                dry_run=False,
            )
            self.assertFalse(result.success)
            self.assertIn("Permissao negada", result.error_message)


if __name__ == "__main__":
    unittest.main()
