"""Orquestrador principal da janela, estado do timer e loop temporal."""

from __future__ import annotations

import logging
import time
import tkinter as tk
from tkinter import messagebox

from timer_app.config import APP_TITLE, Colors, Dimensions, get_font_family
from timer_app.models import AppScreen, OperatingSystem, PowerAction, TimerState
from timer_app.os_executor import execute_power_action, validate_scripts
from timer_app.time_utils import (
    DEFAULT_DIGITS,
    calculate_progress_extent,
    digits_to_total_seconds,
    format_countdown,
    format_header_title,
    pop_digit,
    preset_to_digits,
    push_digit,
)
from timer_app.ui.countdown_view import CountdownView
from timer_app.ui.setup_view import SetupView

logger = logging.getLogger(__name__)


class TimerShutdownApp:
    """Controlador principal do aplicativo Timer de Desligamento."""

    def __init__(
        self,
        root: tk.Tk,
        os_type: OperatingSystem,
        dry_run: bool = False,
        check_env_on_startup: bool = True,
    ) -> None:
        self.root = root
        self.os_type = os_type
        self.dry_run = dry_run

        self.digits: str = DEFAULT_DIGITS
        self.selected_action: PowerAction = PowerAction.DESLIGAR
        self.current_screen: AppScreen = AppScreen.SETUP
        self.timer_state: TimerState = TimerState.IDLE
        self.total_seconds: int = 0
        self.remaining_seconds: float = 0.0
        self.end_monotonic: float | None = None
        self._after_id: str | None = None
        self._startup_after_id: str | None = None
        self._is_closed = False

        self._configure_window()
        font_family = get_font_family(self.os_type)

        self.container = tk.Frame(self.root, bg=Colors.BG_SETUP)
        self.container.pack(fill=tk.BOTH, expand=True)

        self.setup_view = SetupView(
            self.container,
            font_family=font_family,
            on_digit=self.on_digit_input,
            on_backspace=self.on_backspace,
            on_preset=self.on_preset_selected,
            on_action_change=self.on_action_selected,
            on_start=self.on_start_clicked,
        )
        self.countdown_view = CountdownView(
            self.container,
            font_family=font_family,
            on_toggle_pause=self.on_toggle_pause,
            on_cancel=self.on_cancel_clicked,
        )

        self._show_screen(AppScreen.SETUP)
        self.root.bind("<Key>", self.on_key_press)
        self.root.protocol("WM_DELETE_WINDOW", self.on_window_close)

        if check_env_on_startup:
            self._startup_after_id = self.root.after(
                0, self._check_environment_on_startup
            )

    def _configure_window(self) -> None:
        self.root.title(APP_TITLE)
        self.root.configure(bg=Colors.BG_SETUP)
        self.root.resizable(False, False)

        self.root.update_idletasks()
        width = Dimensions.WINDOW_WIDTH
        height = Dimensions.WINDOW_HEIGHT
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        pos_x = max(0, (screen_w - width) // 2)
        pos_y = max(0, (screen_h - height) // 2)
        self.root.geometry(f"{width}x{height}+{pos_x}+{pos_y}")

    def _check_environment_on_startup(self) -> None:
        self._startup_after_id = None
        if self._is_closed:
            return

        if self.os_type == OperatingSystem.UNSUPPORTED:
            msg = (
                "Sistema operacional nao suportado.\n"
                "O Timer de Desligamento suporta apenas Windows e Linux."
            )
            if self.dry_run:
                msg += "\n\nExecutando em modo --dry-run apenas para testes visuais."
            messagebox.showwarning(APP_TITLE, msg)
            return

        missing = validate_scripts(self.os_type)
        if missing:
            paths_text = "\n".join(f"- {path}" for path in missing)
            messagebox.showwarning(
                APP_TITLE,
                "Alguns scripts de energia nao foram encontrados:\n\n"
                f"{paths_text}",
            )

    def run(self) -> None:
        """Inicia o loop principal da interface grafica."""
        self.root.mainloop()

    def on_digit_input(self, token: str) -> None:
        """Insere digito(s) no visor de configuracao."""
        if self.current_screen != AppScreen.SETUP:
            return
        self.digits = push_digit(self.digits, token)
        self._refresh_setup_display()

    def on_backspace(self) -> None:
        """Remove o digito mais a direita do visor."""
        if self.current_screen != AppScreen.SETUP:
            return
        self.digits = pop_digit(self.digits)
        self._refresh_setup_display()

    def on_clear_digits(self) -> None:
        """Limpa o visor de volta para 00 00 00."""
        if self.current_screen != AppScreen.SETUP:
            return
        self.digits = DEFAULT_DIGITS
        self._refresh_setup_display()

    def on_preset_selected(self, minutes: int) -> None:
        """Preenche o visor com o atalho escolhido sem iniciar automaticamente."""
        if self.current_screen != AppScreen.SETUP:
            return
        self.digits = preset_to_digits(minutes)
        self._refresh_setup_display()

    def on_action_selected(self, action: PowerAction) -> None:
        """Atualiza a acao de energia selecionada."""
        self.selected_action = action
        self.setup_view.set_selected_action(action)

    def _refresh_setup_display(self) -> None:
        self.setup_view.cancel_flash()
        self.setup_view.update_digits(self.digits)
        total = digits_to_total_seconds(self.digits)
        self.setup_view.set_start_enabled(total > 0)

    def on_start_clicked(self) -> None:
        """Valida o tempo configurado e inicia a contagem regressiva na Tela 2."""
        if self.current_screen != AppScreen.SETUP:
            return

        total = digits_to_total_seconds(self.digits)
        if total <= 0:
            self.setup_view.flash_zero_warning()
            return

        self.setup_view.cancel_flash()
        self.total_seconds = total
        self.remaining_seconds = float(total)
        self.end_monotonic = time.monotonic() + self.remaining_seconds
        self.timer_state = TimerState.RUNNING

        title = format_header_title(self.selected_action, self.total_seconds)
        initial_time = format_countdown(self.total_seconds)
        self.countdown_view.configure_timer(title=title, initial_time_text=initial_time)
        self._show_screen(AppScreen.COUNTDOWN)
        self._schedule_tick()

    def on_toggle_pause(self) -> None:
        """Alterna entre pausa e retomada da contagem regressiva."""
        if self.current_screen != AppScreen.COUNTDOWN:
            return

        if self.timer_state == TimerState.RUNNING:
            self._cancel_after_loop()
            if self.end_monotonic is not None:
                self.remaining_seconds = max(0.0, self.end_monotonic - time.monotonic())
            self.end_monotonic = None
            self.timer_state = TimerState.PAUSED
            self.countdown_view.update_progress(
                time_text=format_countdown(self.remaining_seconds),
                extent=calculate_progress_extent(
                    self.remaining_seconds, self.total_seconds
                ),
                is_paused=True,
            )
        elif self.timer_state == TimerState.PAUSED:
            self.end_monotonic = time.monotonic() + self.remaining_seconds
            self.timer_state = TimerState.RUNNING
            self.countdown_view.update_progress(
                time_text=format_countdown(self.remaining_seconds),
                extent=calculate_progress_extent(
                    self.remaining_seconds, self.total_seconds
                ),
                is_paused=False,
            )
            self._schedule_tick()

    def on_cancel_clicked(self) -> None:
        """Cancela o timer atual e retorna a Tela 1 preservando tempo e acao."""
        self._cancel_after_loop()
        self.timer_state = TimerState.IDLE
        self.end_monotonic = None
        self.remaining_seconds = 0.0
        self._refresh_setup_display()
        self.setup_view.set_selected_action(self.selected_action)
        self._show_screen(AppScreen.SETUP)

    def on_key_press(self, event: tk.Event) -> None:
        """Mapeia atalhos do teclado fisico conforme a tela ativa."""
        if self.current_screen == AppScreen.SETUP:
            if event.char and len(event.char) == 1 and event.char in "0123456789":
                self.on_digit_input(event.char)
            elif event.keysym == "BackSpace":
                self.on_backspace()
            elif event.keysym == "Escape":
                self.on_clear_digits()
            elif event.keysym in ("Return", "KP_Enter"):
                self.on_start_clicked()
        elif self.current_screen == AppScreen.COUNTDOWN:
            if event.keysym == "space":
                self.on_toggle_pause()
            elif event.keysym == "Escape":
                self.on_cancel_clicked()

    def _show_screen(self, screen: AppScreen) -> None:
        self.current_screen = screen
        if screen == AppScreen.SETUP:
            self.countdown_view.pack_forget()
            self.container.configure(bg=Colors.BG_SETUP)
            self.root.configure(bg=Colors.BG_SETUP)
            self.setup_view.pack(fill=tk.BOTH, expand=True)
        else:
            self.setup_view.pack_forget()
            self.container.configure(bg=Colors.BG_COUNTDOWN)
            self.root.configure(bg=Colors.BG_COUNTDOWN)
            self.countdown_view.pack(fill=tk.BOTH, expand=True)

    def _schedule_tick(self) -> None:
        self._cancel_after_loop()
        if not self._is_closed:
            self._after_id = self.root.after(Dimensions.TICK_INTERVAL_MS, self._tick)

    def _cancel_after_loop(self) -> None:
        if self._after_id is not None:
            try:
                self.root.after_cancel(self._after_id)
            except tk.TclError:
                pass
            self._after_id = None

    def _tick(self) -> None:
        self._after_id = None
        if self._is_closed or self.timer_state != TimerState.RUNNING:
            return
        if self.end_monotonic is None:
            return

        remaining = max(0.0, self.end_monotonic - time.monotonic())
        self.remaining_seconds = remaining

        if remaining > 0.0:
            self.countdown_view.update_progress(
                time_text=format_countdown(remaining),
                extent=calculate_progress_extent(remaining, self.total_seconds),
                is_paused=False,
            )
            self._schedule_tick()
            return

        self.countdown_view.update_progress(
            time_text="00:00",
            extent=0.0,
            is_paused=False,
        )
        self.timer_state = TimerState.FINISHED
        self.end_monotonic = None
        self._handle_timer_finished()

    def _handle_timer_finished(self) -> None:
        result = execute_power_action(
            self.selected_action,
            os_type=self.os_type,
            dry_run=self.dry_run,
        )

        if self.dry_run and result.success:
            cmd_str = " ".join(result.command)
            messagebox.showinfo(
                "Modo Simulacao (--dry-run)",
                "Contagem concluida em modo de simulacao.\n\n"
                f"Acao: {self.selected_action.value}\n"
                f"SO: {result.os_type.value}\n"
                f"Script: {result.script_path}\n"
                f"Comando: {cmd_str}",
            )
            self.on_cancel_clicked()
            return

        if result.success:
            logger.info("Acao executada com sucesso; encerrando aplicativo.")
            self.on_window_close()
            return

        messagebox.showerror(
            "Erro ao executar acao",
            result.error_message or "Nao foi possivel executar o script de energia.",
        )
        self.on_cancel_clicked()

    def on_window_close(self) -> None:
        """Cancela loops pendentes e encerra a janela com seguranca."""
        if self._is_closed:
            return
        self._is_closed = True
        self._cancel_after_loop()
        if self._startup_after_id is not None:
            try:
                self.root.after_cancel(self._startup_after_id)
            except tk.TclError:
                pass
            self._startup_after_id = None
        self.setup_view.cancel_flash()
        try:
            self.root.destroy()
        except tk.TclError:
            pass
