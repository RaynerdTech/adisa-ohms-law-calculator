# Automated tests for the 12 Ohm's law and power calculation methods.
# Run from the project folder: python -m unittest discover -s tests -v

import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ohms_law import (calculate_electrical, derive_metrics, display_quantity,
                      parse_number, substituted_formula)


class ElectricalCalculationsTest(unittest.TestCase):
    def test_all_twelve_methods(self):
        # The same ideal circuit has 12 V, 2 A, 6 ohms and 24 W.
        examples = [
            ("Voltage", 0, 2, 6, 12),
            ("Voltage", 1, 24, 2, 12),
            ("Voltage", 2, 24, 6, 12),
            ("Current", 0, 12, 6, 2),
            ("Current", 1, 24, 12, 2),
            ("Current", 2, 24, 6, 2),
            ("Resistance", 0, 12, 2, 6),
            ("Resistance", 1, 12, 24, 6),
            ("Resistance", 2, 24, 2, 6),
            ("Power", 0, 12, 2, 24),
            ("Power", 1, 2, 6, 24),
            ("Power", 2, 12, 6, 24),
        ]
        for target, method, a, b, expected in examples:
            with self.subTest(target=target, method=method):
                self.assertAlmostEqual(calculate_electrical(target, method, a, b), expected)

    def test_zero_is_allowed_where_physically_defined(self):
        self.assertEqual(calculate_electrical("Voltage", 0, 0, 100), 0)
        self.assertEqual(calculate_electrical("Power", 1, 0, 100), 0)

    def test_zero_denominators_rejected(self):
        for target, method, a, b in [
            ("Voltage", 1, 12, 0), ("Current", 0, 12, 0),
            ("Current", 1, 24, 0), ("Current", 2, 24, 0),
            ("Resistance", 0, 12, 0), ("Resistance", 1, 12, 0),
            ("Resistance", 2, 24, 0), ("Power", 2, 12, 0),
        ]:
            with self.subTest(target=target, method=method):
                with self.assertRaises(ValueError):
                    calculate_electrical(target, method, a, b)

    def test_bad_values_rejected(self):
        for text in ("", "hello", "nan", "inf", "-2"):
            with self.subTest(text=text):
                with self.assertRaises(ValueError):
                    parse_number(text, "Voltage")
        for value in (-1, math.inf, math.nan):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    calculate_electrical("Power", 0, value, 3)
        with self.assertRaises(ValueError):
            calculate_electrical("Unknown", 0, 2, 3)
        with self.assertRaises(ValueError):
            calculate_electrical("Power", 10, 2, 3)

    def test_reconstructs_full_circuit_metrics(self):
        metrics = derive_metrics("Voltage", 0, 2, 6, 12)
        self.assertEqual(metrics, {"Voltage": 12, "Current": 2,
                                   "Resistance": 6, "Power": 24})

    def test_engineering_display(self):
        self.assertEqual(display_quantity(1200, "Ω"), "1.2 kΩ")
        self.assertEqual(display_quantity(0.002, "A"), "2 mA")
        self.assertEqual(display_quantity(None, "V"), "—")
        self.assertIn("12", substituted_formula("Voltage", 0, 2, 12))


if __name__ == "__main__":
    unittest.main()
