import unittest
import ast
import html
from html.parser import HTMLParser
from pathlib import Path

from services.bbt_display import render_compact_bbt


class Cells(HTMLParser):
    def __init__(self):
        super().__init__(); self.rows=[]
    def handle_starttag(self, tag, attrs):
        if tag == 'tr': self.rows.append(0)
        elif tag in ('td', 'th'): self.rows[-1] += 1


class TestBBTDisplay(unittest.TestCase):
    raw = "x | -inf | -1 | 1 | +inf\ny' | + | 0 | - | 0 | +\ny | -inf | 3 | -1 | +inf"

    def test_live_table_has_aligned_points_signs_and_variation_arrows(self):
        rendered = render_compact_bbt(self.raw); parser=Cells(); parser.feed(rendered)
        self.assertEqual(parser.rows, [8, 8, 8])
        self.assertNotIn('inf', rendered)
        self.assertEqual(rendered.count('↗'), 2)
        self.assertEqual(rendered.count('↘'), 1)
        self.assertIn('3</td>', rendered)
        self.assertIn('-1</td>', rendered)

    def test_incomplete_conflicting_or_unsupported_data_is_not_guessed(self):
        for raw in (self.raw.replace(' | 3 | -1', ' | -9 | 20'),
                    self.raw.replace(' | 0 | -', ' | -'),
                    self.raw.replace(' | -1 | 1', ' | 1 | -1'),
                    self.raw.replace('3 | -1', '<script>bad()</script> | -1'),
                    'x | -inf | +inf\ny | -inf | +inf'):
            with self.subTest(raw=raw): self.assertEqual(render_compact_bbt(raw), '')

    def test_equivalent_infinity_spellings_and_no_input_mutation(self):
        raw=self.raw.replace('-inf', r'-\infty').replace('+inf', '+∞')
        before=raw
        self.assertIn('−∞', render_compact_bbt(raw))
        self.assertEqual(raw, before)

    def test_noncalculus_table_is_left_to_existing_renderer(self):
        self.assertEqual(render_compact_bbt('Năm | 2025 | 2026\nSản lượng | 30 | 40'), '')

    def app_renderer(self):
        source=Path(__file__).resolve().parents[1].joinpath('app.py')
        node=next(n for n in ast.parse(source.read_text(encoding='utf-8')).body
                  if isinstance(n, ast.FunctionDef) and n.name == 'question_visual_html')
        namespace={'html': html, 'sanitize_svg_for_markdown': lambda s:s,
                   'render_math_graph_to_webp_base64': lambda model:'data:image/webp;base64,TEST'}
        exec(compile(ast.Module(body=[node], type_ignores=[]), str(source), 'exec'), namespace)
        return namespace['question_visual_html']

    def test_app_keeps_other_supplied_visuals_alongside_aligned_table(self):
        question={'bbt': self.raw, 'mslgn_data': {'groups':['[1;2)'], 'freq':[7]},
                  'f': {'type':'func_3', 'a':1, 'b':0, 'c':-3, 'd':1}}
        rendered=self.app_renderer()(question)
        self.assertIn('gsai-compact-bbt', rendered)
        self.assertIn('[1;2)', rendered)
        self.assertIn('data:image/webp;base64,TEST', rendered)
        self.assertEqual(question['bbt'], self.raw)

    def test_unsupported_bbt_keeps_escaped_fallback_in_app(self):
        rendered=self.app_renderer()({'bbt':'x | <script>bad()</script>\ny | data'})
        self.assertIn('&lt;script&gt;', rendered)
        self.assertNotIn('<script>', rendered)
