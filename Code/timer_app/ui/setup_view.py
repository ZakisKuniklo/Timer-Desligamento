"""Tela 1 (Configuracao): visor HH MM SS, presets, barra segmentada e teclado 3x4."""

from __future__ import annotations

import tkinter as tk
from typing import Callable

from timer_app.config import ACTION_LABELS, Colors, PRESETS_MINUTES
from timer_app.models import PowerAction
from timer_app.time_utils import digits_to_hms
from timer_app.ui.widgets import KeypadButton, PillButton, SegmentedSelector


class SetupView(tk.Frame):
    """Tela de configuracao inicial do temporizador e acao de energia."""

    def __init__(
        self,
        parent: tk.Misc,
        font_family: str,
        on_digit: Callable[[str], None],
        on_backspace: Callable[[], None],
        on_preset: Callable[[int], None],
        on_action_change: Callable[[PowerAction], None],
        on_start: Callable[[], None],
    ) -> None:
        super().__init__(parent, bg=Colors.BG_SETUP)
        self._font_family = font_family
        self._current_digits = "000000"
        self._flash_after_id: str | None = None

        self._build_display()
        self._build_presets(on_preset)
        self._build_action_selector(on_action_change)
        self._build_start_button(on_start)
        self._build_keypad(on_digit, on_backspace)

        self.update_digits("000000")
        self.set_start_enabled(False)

    def _build_display(self) -> None:
        display_frame = tk.Frame(self, bg=Colors.BG_SETUP)
        display_frame.pack(pady=(28, 18))

        digit_font = (self._font_family, 44, "bold")
        caption_font = (self._font_family, 10)

        self.lbl_hours = self._create_time_block(
            display_frame,
            caption="Horas",
            digit_font=digit_font,
            caption_font=caption_font,
            padx=(0, 14),
        )
        self.lbl_minutes = self._create_time_block(
            display_frame,
            caption="Minutos",
            digit_font=digit_font,
            caption_font=caption_font,
            padx=14,
        )
        self.lbl_seconds = self._create_time_block(
            display_frame,
            caption="Segundos",
            digit_font=digit_font,
            caption_font=caption_font,
            padx=(14, 0),
        )

    @staticmethod
    def _create_time_block(
        parent: tk.Misc,
        caption: str,
        digit_font: tuple[str, int, str],
        caption_font: tuple[str, int],
        padx: int | tuple[int, int],
    ) -> tk.Label:
        col = tk.Frame(parent, bg=Colors.BG_SETUP)
        col.pack(side=tk.LEFT, padx=padx)

        lbl_digits = tk.Label(
            col,
            text="00",
            font=digit_font,
            fg=Colors.DIGITS_INACTIVE,
            bg=Colors.BG_SETUP,
        )
        lbl_digits.pack()

        lbl_caption = tk.Label(
            col,
            text=caption,
            font=caption_font,
            fg=Colors.TEXT_SECONDARY,
            bg=Colors.BG_SETUP,
        )
        lbl_caption.pack(pady=(2, 0))
        return lbl_digits

    def _build_presets(self, on_preset: Callable[[int], None]) -> None:
        presets_frame = tk.Frame(self, bg=Colors.BG_SETUP)
        presets_frame.pack(pady=(0, 20))

        self.preset_buttons: list[PillButton] = []
        preset_font = (self._font_family, 11, "bold")
        for idx, minutes in enumerate(PRESETS_MINUTES):
            btn = PillButton(
                presets_frame,
                text=f"{minutes}min",
                command=lambda m=minutes: on_preset(m),
                width=74,
                height=34,
                bg_color=Colors.SURFACE,
                hover_color=Colors.SURFACE_HOVER,
                text_color=Colors.TEXT_PRIMARY,
                font=preset_font,
                canvas_bg=Colors.BG_SETUP,
            )
            padx = (0, 10) if idx < len(PRESETS_MINUTES) - 1 else (0, 0)
            btn.pack(side=tk.LEFT, padx=padx)
            self.preset_buttons.append(btn)

    def _build_action_selector(
        self,
        on_action_change: Callable[[PowerAction], None],
    ) -> None:
        options = [
            (action, ACTION_LABELS[action])
            for action in (
                PowerAction.DESLIGAR,
                PowerAction.REINICIAR,
                PowerAction.LOGOFF,
            )
        ]
        self.action_selector = SegmentedSelector(
            self,
            options=options,
            initial=PowerAction.DESLIGAR,
            on_change=on_action_change,
            width=326,
            height=40,
            font=(self._font_family, 10, "bold"),
            canvas_bg=Colors.BG_SETUP,
        )
        self.action_selector.pack(pady=(0, 14))

    def _build_start_button(self, on_start: Callable[[], None]) -> None:
        self.btn_start = PillButton(
            self,
            text="Iniciar",
            command=on_start,
            width=326,
            height=44,
            bg_color=Colors.ACCENT_BLUE,
            hover_color=Colors.ACCENT_BLUE_HOVER,
            text_color=Colors.TEXT_PRIMARY,
            disabled_bg=Colors.SURFACE,
            disabled_fg=Colors.TEXT_MUTED,
            font=(self._font_family, 12, "bold"),
            canvas_bg=Colors.BG_SETUP,
            invoke_when_disabled=True,
        )
        self.btn_start.pack(pady=(0, 20))

    def _build_keypad(
        self,
        on_digit: Callable[[str], None],
        on_backspace: Callable[[], None],
    ) -> None:
        keypad_frame = tk.Frame(self, bg=Colors.BG_SETUP)
        keypad_frame.pack(pady=(0, 16))

        rows: list[list[str]] = [
            ["1", "2", "3"],
            ["4", "5", "6"],
            ["7", "8", "9"],
            ["00", "0", "backspace"],
        ]
        key_font = (self._font_family, 21)

        for row_idx, row in enumerate(rows):
            for col_idx, token in enumerate(row):
                if token == "backspace":
                    btn = KeypadButton(
                        keypad_frame,
                        label="",
                        command=on_backspace,
                        width=92,
                        height=64,
                        font=key_font,
                        icon_type="backspace",
                    )
                else:
                    btn = KeypadButton(
                        keypad_frame,
                        label=token,
                        command=lambda t=token: on_digit(t),
                        width=92,
                        height=64,
                        font=key_font,
                    )
                btn.grid(row=row_idx, column=col_idx, padx=6, pady=4)

    def update_digits(self, digits: str) -> None:
        """Atualiza os tres blocos HH MM SS e alterna cor entre inativo e ativo."""
        self._current_digits = digits
        hours, minutes, seconds = digits_to_hms(digits)
        self.lbl_hours.configure(text=f"{hours:02d}")
        self.lbl_minutes.configure(text=f"{minutes:02d}")
        self.lbl_seconds.configure(text=f"{seconds:02d}")
        self._apply_digit_color()

    def _apply_digit_color(self) -> None:
        color = (
            Colors.DIGITS_INACTIVE
            if self._current_digits == "000000"
            else Colors.TEXT_PRIMARY
        )
        for lbl in (self.lbl_hours, self.lbl_minutes, self.lbl_seconds):
            lbl.configure(fg=color)

    def set_selected_action(self, action: PowerAction) -> None:
        """Sincroniza a barra segmentada com o estado selecionado."""
        self.action_selector.set_selected(action)

    def set_start_enabled(self, enabled: bool) -> None:
        """Atualiza o estado visual ativo/atenuado do botao Iniciar."""
        self.btn_start.set_enabled(enabled)

    def flash_zero_warning(self) -> None:
        """Pisca brevemente os digitos em vermelho ao tentar iniciar com tempo zero."""
        self.cancel_flash()
        for lbl in (self.lbl_hours, self.lbl_minutes, self.lbl_seconds):
            lbl.configure(fg=Colors.ALERT_RED)
        self._flash_after_id = self.after(300, self._restore_after_flash)

    def _restore_after_flash(self) -> None:
        self._flash_after_id = None
        self._apply_digit_color()

    def cancel_flash(self) -> None:
        """Cancela feedback visual pendente antes de trocar ou fechar a tela."""
        if self._flash_after_id is not None:
            try:
                self.after_cancel(self._flash_after_id)
            except tk.TclError:
                pass
            self._flash_after_id = None
