"""Tela 2 (Contagem Regressiva Ativa): cabecalho com X, anel circular e Play/Pause."""

from __future__ import annotations

import tkinter as tk
from typing import Callable

from timer_app.config import Colors, Dimensions
from timer_app.ui.widgets import CancelIconButton, CircularProgressRing


class CountdownView(tk.Frame):
    """Tela minimalista exibida durante a contagem regressiva ativa ou pausada."""

    def __init__(
        self,
        parent: tk.Misc,
        font_family: str,
        on_toggle_pause: Callable[[], None],
        on_cancel: Callable[[], None],
    ) -> None:
        super().__init__(parent, bg=Colors.BG_COUNTDOWN)

        header = tk.Frame(self, bg=Colors.BG_COUNTDOWN)
        header.pack(fill=tk.X, padx=24, pady=(24, 12))

        self.lbl_title = tk.Label(
            header,
            text="",
            font=(font_family, 15),
            fg=Colors.TEXT_PRIMARY,
            bg=Colors.BG_COUNTDOWN,
            anchor="w",
        )
        self.lbl_title.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.btn_cancel = CancelIconButton(
            header,
            command=on_cancel,
            size=36,
            canvas_bg=Colors.BG_COUNTDOWN,
        )
        self.btn_cancel.pack(side=tk.RIGHT)

        center_frame = tk.Frame(self, bg=Colors.BG_COUNTDOWN)
        center_frame.pack(fill=tk.BOTH, expand=True)

        self.ring = CircularProgressRing(
            center_frame,
            size=Dimensions.RING_SIZE,
            stroke_width=Dimensions.RING_STROKE,
            font_family=font_family,
            on_toggle_pause=on_toggle_pause,
        )
        self.ring.place(relx=0.5, rely=0.45, anchor=tk.CENTER)

    def configure_timer(self, title: str, initial_time_text: str) -> None:
        """Inicializa titulo e anel completo ao abrir a tela de contagem."""
        self.lbl_title.configure(text=title)
        self.ring.set_state(initial_time_text, extent=359.9, is_paused=False)

    def update_progress(self, time_text: str, extent: float, is_paused: bool) -> None:
        """Atualiza contador central, arco de progresso e icone Play/Pause."""
        self.ring.set_state(time_text, extent=extent, is_paused=is_paused)
