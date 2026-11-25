"""Constantes visuais, dimensoes, rotulos e configuracoes do aplicativo."""

from __future__ import annotations

from timer_app.models import OperatingSystem, PowerAction

APP_TITLE = "Timer de Desligamento"


class Colors:
    """Paleta oficial do tema escuro definida na especificacao visual."""

    BG_SETUP = "#000000"
    BG_COUNTDOWN = "#1F242D"
    SURFACE = "#24262B"
    SURFACE_HOVER = "#33363D"
    SURFACE_DISABLED = "#1A1C20"
    DIGITS_INACTIVE = "#6E7175"
    TEXT_PRIMARY = "#FFFFFF"
    TEXT_SECONDARY = "#D0D3D8"
    TEXT_MUTED = "#8A8E96"
    ACCENT_BLUE = "#1A73E8"
    ACCENT_BLUE_HOVER = "#2575FC"
    RING_TRACK = "#2C323E"
    ALERT_RED = "#E53935"


class Dimensions:
    """Dimensoes da janela, loop de temporizacao e componentes no Canvas."""

    WINDOW_WIDTH = 390
    WINDOW_HEIGHT = 650
    TICK_INTERVAL_MS = 50
    RING_SIZE = 270
    RING_STROKE = 11


PRESETS_MINUTES: tuple[int, ...] = (1, 5, 10, 15)

ACTION_LABELS: dict[PowerAction, str] = {
    PowerAction.DESLIGAR: "Desligar",
    PowerAction.REINICIAR: "Reiniciar",
    PowerAction.LOGOFF: "Logoff",
}

SCRIPT_FILENAMES: dict[OperatingSystem, dict[PowerAction, str]] = {
    OperatingSystem.WINDOWS: {
        PowerAction.DESLIGAR: "win/desligar.bat",
        PowerAction.REINICIAR: "win/reiniciar.bat",
        PowerAction.LOGOFF: "win/logoff.bat",
    },
    OperatingSystem.LINUX: {
        PowerAction.DESLIGAR: "linux/desligar.sh",
        PowerAction.REINICIAR: "linux/reiniciar.sh",
        PowerAction.LOGOFF: "linux/logoff.sh",
    },
}


def get_font_family(os_type: OperatingSystem) -> str:
    """Retorna a familia de fontes padrao mais adequada para o SO atual."""
    if os_type == OperatingSystem.WINDOWS:
        return "Segoe UI"
    if os_type == OperatingSystem.LINUX:
        return "DejaVu Sans"
    return "TkDefaultFont"
