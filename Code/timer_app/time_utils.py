"""Funcoes puras para manipulacao de tempo, digitos HHMMSS e progresso visual."""

from __future__ import annotations

import math

from timer_app.config import ACTION_LABELS
from timer_app.models import PowerAction

MAX_DIGITS = 6
DEFAULT_DIGITS = "000000"
MAX_TOTAL_SECONDS = 99 * 3600 + 59 * 60 + 59
FULL_RING_EXTENT = 359.9


def _sanitize_digits(digits: str) -> str:
    """Garante representacao valida de 6 digitos numericos."""
    if len(digits) != MAX_DIGITS or not digits.isdigit():
        raise ValueError(f"Esperada string de 6 digitos numericos, recebido: {digits!r}")
    return digits


def push_digit(digits: str, token: str) -> str:
    """Insere um token ('0'-'9' ou '00') da direita para a esquerda em HHMMSS."""
    current = _sanitize_digits(digits)
    if token == "00":
        if current[:2] != "00":
            return current
        return current[2:] + "00"
    if len(token) == 1 and token.isdigit():
        if current[0] != "0":
            return current
        return current[1:] + token
    raise ValueError(f"Token numerico invalido: {token!r}")


def pop_digit(digits: str) -> str:
    """Remove o digito mais a direita e preenche '0' a esquerda."""
    current = _sanitize_digits(digits)
    return "0" + current[:-1]


def preset_to_digits(minutes: int) -> str:
    """Converte um atalho em minutos para a representacao HHMMSS de 6 digitos."""
    if minutes < 0:
        raise ValueError(f"Preset em minutos nao pode ser negativo: {minutes}")
    hours, rem_minutes = divmod(minutes, 60)
    if hours > 99:
        raise ValueError(f"Preset excede o limite de 99 horas: {minutes}")
    return f"{hours:02d}{rem_minutes:02d}00"


def digits_to_hms(digits: str) -> tuple[int, int, int]:
    """Fatia os 6 digitos em (horas, minutos, segundos) sem normalizar >= 60."""
    current = _sanitize_digits(digits)
    return int(current[0:2]), int(current[2:4]), int(current[4:6])


def digits_to_total_seconds(digits: str) -> int:
    """Converte HHMMSS no total de segundos (normalizando valores >= 60)."""
    hours, minutes, seconds = digits_to_hms(digits)
    return hours * 3600 + minutes * 60 + seconds


def seconds_to_digits(total_seconds: int) -> str:
    """Converte segundos totais normalizados em string HHMMSS (ate 99:59:59)."""
    clamped = max(0, min(total_seconds, MAX_TOTAL_SECONDS))
    hours, remainder = divmod(clamped, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}{minutes:02d}{seconds:02d}"


def format_countdown(remaining_seconds: float) -> str:
    """Formata o tempo restante usando math.ceil para MM:SS ou HH:MM:SS."""
    ceil_seconds = max(0, math.ceil(remaining_seconds))
    if ceil_seconds < 3600:
        minutes, seconds = divmod(ceil_seconds, 60)
        return f"{minutes:02d}:{seconds:02d}"
    hours, remainder = divmod(ceil_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def format_header_title(action: PowerAction, total_seconds: int) -> str:
    """Formata o cabecalho da tela de contagem regressiva (ex.: 'Desligar • 05:00')."""
    label = ACTION_LABELS[action]
    formatted_time = format_countdown(total_seconds)
    return f"{label} \u2022 {formatted_time}"


def calculate_progress_extent(remaining_seconds: float, total_seconds: int) -> float:
    """Calcula o angulo do arco de progresso entre 0.0 e 359.9 graus."""
    if total_seconds <= 0 or remaining_seconds <= 0.0:
        return 0.0
    ratio = remaining_seconds / float(total_seconds)
    return max(0.0, min(FULL_RING_EXTENT, FULL_RING_EXTENT * ratio))
