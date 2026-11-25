"""Testes de fluxo de estados e integracao UI/controlador com mocks seguros."""

from __future__ import annotations

import sys
import tkinter as tk
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

CODE_DIR = Path(__file__).resolve().parent.parent
if str(CODE_DIR) not in sys.path:
    sys.path.insert(0, str(CODE_DIR))

from timer_app.models import (  # noqa: E402
    AppScreen,
    ExecutionResult,
    OperatingSystem,
    PowerAction,
    TimerState,
)
from timer_app.ui.app_window import TimerShutdownApp  # noqa: E402


class TestAppFlow(unittest.TestCase):
    """Valida UC02 a UC11 na maquina de estados de TimerShutdownApp."""

    def setUp(self) -> None:
        try:
            self.root = tk.Tk()
        except tk.TclError as exc:
            self.skipTest(f"Tkinter sem display disponivel neste ambiente: {exc}")
        self.root.withdraw()
        self.app = TimerShutdownApp(
            self.root,
            os_type=OperatingSystem.WINDOWS,
            dry_run=True,
            check_env_on_startup=False,
        )

    def tearDown(self) -> None:
        if hasattr(self, "app"):
            self.app.on_window_close()

    def test_initial_state(self) -> None:
        self.assertEqual(self.app.digits, "000000")
        self.assertEqual(self.app.selected_action, PowerAction.DESLIGAR)
        self.assertEqual(self.app.current_screen, AppScreen.SETUP)
        self.assertEqual(self.app.timer_state, TimerState.IDLE)

    def test_digit_input_backspace_and_escape_clear(self) -> None:
        self.app.on_digit_input("5")
        self.app.on_digit_input("00")
        self.assertEqual(self.app.digits, "000500")

        self.app.on_backspace()
        self.assertEqual(self.app.digits, "000050")

        self.app.on_key_press(SimpleNamespace(char="", keysym="Escape"))
        self.assertEqual(self.app.digits, "000000")

    def test_preset_fills_display_without_starting(self) -> None:
        self.app.on_preset_selected(5)
        self.assertEqual(self.app.digits, "000500")
        self.assertEqual(self.app.current_screen, AppScreen.SETUP)
        self.assertEqual(self.app.timer_state, TimerState.IDLE)

    def test_start_with_zero_stays_on_setup(self) -> None:
        with mock.patch.object(self.app.setup_view, "flash_zero_warning") as mock_flash:
            self.app.on_start_clicked()
            mock_flash.assert_called_once()
        self.assertEqual(self.app.current_screen, AppScreen.SETUP)
        self.assertEqual(self.app.timer_state, TimerState.IDLE)

    def test_start_pause_resume_and_cancel_preserves_state(self) -> None:
        self.app.on_action_selected(PowerAction.REINICIAR)
        self.app.on_digit_input("9")
        self.app.on_digit_input("0")
        self.assertEqual(self.app.digits, "000090")

        self.app.on_key_press(SimpleNamespace(char="\r", keysym="Return"))
        self.assertEqual(self.app.current_screen, AppScreen.COUNTDOWN)
        self.assertEqual(self.app.timer_state, TimerState.RUNNING)
        self.assertEqual(self.app.total_seconds, 90)

        # Pausa via barra de espaco
        self.app.on_key_press(SimpleNamespace(char=" ", keysym="space"))
        self.assertEqual(self.app.timer_state, TimerState.PAUSED)
        self.assertIsNone(self.app._after_id)

        # Retoma via on_toggle_pause
        self.app.on_toggle_pause()
        self.assertEqual(self.app.timer_state, TimerState.RUNNING)
        self.assertIsNotNone(self.app._after_id)

        # Cancela via Esc na Tela 2 e verifica preservacao do tempo e da acao
        self.app.on_key_press(SimpleNamespace(char="", keysym="Escape"))
        self.assertEqual(self.app.current_screen, AppScreen.SETUP)
        self.assertEqual(self.app.timer_state, TimerState.IDLE)
        self.assertIsNone(self.app._after_id)
        self.assertEqual(self.app.digits, "000090")
        self.assertEqual(self.app.selected_action, PowerAction.REINICIAR)

    def test_timer_finish_dry_run_shows_info_and_returns_to_setup(self) -> None:
        self.app.on_preset_selected(1)
        self.app.on_start_clicked()

        fake_result = ExecutionResult(
            success=True,
            os_type=OperatingSystem.WINDOWS,
            action=PowerAction.DESLIGAR,
            script_path=Path("Code/scripts/win/desligar.bat"),
            command=["Code/scripts/win/desligar.bat"],
            returncode=0,
            dry_run=True,
        )

        with (
            mock.patch(
                "timer_app.ui.app_window.execute_power_action",
                return_value=fake_result,
            ) as mock_exec,
            mock.patch("timer_app.ui.app_window.messagebox.showinfo") as mock_info,
        ):
            self.app.end_monotonic = 0.0
            with mock.patch("timer_app.ui.app_window.time.monotonic", return_value=10.0):
                self.app._tick()

            mock_exec.assert_called_once_with(
                PowerAction.DESLIGAR,
                os_type=OperatingSystem.WINDOWS,
                dry_run=True,
            )
            mock_info.assert_called_once()
            self.assertEqual(self.app.current_screen, AppScreen.SETUP)
            self.assertEqual(self.app.timer_state, TimerState.IDLE)

    def test_timer_finish_real_success_closes_window(self) -> None:
        self.app.dry_run = False
        self.app.on_preset_selected(1)
        self.app.on_start_clicked()

        fake_result = ExecutionResult(
            success=True,
            os_type=OperatingSystem.WINDOWS,
            action=PowerAction.DESLIGAR,
            script_path=Path("Code/scripts/win/desligar.bat"),
            command=["Code/scripts/win/desligar.bat"],
            returncode=0,
            dry_run=False,
        )

        with mock.patch(
            "timer_app.ui.app_window.execute_power_action",
            return_value=fake_result,
        ):
            self.app._handle_timer_finished()

        self.assertTrue(self.app._is_closed)

    def test_timer_finish_error_shows_alert_and_returns_to_setup(self) -> None:
        self.app.dry_run = False
        self.app.on_preset_selected(1)
        self.app.on_start_clicked()

        fake_error = ExecutionResult(
            success=False,
            os_type=OperatingSystem.LINUX,
            action=PowerAction.DESLIGAR,
            script_path=Path("Code/scripts/linux/desligar.sh"),
            command=["bash", "Code/scripts/linux/desligar.sh"],
            returncode=1,
            stderr="Permission denied",
            error_message="Falha de permissao",
        )

        with (
            mock.patch(
                "timer_app.ui.app_window.execute_power_action",
                return_value=fake_error,
            ),
            mock.patch("timer_app.ui.app_window.messagebox.showerror") as mock_err,
        ):
            self.app._handle_timer_finished()

        mock_err.assert_called_once()
        self.assertFalse(self.app._is_closed)
        self.assertEqual(self.app.current_screen, AppScreen.SETUP)


if __name__ == "__main__":
    unittest.main()
