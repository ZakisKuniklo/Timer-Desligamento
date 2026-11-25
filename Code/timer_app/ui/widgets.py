"""Componentes visuais customizados desenhados em tkinter.Canvas."""

from __future__ import annotations

import math
import tkinter as tk
from typing import Callable

from timer_app.config import Colors
from timer_app.models import PowerAction


def draw_rounded_rect(
    canvas: tk.Canvas,
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    radius: float,
    **kwargs: object,
) -> int:
    """Desenha um retangulo com cantos arredondados suaves via poligono."""
    r = max(0.0, min(radius, (x2 - x1) / 2.0, (y2 - y1) / 2.0))
    points = [
        x1 + r,
        y1,
        x1 + r,
        y1,
        x2 - r,
        y1,
        x2 - r,
        y1,
        x2,
        y1,
        x2,
        y1 + r,
        x2,
        y1 + r,
        x2,
        y2 - r,
        x2,
        y2 - r,
        x2,
        y2,
        x2 - r,
        y2,
        x2 - r,
        y2,
        x1 + r,
        y2,
        x1 + r,
        y2,
        x1,
        y2,
        x1,
        y2 - r,
        x1,
        y2 - r,
        x1,
        y1 + r,
        x1,
        y1 + r,
        x1,
        y1,
    ]
    return canvas.create_polygon(points, smooth=True, **kwargs)


class PillButton(tk.Canvas):
    """Botao em formato de pilula totalmente desenhado em Canvas."""

    def __init__(
        self,
        parent: tk.Misc,
        text: str,
        command: Callable[[], None],
        width: int,
        height: int,
        bg_color: str = Colors.SURFACE,
        hover_color: str = Colors.SURFACE_HOVER,
        text_color: str = Colors.TEXT_PRIMARY,
        disabled_bg: str = Colors.SURFACE,
        disabled_fg: str = Colors.TEXT_MUTED,
        font: tuple[str, int] | tuple[str, int, str] = ("TkDefaultFont", 12),
        canvas_bg: str = Colors.BG_SETUP,
        invoke_when_disabled: bool = False,
    ) -> None:
        super().__init__(
            parent,
            width=width,
            height=height,
            bg=canvas_bg,
            highlightthickness=0,
            bd=0,
            cursor="hand2",
        )
        self._text = text
        self._command = command
        self._width = width
        self._height = height
        self._bg_color = bg_color
        self._hover_color = hover_color
        self._text_color = text_color
        self._disabled_bg = disabled_bg
        self._disabled_fg = disabled_fg
        self._font = font
        self._invoke_when_disabled = invoke_when_disabled

        self._enabled = True
        self._hovered = False
        self._pressed = False

        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<ButtonPress-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_click)
        self._redraw()

    def set_enabled(self, enabled: bool) -> None:
        """Atualiza o estado habilitado/atenuado do botao."""
        if self._enabled == enabled:
            return
        self._enabled = enabled
        cursor = "hand2" if (enabled or self._invoke_when_disabled) else ""
        self.configure(cursor=cursor)
        self._redraw()

    def set_colors(self, bg: str, hover: str, fg: str) -> None:
        """Atualiza dinamicamente as cores do estado ativo do botao."""
        self._bg_color = bg
        self._hover_color = hover
        self._text_color = fg
        self._redraw()

    def _on_enter(self, _event: tk.Event) -> None:
        self._hovered = True
        self._redraw()

    def _on_leave(self, _event: tk.Event) -> None:
        self._hovered = False
        self._pressed = False
        self._redraw()

    def _on_press(self, _event: tk.Event) -> None:
        if self._enabled or self._invoke_when_disabled:
            self._pressed = True
            self._redraw()

    def _on_click(self, event: tk.Event) -> None:
        was_pressed = self._pressed
        self._pressed = False
        self._redraw()
        if not was_pressed:
            return
        if not (0 <= event.x <= self._width and 0 <= event.y <= self._height):
            return
        if self._enabled or self._invoke_when_disabled:
            self._command()

    def _redraw(self) -> None:
        self.delete("all")
        if not self._enabled:
            fill = self._disabled_bg
            fg = self._disabled_fg
        elif self._pressed or self._hovered:
            fill = self._hover_color
            fg = self._text_color
        else:
            fill = self._bg_color
            fg = self._text_color

        radius = (self._height - 2) / 2.0
        draw_rounded_rect(
            self,
            1,
            1,
            self._width - 1,
            self._height - 1,
            radius=radius,
            fill=fill,
            outline="",
        )
        self.create_text(
            self._width / 2.0,
            self._height / 2.0,
            text=self._text,
            fill=fg,
            font=self._font,
        )


class SegmentedSelector(tk.Canvas):
    """Barra segmentada em pilula para selecionar Desligar, Reiniciar ou Logoff."""

    def __init__(
        self,
        parent: tk.Misc,
        options: list[tuple[PowerAction, str]],
        initial: PowerAction,
        on_change: Callable[[PowerAction], None],
        width: int = 326,
        height: int = 40,
        font: tuple[str, int] | tuple[str, int, str] = ("TkDefaultFont", 11, "bold"),
        canvas_bg: str = Colors.BG_SETUP,
    ) -> None:
        super().__init__(
            parent,
            width=width,
            height=height,
            bg=canvas_bg,
            highlightthickness=0,
            bd=0,
            cursor="hand2",
        )
        self._segments = options
        self._selected = initial
        self._on_change = on_change
        self._width = width
        self._height = height
        self._font = font
        self._hovered_index: int | None = None

        self.bind("<Button-1>", self._on_click)
        self.bind("<Motion>", self._on_motion)
        self.bind("<Leave>", self._on_leave)
        self._redraw()

    def set_selected(self, action: PowerAction) -> None:
        """Define a acao selecionada sem disparar callback."""
        if self._selected == action:
            return
        self._selected = action
        self._redraw()

    def get_selected(self) -> PowerAction:
        """Retorna a acao atualmente selecionada."""
        return self._selected

    def _index_at_x(self, x: float) -> int:
        seg_width = self._width / float(len(self._segments))
        idx = int(x // seg_width)
        return max(0, min(len(self._segments) - 1, idx))

    def _on_click(self, event: tk.Event) -> None:
        idx = self._index_at_x(event.x)
        action = self._segments[idx][0]
        if action != self._selected:
            self._selected = action
            self._redraw()
        self._on_change(action)

    def _on_motion(self, event: tk.Event) -> None:
        idx = self._index_at_x(event.x)
        if idx != self._hovered_index:
            self._hovered_index = idx
            self._redraw()

    def _on_leave(self, _event: tk.Event) -> None:
        if self._hovered_index is not None:
            self._hovered_index = None
            self._redraw()

    def _redraw(self) -> None:
        self.delete("all")
        draw_rounded_rect(
            self,
            1,
            1,
            self._width - 1,
            self._height - 1,
            radius=(self._height - 2) / 2.0,
            fill=Colors.SURFACE,
            outline="",
        )

        count = len(self._segments)
        seg_width = (self._width - 6) / float(count)
        inner_pad_y = 3
        inner_radius = (self._height - 2 * inner_pad_y) / 2.0

        for idx, (action, label) in enumerate(self._segments):
            sx1 = 3 + idx * seg_width
            sx2 = sx1 + seg_width
            is_selected = action == self._selected
            is_hovered = self._hovered_index == idx

            if is_selected:
                draw_rounded_rect(
                    self,
                    sx1,
                    inner_pad_y,
                    sx2,
                    self._height - inner_pad_y,
                    radius=inner_radius,
                    fill=Colors.ACCENT_BLUE,
                    outline="",
                )
                text_color = Colors.TEXT_PRIMARY
            elif is_hovered:
                draw_rounded_rect(
                    self,
                    sx1,
                    inner_pad_y,
                    sx2,
                    self._height - inner_pad_y,
                    radius=inner_radius,
                    fill=Colors.SURFACE_HOVER,
                    outline="",
                )
                text_color = Colors.TEXT_PRIMARY
            else:
                text_color = Colors.TEXT_SECONDARY

            self.create_text(
                (sx1 + sx2) / 2.0,
                self._height / 2.0,
                text=label,
                fill=text_color,
                font=self._font,
            )


class KeypadButton(tk.Canvas):
    """Botao minimalista do teclado numerico 3x4 (digitos ou icone vetorial backspace)."""

    def __init__(
        self,
        parent: tk.Misc,
        label: str,
        command: Callable[[], None],
        width: int = 92,
        height: int = 64,
        font: tuple[str, int] = ("TkDefaultFont", 22),
        icon_type: str | None = None,
    ) -> None:
        super().__init__(
            parent,
            width=width,
            height=height,
            bg=Colors.BG_SETUP,
            highlightthickness=0,
            bd=0,
            cursor="hand2",
        )
        self._label = label
        self._command = command
        self._width = width
        self._height = height
        self._font = font
        self._icon_type = icon_type
        self._hovered = False
        self._pressed = False

        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<ButtonPress-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)
        self._redraw()

    def _on_enter(self, _event: tk.Event) -> None:
        self._hovered = True
        self._redraw()

    def _on_leave(self, _event: tk.Event) -> None:
        self._hovered = False
        self._pressed = False
        self._redraw()

    def _on_press(self, _event: tk.Event) -> None:
        self._pressed = True
        self._redraw()

    def _on_release(self, event: tk.Event) -> None:
        was_pressed = self._pressed
        self._pressed = False
        self._redraw()
        if was_pressed and 0 <= event.x <= self._width and 0 <= event.y <= self._height:
            self._command()

    def _draw_backspace_icon(self, cx: float, cy: float) -> None:
        """Desenha o icone vetorial de backspace (seta esquerda com x interno)."""
        outline_pts = [
            cx - 12,
            cy,
            cx - 5,
            cy - 8,
            cx + 12,
            cy - 8,
            cx + 12,
            cy + 8,
            cx - 5,
            cy + 8,
        ]
        self.create_polygon(
            outline_pts,
            fill="",
            outline=Colors.TEXT_PRIMARY,
            width=1.8,
            joinstyle=tk.ROUND,
        )
        self.create_line(
            cx,
            cy - 3.5,
            cx + 7,
            cy + 3.5,
            fill=Colors.TEXT_PRIMARY,
            width=1.8,
            capstyle=tk.ROUND,
        )
        self.create_line(
            cx + 7,
            cy - 3.5,
            cx,
            cy + 3.5,
            fill=Colors.TEXT_PRIMARY,
            width=1.8,
            capstyle=tk.ROUND,
        )

    def _redraw(self) -> None:
        self.delete("all")
        cx = self._width / 2.0
        cy = self._height / 2.0

        if self._pressed:
            r = min(self._width, self._height) / 2.0 - 3
            self.create_oval(
                cx - r,
                cy - r,
                cx + r,
                cy + r,
                fill=Colors.SURFACE_HOVER,
                outline="",
            )
        elif self._hovered:
            r = min(self._width, self._height) / 2.0 - 3
            self.create_oval(
                cx - r,
                cy - r,
                cx + r,
                cy + r,
                fill=Colors.SURFACE,
                outline="",
            )

        if self._icon_type == "backspace":
            self._draw_backspace_icon(cx, cy)
        else:
            self.create_text(
                cx,
                cy,
                text=self._label,
                fill=Colors.TEXT_PRIMARY,
                font=self._font,
            )


class CancelIconButton(tk.Canvas):
    """Botao circular discreto com icone vetorial X para cancelar na Tela 2."""

    def __init__(
        self,
        parent: tk.Misc,
        command: Callable[[], None],
        size: int = 36,
        canvas_bg: str = Colors.BG_COUNTDOWN,
    ) -> None:
        super().__init__(
            parent,
            width=size,
            height=size,
            bg=canvas_bg,
            highlightthickness=0,
            bd=0,
            cursor="hand2",
        )
        self._command = command
        self._size = size
        self._hovered = False
        self._pressed = False

        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<ButtonPress-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)
        self._redraw()

    def _on_enter(self, _event: tk.Event) -> None:
        self._hovered = True
        self._redraw()

    def _on_leave(self, _event: tk.Event) -> None:
        self._hovered = False
        self._pressed = False
        self._redraw()

    def _on_press(self, _event: tk.Event) -> None:
        self._pressed = True
        self._redraw()

    def _on_release(self, event: tk.Event) -> None:
        was_pressed = self._pressed
        self._pressed = False
        self._redraw()
        if was_pressed and 0 <= event.x <= self._size and 0 <= event.y <= self._size:
            self._command()

    def _redraw(self) -> None:
        self.delete("all")
        cx = self._size / 2.0
        cy = self._size / 2.0
        if self._pressed or self._hovered:
            bg = Colors.SURFACE_HOVER if self._hovered else Colors.SURFACE
            self.create_oval(2, 2, self._size - 2, self._size - 2, fill=bg, outline="")

        offset = 7.5
        self.create_line(
            cx - offset,
            cy - offset,
            cx + offset,
            cy + offset,
            fill=Colors.TEXT_PRIMARY,
            width=2.2,
            capstyle=tk.ROUND,
        )
        self.create_line(
            cx + offset,
            cy - offset,
            cx - offset,
            cy + offset,
            fill=Colors.TEXT_PRIMARY,
            width=2.2,
            capstyle=tk.ROUND,
        )


class CircularProgressRing(tk.Canvas):
    """Anel circular de progresso com contador central e botao Play/Pause vetorial."""

    def __init__(
        self,
        parent: tk.Misc,
        size: int,
        stroke_width: int,
        font_family: str,
        on_toggle_pause: Callable[[], None],
    ) -> None:
        super().__init__(
            parent,
            width=size,
            height=size,
            bg=Colors.BG_COUNTDOWN,
            highlightthickness=0,
            bd=0,
        )
        self._size = size
        self._stroke_width = stroke_width
        self._font_family = font_family
        self._on_toggle_pause = on_toggle_pause

        self._time_text = "00:00"
        self._extent = 359.9
        self._is_paused = False
        self._toggle_hovered = False

        cx = size / 2.0
        cy = size / 2.0
        self._toggle_center = (cx, cy + 48.0)
        self._toggle_radius = 28.0

        pad = stroke_width / 2.0 + 10.0
        bbox = (pad, pad, size - pad, size - pad)

        self._track_id = self.create_arc(
            *bbox,
            start=90,
            extent=359.9,
            style=tk.ARC,
            width=stroke_width,
            outline=Colors.RING_TRACK,
        )
        self._arc_id = self.create_arc(
            *bbox,
            start=90,
            extent=359.9,
            style=tk.ARC,
            width=stroke_width,
            outline=Colors.ACCENT_BLUE,
        )
        self._time_id = self.create_text(
            cx,
            cy - 18.0,
            text=self._time_text,
            fill=Colors.TEXT_PRIMARY,
            font=(self._font_family, 42),
        )
        self._toggle_bg_id = self.create_oval(
            self._toggle_center[0] - self._toggle_radius,
            self._toggle_center[1] - self._toggle_radius,
            self._toggle_center[0] + self._toggle_radius,
            self._toggle_center[1] + self._toggle_radius,
            fill="",
            outline="",
        )

        self.bind("<Motion>", self._on_motion)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_canvas_click)
        self._draw_toggle_icon(self._is_paused)

    def set_state(self, time_text: str, extent: float, is_paused: bool) -> None:
        """Atualiza o texto do contador, o angulo do arco e o icone Play/Pause."""
        self._time_text = time_text
        self._extent = max(0.0, min(359.9, extent))
        self._is_paused = is_paused

        font_size = 42 if len(time_text) <= 5 else 32
        self.itemconfigure(
            self._time_id,
            text=self._time_text,
            font=(self._font_family, font_size),
        )

        if self._extent <= 0.0:
            self.itemconfigure(self._arc_id, state="hidden")
        else:
            self.itemconfigure(self._arc_id, state="normal", extent=self._extent)

        self._draw_toggle_icon(self._is_paused)

    def _is_inside_toggle(self, x: float, y: float) -> bool:
        tx, ty = self._toggle_center
        return math.hypot(x - tx, y - ty) <= self._toggle_radius

    def _on_motion(self, event: tk.Event) -> None:
        hovered = self._is_inside_toggle(event.x, event.y)
        if hovered != self._toggle_hovered:
            self._toggle_hovered = hovered
            self.configure(cursor="hand2" if hovered else "")
            self.itemconfigure(
                self._toggle_bg_id,
                fill=Colors.SURFACE_HOVER if hovered else "",
            )

    def _on_leave(self, _event: tk.Event) -> None:
        if self._toggle_hovered:
            self._toggle_hovered = False
            self.configure(cursor="")
            self.itemconfigure(self._toggle_bg_id, fill="")

    def _on_canvas_click(self, event: tk.Event) -> None:
        if self._is_inside_toggle(event.x, event.y):
            self._on_toggle_pause()

    def _draw_toggle_icon(self, is_paused: bool) -> None:
        """Desenha vetorialmente o icone Pause (||) ou Play (triangulo)."""
        self.delete("toggle_icon")
        tx, ty = self._toggle_center
        if is_paused:
            points = [
                tx - 7,
                ty - 11,
                tx - 7,
                ty + 11,
                tx + 11,
                ty,
            ]
            self.create_polygon(
                points,
                fill=Colors.TEXT_PRIMARY,
                outline=Colors.TEXT_PRIMARY,
                tags=("toggle_icon",),
            )
        else:
            self.create_rectangle(
                tx - 8,
                ty - 10,
                tx - 3,
                ty + 10,
                fill=Colors.TEXT_PRIMARY,
                outline="",
                tags=("toggle_icon",),
            )
            self.create_rectangle(
                tx + 3,
                ty - 10,
                tx + 8,
                ty + 10,
                fill=Colors.TEXT_PRIMARY,
                outline="",
                tags=("toggle_icon",),
            )
