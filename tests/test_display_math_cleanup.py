import ast
from pathlib import Path
import re
import unittest
from services.text_boundaries import remove_empty_math, chemical_display_markdown


class DisplayMathCleanupTests(unittest.TestCase):
    def test_real_deep_cleaner_preserves_complete_rate_equation_across_two_passes(self):
        tree = ast.parse(Path('real_exam_engine.py').read_text(encoding='utf-8'))
        node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'deep_clean_pua_and_artifacts')
        scope = {'re': re}
        exec(compile(ast.Module(body=[node], type_ignores=[]), 'real-cleaner', 'exec'), scope)
        formula = r'$$v=-\frac{1}{a}\frac{\Delta C_A}{\Delta t}=\frac{1}{c}\frac{\Delta C_C}{\Delta t}$$'
        for _ in range(2):
            self.assertEqual(scope['deep_clean_pua_and_artifacts'](formula), formula)
        self.assertEqual(remove_empty_math('A $ $ B $$  $$ C'), 'A  B  C')
        code = '```text\n$ $ $$ $$\n```'
        self.assertEqual(remove_empty_math(code), code)

    def test_fractional_chemical_coefficient_renders_without_changing_atoms(self):
        text = chemical_display_markdown(r'$\ce{N2O5(g) -> 2NO2(g) + 1/2 O2(g)}$')
        self.assertNotIn('Công thức cần đối chiếu', text)
        self.assertIn(r'\frac{1}{2}', text)
        self.assertIn(r'\mathrm{O}_{2}', text)
        invalid = chemical_display_markdown(r'$\ce{1/0 O2}$')
        self.assertIn('Công thức cần đối chiếu', invalid)
