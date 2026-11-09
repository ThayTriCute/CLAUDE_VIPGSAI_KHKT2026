"""Nhãn đồ thị Lab không trùng/không đè (ca thật owner 09/11/2026: y = 3x³ − 2x + 1 hiện hai
nhãn (0; 1) vì I trùng giao Oy; chữ O trôi; miền nghiệm Plotly nhãn đè nhau)."""
import ast
import itertools
import math
import re
import sys
import types
import unittest
from fractions import Fraction
from pathlib import Path
from unittest.mock import Mock

from services.plot_labels import label_box, merge_coincident, place_labels, axis_letter_annotations

APP = Path(__file__).resolve().parents[1] / 'app.py'


def boxes(points, shifts, x_range, y_range, w=620, h=435):
    out = []
    for p, (dx, dy) in zip(points, shifts):
        bw, bh = label_box(p['text'])
        cx = (p['x'] - x_range[0]) / (x_range[1] - x_range[0]) * w + dx
        cy = (y_range[1] - p['y']) / (y_range[1] - y_range[0]) * h - dy
        out.append((cx - bw / 2, cy - bh / 2, bw, bh))
    return out


def overlap(a, b):
    return max(0, min(a[0] + a[2], b[0] + b[2]) - max(a[0], b[0])) * max(0, min(a[1] + a[3], b[1] + b[3]) - max(a[1], b[1]))


def cubic_points(a, b, c, d):
    pts = []
    disc = b * b - 3 * a * c
    f = lambda x: a * x ** 3 + b * x ** 2 + c * x + d
    if disc > 0:
        for x, kind in (((-b - math.sqrt(disc)) / (3 * a), 'CĐ' if a > 0 else 'CT'), ((-b + math.sqrt(disc)) / (3 * a), 'CT' if a > 0 else 'CĐ')):
            pts.append(dict(x=x, y=f(x), text=kind + '(x; y)', kind=kind, name=kind))
    xi = -b / (3 * a)
    pts.append(dict(x=xi, y=f(xi), text='I(x; y)', kind='I', name='Tâm ĐX'))
    pts.append(dict(x=0.0, y=float(d), text='(0; d)', kind='Oy', name='Giao Oy'))
    import numpy as np
    for r in np.roots([a, b, c, d]):
        if abs(r.imag) < 1e-9:
            pts.append(dict(x=float(r.real), y=0.0, text='(r; 0)', kind='Ox', name='Giao Ox'))
    return pts


class MergeAndPlaceTests(unittest.TestCase):
    def test_owner_case_single_label_for_I_and_Oy(self):
        pts = cubic_points(3, 0, -2, 1)
        kept = merge_coincident(pts)
        self.assertEqual(sum(1 for p in kept if abs(p['x']) < 1e-12 and abs(p['y'] - 1) < 1e-12), 1)
        center = next(p for p in kept if p['kind'] == 'I')
        self.assertEqual(center['aliases'], ['Giao Oy'])

    def test_no_label_overlaps_across_coefficient_grid(self):
        grid = [-3, -2, -1, 1, 2, 3]
        worst = 0
        for a, b, c, d in itertools.product([1, -1, 3], [-3, 0, 2], [-2, 0, 1], [-2, 0, 1]):
            pts = merge_coincident(cubic_points(a, b, c, d))
            xs = [p['x'] for p in pts] + [0]
            ys = [p['y'] for p in pts] + [0]
            xr = (min(xs) - 2.5, max(xs) + 2.5)
            yr = (min(ys) - 2.5, max(ys) + 2.5)
            bs = boxes(pts, place_labels(pts, xr, yr), xr, yr)
            for i, j in itertools.combinations(range(len(bs)), 2):
                worst = max(worst, overlap(bs[i], bs[j]))
        self.assertEqual(worst, 0)

    def test_double_root_on_extremum_and_origin_point(self):
        kept = merge_coincident(cubic_points(1, 0, -3, 2))  # CT(1; 0) là nghiệm kép
        self.assertEqual(len([p for p in kept if abs(p['x'] - 1) < 1e-6 and abs(p['y']) < 1e-6]), 1)
        kept = merge_coincident(cubic_points(1, 0, -1, 0))  # gốc O vừa là I, giao Oy, giao Ox
        at_origin = [p for p in kept if abs(p['x']) < 1e-9 and abs(p['y']) < 1e-9]
        self.assertEqual(len(at_origin), 1)
        self.assertEqual(at_origin[0]['kind'], 'I')

    def test_axis_letters_anchor_in_pixels(self):
        notes = axis_letter_annotations((-3, 3), (-1.8, 3.4))
        origin = next(n for n in notes if 'O' in n['text'])
        self.assertEqual((origin['x'], origin['y']), (0, 0))
        self.assertTrue(origin['xshift'] < 0 and origin['yshift'] < 0)


class RendererWiringTests(unittest.TestCase):
    def test_render_exact_function_plotly_merges_and_places(self):
        tree = ast.parse(APP.read_text(encoding='utf-8'))
        node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'render_exact_function_plotly')
        ns = {'re': re}
        exec(compile(ast.Module(body=[node], type_ignores=[]), 'app-plot', 'exec'), ns)
        components = types.ModuleType('streamlit.components.v1')
        components.html = Mock()
        sys.modules.setdefault('streamlit', types.ModuleType('streamlit'))
        sys.modules.setdefault('streamlit.components', types.ModuleType('streamlit.components'))
        sys.modules['streamlit.components.v1'] = components
        sys.modules['streamlit.components'].v1 = components
        traces = []
        for name, x, y, text in (('Cực đại (CĐ)', -0.47, 1.63, 'CĐ(-sqrt(2)/3; 4*sqrt(2)/9 + 1)'),
                                 ('Cực tiểu (CT)', 0.47, 0.37, 'CT(sqrt(2)/3; 1 - 4*sqrt(2)/9)'),
                                 ('Tâm ĐX / Điểm uốn I', 0.0, 1.0, 'I(0; 1)'),
                                 ('Giao trục Oy', 0.0, 1.0, '(0; 1)'),
                                 ('Giao trục Ox', -1.0, 0.0, '(-1; 0)')):
            traces.append(types.SimpleNamespace(name=name, x=[x], y=[y], text=[text], mode='markers+text', showlegend=True))
        notes = []
        layout = types.SimpleNamespace(xaxis=types.SimpleNamespace(range=[-3.5, 3.5]),
                                       yaxis=types.SimpleNamespace(range=[-1.8, 3.4]), annotations=[])
        fig = types.SimpleNamespace(data=traces, layout=layout, update_layout=Mock(),
                                    to_html=Mock(return_value='<div></div>'),
                                    add_annotation=lambda **kw: (notes.append(kw), layout.annotations.append(types.SimpleNamespace(**kw))))
        ns['render_exact_function_plotly'](fig)
        self.assertEqual(len(notes), 4)  # I và giao Oy chung một nhãn
        self.assertIn('≡ Giao trục Oy', traces[2].name)
        self.assertFalse(traces[3].showlegend)
        self.assertTrue(all(t.text is None for t in traces))


class RegionPlotlyLabelTests(unittest.TestCase):
    def test_region_vertex_labels_do_not_overlap(self):
        from services.inequality_region import parse_constraints, region_plotly_spec
        for text in ('x>=0; y>=0; 3x+5y<=7', 'x + y <= 4; x - y > -2; 0 <= x <= 3', 'x>=0; y>=0; x+y<=1; x-y<=0.5'):
            spec, _ = region_plotly_spec(parse_constraints(text))
            notes = spec['layout']['annotations']
            xr, yr = spec['layout']['xaxis']['range'], spec['layout']['yaxis']['range']
            pts = [dict(x=n['x'], y=n['y'], text=n['text']) for n in notes]
            bs = boxes(pts, [(n['xshift'], n['yshift']) for n in notes], xr, yr, 600, 470)
            for i, j in itertools.combinations(range(len(bs)), 2):
                self.assertEqual(overlap(bs[i], bs[j]), 0, (text, notes[i]['text'], notes[j]['text']))
            self.assertTrue(all(d.get('mode') != 'markers+text' for d in spec['data']))


if __name__ == '__main__':
    unittest.main()
