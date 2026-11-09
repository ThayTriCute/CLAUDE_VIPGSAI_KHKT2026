"""Trạm 1 (09/11/2026): AI vẽ đồ thị bằng ký tự trong ``` và viết vạch kép BBT dạng thoát Markdown.

Ca thật owner báo: bài "Khảo sát ba hàm số cơ bản, Toán 12 KNTT".
"""
import ast
import html
import re
import unittest
from pathlib import Path
from unittest.mock import patch

from services import function_visuals

ASCII_CUBIC = """```
      y
      |
  2 -+---. CĐ (-1,2)
      |  / \\
      | /   \\
--|---|/--|--|---|--> x
 -\\sqrt{3}-1 0 1  \\sqrt{3}
      |\\    /
 -2 -+--`-/ CT (1,-2)
      |
```"""

ASCII_HOMOGRAPHIC = """```
       |  x = -1
    y  |  :
    |  |  :
 2 -+--+--+======== y = 2
    |  |  :
  0 +--+--+-----> x
    | -1  : 1/2
-1 -+--.  :
    |   \\ :
```"""

PYTHON_CODE = """```python
for i in range(3):
    print(i)
```"""


def _fake_figure(source):
    source = source.replace(' ', '')
    known = {'y=x^3-3x': 'FIG_CUBIC', 'y=\\dfrac{2x+1}{x+1}': 'FIG_HOMO'}
    for key, name in known.items():
        if source.rstrip('.').startswith(key):
            return '<section class="verified-function-visuals">' + name + '</section>'
    return ''


class AsciiPlotDetectionTests(unittest.TestCase):
    def test_owner_reported_drawings_are_detected(self):
        self.assertTrue(function_visuals.is_ascii_plot(ASCII_CUBIC))
        self.assertTrue(function_visuals.is_ascii_plot(ASCII_HOMOGRAPHIC))

    def test_code_and_tables_are_not_drawings(self):
        self.assertFalse(function_visuals.is_ascii_plot(PYTHON_CODE))
        self.assertFalse(function_visuals.is_ascii_plot("```\nKết luận: hàm số đồng biến.\n```"))


class AsciiPlotReplacementTests(unittest.TestCase):
    def test_each_drawing_gets_the_figure_of_its_own_function(self):
        lesson = ("Ví dụ 1. Khảo sát $y = x^3 - 3x$.\n\n" + ASCII_CUBIC +
                  "\n\nVí dụ 2. Khảo sát $y=\\dfrac{2x+1}{x+1}$. Tiệm cận ngang $y = 2$.\n\n" + ASCII_HOMOGRAPHIC + "\n")
        with patch.object(function_visuals, 'explicit_function_visuals', side_effect=_fake_figure):
            result = function_visuals.with_function_visuals(lesson, 'Khảo sát ba hàm số cơ bản', lesson)
        self.assertNotIn('```', result)
        self.assertNotIn('\\sqrt{3}-1', result)
        self.assertEqual(result.count('FIG_CUBIC'), 1)
        self.assertEqual(result.count('FIG_HOMO'), 1)
        self.assertLess(result.index('FIG_CUBIC'), result.index('Ví dụ 2'))
        self.assertGreater(result.index('FIG_HOMO'), result.index('Ví dụ 2'))

    def test_bbt_then_drawing_keeps_one_verified_figure(self):
        table = ('<div style="x"><div style="h">📐 Bảng Biến Thiên Chuẩn Sư Phạm (CT GDPT 2018)</div>'
                 '<table><tr><td>x</td></tr><tr><td>y′</td></tr><tr><td>y</td></tr></table></div>')
        lesson = ("Ví dụ 1. $y = x^3 - 3x$.\n\n" + table + "\n\n" + ASCII_CUBIC +
                  "\n\nVí dụ 2. $y=\\dfrac{2x+1}{x+1}$.\n\n" + ASCII_HOMOGRAPHIC)
        with patch.object(function_visuals, 'explicit_function_visuals', side_effect=_fake_figure):
            result = function_visuals.with_function_visuals(lesson, 'Khảo sát ba hàm số cơ bản', lesson)
        self.assertEqual(result.count('FIG_CUBIC'), 1)
        self.assertNotIn('📐', result)
        self.assertNotIn('```', result)

    def test_exported_pre_block_is_replaced_too(self):
        body = ('<p>Ví dụ 1. <span class="lesson-math" data-tex="y=x^3-3x">$y=x^3-3x$</span></p>'
                '<pre><code>' + html.escape(ASCII_CUBIC.strip('`').strip('\n')) + '</code></pre>'
                '<p>Ví dụ 2. <span class="lesson-math" data-tex="y=\\dfrac{2x+1}{x+1}">x</span></p>')
        with patch.object(function_visuals, 'explicit_function_visuals', side_effect=_fake_figure):
            result = function_visuals.with_function_visuals(body, 'Khảo sát ba hàm số cơ bản', '$y = x^3 - 3x$ và $y=\\dfrac{2x+1}{x+1}$')
        self.assertNotIn('<pre>', result)
        self.assertLess(result.index('FIG_CUBIC'), result.index('Ví dụ 2'))
        self.assertEqual(result.count('FIG_HOMO'), 1)

    def test_code_blocks_are_preserved(self):
        lesson = "$y = x^3 - 3x$\n\n" + PYTHON_CODE + "\n\n$y=\\dfrac{2x+1}{x+1}$\n"
        with patch.object(function_visuals, 'explicit_function_visuals', side_effect=_fake_figure):
            result = function_visuals.with_function_visuals(lesson, 'Khảo sát ba hàm số cơ bản', lesson)
        self.assertIn(PYTHON_CODE, result)

    def test_drawing_without_recognisable_function_is_kept(self):
        lesson = "Hàm số bất kỳ.\n\n" + ASCII_CUBIC
        with patch.object(function_visuals, 'explicit_function_visuals', side_effect=_fake_figure):
            self.assertEqual(function_visuals.with_function_visuals(lesson, 'Chủ đề', lesson), lesson)


class EscapedDoubleBarTests(unittest.TestCase):
    """Markdown bắt buộc thoát '|' trong ô bảng: '\\|\\|' và '\\|' phải là vạch tiệm cận đứng."""

    @classmethod
    def setUpClass(cls):
        tree = ast.parse(Path('app.py').read_text(encoding='utf-8'))
        ns = {'re': re, 'html': html}
        for node in tree.body:
            if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id.startswith('_MOET_') for t in node.targets):
                exec(compile(ast.Module(body=[node], type_ignores=[]), 'app-support', 'exec'), ns)
        for name in ('_normalize_bbt_discontinuity', '_moet_plaintext_math', '_render_math_html_token',
                     '_parse_bbt_cells_safe', '_normalize_moet_bbt_grid', '_build_svg_bbt_from_rows'):
            node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name)
            exec(compile(ast.Module(body=[node], type_ignores=[]), 'app-bbt', 'exec'), ns)
        cls.ns = ns

    def grid(self, rows):
        return self.ns['_normalize_moet_bbt_grid'](*[self.ns['_parse_bbt_cells_safe'](r) for r in rows])

    def test_owner_reported_homographic_table(self):
        for bar in ('\\|\\|', '\\|', '||', '\\Vert\\Vert', '\\parallel'):
            with self.subTest(bar=bar):
                g = self.grid(["| $x$ | $-\\infty$ | | $-1$ | | $+\\infty$ |",
                               "| $y'$ | | $+$ | $" + bar + "$ | $+$ | |",
                               "| $y$ | $2$ | $\\nearrow$ | $+\\infty " + bar + " -\\infty$ | $\\nearrow$ | $2$ |"])
                self.assertEqual(g['yp_at_pts'], ['', '||', ''])
                self.assertEqual(g['y_at_pts'][1].replace('$', '').split('||')[0].strip(), '+\\infty')

    def test_owner_reported_quadratic_over_linear_table(self):
        g = self.grid(["| $x$ | $-\\infty$ | | $0$ | | $1$ | | $2$ | | $+\\infty$ |",
                       "| $y'$ | | $+$ | $0$ | $-$ | $\\|\\|$ | $-$ | $0$ | $+$ | |",
                       "| $y$ | $-\\infty$ | $\\nearrow$ | $-1$ | $\\searrow$ | $-\\infty \\|\\| +\\infty$ | $\\searrow$ | $3$ | $\\nearrow$ | $+\\infty$ |"])
        self.assertEqual(g['yp_at_pts'], ['', '0', '||', '0', ''])
        out = self.ns['_build_svg_bbt_from_rows'](*[self.ns['_parse_bbt_cells_safe'](r) for r in [
            "| $x$ | $-\\infty$ | | $0$ | | $1$ | | $2$ | | $+\\infty$ |",
            "| $y'$ | | $+$ | $0$ | $-$ | $\\|\\|$ | $-$ | $0$ | $+$ | |",
            "| $y$ | $-\\infty$ | $\\nearrow$ | $-1$ | $\\searrow$ | $-\\infty \\|\\| +\\infty$ | $\\searrow$ | $3$ | $\\nearrow$ | $+\\infty$ |"]])
        # left limit −∞ sits at the bottom (flex-end), right limit +∞ at the top (flex-start)
        asym = re.search(r'align-items:(flex-\w+);[^>]*>([^<]*)</div><div[^>]*border-left[^>]*></div><div[^>]*align-items:(flex-\w+);[^>]*>([^<]*)<', out)
        self.assertIsNotNone(asym)
        self.assertEqual((asym[1], asym[3]), ('flex-end', 'flex-start'))
        self.assertNotIn('\\|', out)

    def test_export_normalizes_escaped_bars_only_in_bbt_tables(self):
        from services.lesson_export import lesson_body_html
        bbt = ("| $x$ | $-\\infty$ | | $-1$ | | $+\\infty$ |\n|---|---|---|---|---|---|\n"
               "| $y'$ | | $+$ | $\\|\\|$ | $+$ | |\n| $y$ | $2$ | $\\nearrow$ | $+\\infty \\|\\| -\\infty$ | $\\nearrow$ | $2$ |")
        out = lesson_body_html(bbt)
        self.assertIn('data-tex="||"', out)
        self.assertIn('data-tex="+\\infty || -\\infty"', out)
        other = "| Toán tử | Ý nghĩa |\n|---|---|\n| `a \\| b` | hoặc |\n| x \\| y | phân tách |"
        self.assertNotIn('||', lesson_body_html(other))

    def test_absolute_values_are_not_turned_into_asymptotes(self):
        n = self.ns['_normalize_bbt_discontinuity']
        for text in ('$\\|x\\|$', '$y=\\|x-1\\|$', '$\\left\\|x\\right\\|$'):
            self.assertEqual(n(text), text)


if __name__ == '__main__':
    unittest.main()
