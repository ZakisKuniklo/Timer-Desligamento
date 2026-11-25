"""Testes unitarios para funcoes puras em timer_app.time_utils."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

CODE_DIR = Path(__file__).resolve().parent.parent
if str(CODE_DIR) not in sys.path:
    sys.path.insert(0, str(CODE_DIR))

from timer_app.models import PowerAction  # noqa: E402
from timer_app.time_utils import (  # noqa: E402
    calculate_progress_extent,
    digits_to_hms,
    digits_to_total_seconds,
    format_countdown,
    format_header_title,
    pop_digit,
    preset_to_digits,
    push_digit,
    seconds_to_digits,
)


class TestTimeUtils(unittest.TestCase):
    """Valida manipulacao HHMMSS, normalizacao, formatacao e progresso."""

    def test_push_digit_slides_right_to_left(self) -> None:
        digits = "000000"
        digits = push_digit(digits, "5")
        self.assertEqual(digits, "000005")
        digits = push_digit(digits, "00")
        self.assertEqual(digits, "000500")
        digits = push_digit(digits, "1")
        self.assertEqual(digits, "005001")

    def test_push_digit_respects_six_digit_limit(self) -> None:
        self.assertEqual(push_digit("100000", "5"), "100000")
        self.assertEqual(push_digit("010000", "00"), "010000")
        self.assertEqual(push_digit("001000", "00"), "100000")

    def test_push_digit_rejects_invalid_token(self) -> None:
        with self.assertRaises(ValueError):
            push_digit("000000", "a")
        with self.assertRaises(ValueError):
            push_digit("000000", "12")

    def test_pop_digit(self) -> None:
        self.assertEqual(pop_digit("000500"), "000050")
        self.assertEqual(pop_digit("000005"), "000000")
        self.assertEqual(pop_digit("000000"), "000000")

    def test_preset_to_digits(self) -> None:
        self.assertEqual(preset_to_digits(1), "000100")
        self.assertEqual(preset_to_digits(5), "000500")
        self.assertEqual(preset_to_digits(10), "001000")
        self.assertEqual(preset_to_digits(15), "001500")
        self.assertEqual(preset_to_digits(90), "013000")
        with self.assertRaises(ValueError):
            preset_to_digits(-1)

    def test_digits_to_hms_and_normalization(self) -> None:
        self.assertEqual(digits_to_hms("000090"), (0, 0, 90))
        self.assertEqual(digits_to_total_seconds("000090"), 90)
        self.assertEqual(seconds_to_digits(90), "000130")
        self.assertEqual(digits_to_total_seconds("013000"), 5400)
        self.assertEqual(seconds_to_digits(9999999), "995959")

    def test_format_countdown(self) -> None:
        self.assertEqual(format_countdown(0.0), "00:00")
        self.assertEqual(format_countdown(-2.0), "00:00")
        self.assertEqual(format_countdown(59.1), "01:00")
        self.assertEqual(format_countdown(300.0), "05:00")
        self.assertEqual(format_countdown(3599.2), "01:00:00")
        self.assertEqual(format_countdown(3600.0), "01:00:00")
        self.assertEqual(format_countdown(5400.0), "01:30:00")

    def test_format_header_title(self) -> None:
        self.assertEqual(
            format_header_title(PowerAction.DESLIGAR, 300),
            "Desligar \u2022 05:00",
        )
        self.assertEqual(
            format_header_title(PowerAction.REINICIAR, 5400),
            "Reiniciar \u2022 01:30:00",
        )
        self.assertEqual(
            format_header_title(PowerAction.LOGOFF, 45),
            "Logoff \u2022 00:45",
        )

    def test_calculate_progress_extent(self) -> None:
        self.assertEqual(calculate_progress_extent(0.0, 300), 0.0)
        self.assertEqual(calculate_progress_extent(10.0, 0), 0.0)
        self.assertAlmostEqual(calculate_progress_extent(300.0, 300), 359.9)
        self.assertAlmostEqual(calculate_progress_extent(150.0, 300), 179.95)
        self.assertAlmostEqual(calculate_progress_extent(400.0, 300), 359.9)


if __name__ == "__main__":
    unittest.main()
