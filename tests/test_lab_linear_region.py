"""Phòng Lab Toán: miền nghiệm hệ BPT bậc nhất hai ẩn (ca thật owner 09/11/2026:
'MIỀN NGHIỆM GIỚI HẠN BỞI X>=0; Y>=0; 3X+5Y<=7' từng ra sơ đồ tư duy chữ vỡ)."""
import ast
import json
import re
import unittest
from fractions import Fraction as F
from pathlib import Path
from unittest.mock import Mock
from xml.etree import ElementTree

from services.inequality_region import analyse, linear_region_request, parse_constraints, region_svg

OWNER = 'MIỀN NGHIỆM GIỚI HẠN BỞI X>=0; Y>=0; 3X+5Y<=7'
SVG = '{http://www.w3.org/2000/svg}'


class ParseAndGeometryTests(unittest.TestCase):
    def test_owner_case_exact_vertices(self):
        constraints = parse_constraints(OWNER)
        self.assertEqual(constraints, [(1, 0, '>=', 0), (0, 1, '>=', 0), (3, 5, '<=', 7)])
        info = analyse(constraints)
        self.assertEqual(info['status'], 'bounded')
        self.assertEqual(sorted(info['vertices']), [(0, 0), (0, F(7, 5)), (F(7, 3), 0)])

    def test_notations(self):
        self.assertEqual(parse_constraints('x ≥ 0, y ≤ 2x + 1 và 0 <= x <= 3'),
                         [(1, 0, '>=', 0), (-2, 1, '<=', 1), (1, 0, '<=', 3)])  # x ≥ 0 lặp được gộp
        self.assertEqual(parse_constraints(r'$\frac{1}{2}x + y \le 3$'), [(F(1, 2), 1, '<=', 3)])
        self.assertEqual(parse_constraints('7 >= 3x + 5y'), [(3, 5, '<=', 7)])
        self.assertEqual(parse_constraints('2x − y > 1'), [(2, -1, '>', 1)])

    def test_not_linear_or_not_a_region_request(self):
        for text in ('vẽ đồ thị y = x^2', 'x^2 + y <= 1', 'xy >= 1', 'Khảo sát y = x^3 - 3x trên -1 <= x <= 2'):
            self.assertIsNone(linear_region_request(text, 'Toán học'), text)
        self.assertIsNone(linear_region_request(OWNER, 'Ngữ văn'))
        self.assertEqual(linear_region_request(OWNER, 'Toán học'),
                         {'type': 'linear_region', 'constraints': ['x ≥ 0', 'y ≥ 0', '3x + 5y ≤ 7']})

    def test_status_cases(self):
        self.assertEqual(analyse(parse_constraints('x > 0; y > 0; x + y < 0'))['status'], 'empty')
        self.assertEqual(analyse(parse_constraints('x + y <= 2; x + y >= 2'))['status'], 'degenerate')
        unbounded = analyse(parse_constraints('x + y <= 4; x - y > -2; 0 <= x <= 3'))
        self.assertEqual(unbounded['status'], 'unbounded')
        self.assertEqual(sorted(unbounded['vertices']), [(0, 2), (1, 3), (3, 1)])

    def test_svg_is_valid_and_labels_exact(self):
        svg, info = region_svg(parse_constraints(OWNER))
        root = ElementTree.fromstring(svg)
        texts = ' '.join(node.text or '' for node in root.iter(SVG + 'text'))
        self.assertIn('A(0; 7/5)', texts)
        self.assertIn('B(7/3; 0)', texts)
        self.assertIn('Miền nghiệm: phần KHÔNG bị gạch', texts)
        self.assertNotRegex(texts, r'\d\.\d{2,}')
        dashed = parse_constraints('2x - y > 1; miền nghiệm')
        self.assertIn('stroke-dasharray', region_svg(dashed)[0])


class LabWiringTests(unittest.TestCase):
    def test_renderer_draws_region_not_mindmap(self):
        from tests.test_expert_patch_regressions import load_function
        st = Mock()
        st.session_state = {}
        st.radio.return_value = 'SVG chính xác'
        render = load_function('render_smart_lab', st=st)
        render(linear_region_request(OWNER, 'Toán học'), 'Toán học')
        exported = st.download_button.call_args.args[1].decode('utf-8')
        self.assertIn('B(7/3; 0)', exported)
        latex = st.latex.call_args.args[0]
        self.assertIn(r'3x + 5y \le 7', latex)
        vertices = st.markdown.call_args_list[-1].args[0]
        self.assertIn(r'\dfrac{7}{3}', vertices)

    def test_plotly_mode_uses_same_exact_data(self):
        from tests.test_expert_patch_regressions import load_function
        st = Mock()
        st.session_state = {}
        st.radio.return_value = 'Plotly tương tác'
        figure = Mock(side_effect=lambda spec: spec)
        render = load_function('render_smart_lab', st=st, go=Mock(Figure=figure))
        render(linear_region_request(OWNER, 'Toán học'), 'Toán học')
        self.assertEqual(st.radio.call_args.args[1], ['SVG chính xác', 'Plotly tương tác'])
        spec = st.plotly_chart.call_args.args[0]
        vertex_trace = spec['data'][-1]
        self.assertEqual(sorted(vertex_trace['text']), ['A(0; 7/5)', 'B(7/3; 0)', 'O'])
        self.assertTrue(any(d.get('line', {}).get('dash') == 'solid' for d in spec['data']))

    def test_plotly_spec_is_accepted_by_plotly(self):
        try:
            import plotly.graph_objects as go
        except ImportError:
            self.skipTest('plotly chỉ có trên CI/Cloud')
        from services.inequality_region import region_plotly_spec
        for text in (OWNER, '2x - y > 1; miền nghiệm', 'x + y <= 4; x - y > -2; 0 <= x <= 3'):
            fig = go.Figure(region_plotly_spec(parse_constraints(text))[0])
            self.assertTrue(fig.to_json())

    def test_local_route_runs_before_ai_and_prompt_has_type(self):
        src = (Path(__file__).resolve().parents[1] / 'app.py').read_text(encoding='utf-8')
        self.assertIn('explicit_local_model = (explicit_light_model or linear_region_request(lab_command, subject)', src)
        self.assertIn('"type": "linear_region"', src)
        self.assertNotIn("decode('unicode_escape'", src)

    def test_mermaid_recovery_keeps_vietnamese(self):
        raw = '"graph LR\\n Root[\\"🎯 Miền nghiệm 3x+5y<=7\\"] --> A[\\"1. Điều kiện\\"]"'
        self.assertIn('Miền nghiệm', json.loads(raw))
        # Cách cũ (unicode_escape) chính là nguyên nhân chữ vỡ trong ảnh owner.
        self.assertIn('Miá»', raw.encode('utf-8').decode('unicode_escape'))


if __name__ == '__main__':
    unittest.main()
