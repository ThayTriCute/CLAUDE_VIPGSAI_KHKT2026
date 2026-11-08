import math
import unittest

from services.lab_scope import oscillator_equation_latex


class OscillatorEquationTests(unittest.TestCase):
    def test_source_frequency_and_negative_phase_are_not_rounded_to_other_model(self):
        equation = oscillator_equation_latex(4, math.pi / 2, -math.pi / 6)
        self.assertIn(r'\frac{\pi}{2}t', equation)
        self.assertIn(r'-\frac{\pi}{6}', equation)
        self.assertNotIn('1.6t', equation)
        self.assertIn(r'\mathrm{cm}', equation)

    def test_non_pi_coefficients_preserve_selected_value(self):
        equation = oscillator_equation_latex(4.25, 1.5707, 0.123456789)
        self.assertIn('4.25', equation)
        self.assertIn('1.5707t', equation)
        self.assertIn('0.123456789', equation)
        self.assertNotIn(r'\pi', equation)

    def test_invalid_physical_parameters_are_rejected(self):
        for values in [(0, 2, 0), (-1, 2, 0), (1, 0, 0),
                       (1, -2, 0), (1, math.inf, 0), (1, 2, math.nan)]:
            with self.assertRaises(ValueError):
                oscillator_equation_latex(*values)


if __name__ == '__main__':
    unittest.main()
