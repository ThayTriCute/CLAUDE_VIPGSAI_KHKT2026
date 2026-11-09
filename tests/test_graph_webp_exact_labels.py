"""Luồng #3 (đồ thị trong đề/câu hỏi, matplotlib WebP): nhãn tọa độ CHÍNH XÁC.

Owner 05/11: giao trục ghi tọa độ, giữ tọa độ vô tỷ chính xác, KHÔNG làm tròn.
render_math_graph_to_webp_base64 trước đây chỉ vẽ nét gióng mà không ghi số; nay thêm
nhãn tọa độ chính xác (ℚ(√s)) tại giao trục, chú giải ①②③ khi chật.

app.py chạy UI Streamlit khi import nên trích các hàm thuần (fractions/math) bằng AST.
"""
import ast
import math
import os
import unittest

APP = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app.py")


def _load():
    src = open(APP, encoding="utf-8").read()
    tree = ast.parse(src)
    lines = src.splitlines(keepends=True)
    ns = {"math": math}
    names = {"_g_isqrt_free", "_g_frac", "_g_ftex", "_g_quad_roots",
             "_g_rat_tex_or_none", "_g_approx", "_graph_exact_point_labels", "_GER"}
    for n in tree.body:
        if isinstance(n, ast.ImportFrom) and n.module == "fractions":
            exec(compile("".join(lines[n.lineno - 1:n.end_lineno]), APP, "exec"), ns)
        if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name in names:
            exec(compile("".join(lines[n.lineno - 1:n.end_lineno]), APP, "exec"), ns)
    return ns["_graph_exact_point_labels"]


E = _load()


class TestGraphExactLabels(unittest.TestCase):
    def test_rational_extrema(self):
        # cubic x^3-3x: extrema (-1,2),(1,-2)
        self.assertEqual(E(-1.0, 2.0, 'CĐ/CT', 'cubic', 1, 0, -3, 0, 0), ('-1', '2'))
        self.assertEqual(E(1.0, -2.0, 'CĐ/CT', 'cubic', 1, 0, -3, 0, 0), ('1', '-2'))

    def test_pure_surd_cubic(self):
        # x^3-6x: ±√2, ∓4√2
        xt, yt = E(math.sqrt(2), -4 * math.sqrt(2), 'CĐ/CT', 'cubic', 1, 0, -6, 0, 0)
        self.assertEqual(xt, r'\sqrt{2}')
        self.assertEqual(yt, r'-4\sqrt{2}')

    def test_mixed_surd_cubic(self):
        # x^3-3x^2-3x: extrema 1±√2, y=-5∓4√2
        xt, yt = E(1 + math.sqrt(2), 1 ** 3, 'CĐ/CT', 'cubic', 1, -3, -3, 0, 0)
        self.assertEqual(xt, r'1 + \sqrt{2}')

    def test_func_2_1_surd(self):
        # (x^2+2)/(x+1): extrema -1±√3, y=-2±2√3
        xt, yt = E(-1 + math.sqrt(3), (( -1 + math.sqrt(3))**2 + 2)/((-1+math.sqrt(3))+1),
                   'CĐ/CT', 'func_2_1', 1, 0, 2, 1, 1)
        self.assertEqual(xt, r'-1 + \sqrt{3}')
        self.assertEqual(yt, r'-2 + 2\sqrt{3}')

    def test_rational_detected_full_precision(self):
        # giá trị thật từ phép toán số nguyên (đủ precision) -> phân số chính xác
        xt, yt = E(1.0 / 3.0, -4.0, 'Đỉnh', 'parabola', 3, -2, -3, 0, 0)
        self.assertEqual(xt, r'\dfrac{1}{3}')

    def test_imprecise_value_falls_back_to_approx(self):
        # giá trị cắt cụt không khớp hữu tỷ tới 1e-9 -> ≈, KHÔNG in nhãn sai
        xt, _ = E(0.333333, 2.0, 'Đỉnh', 'parabola', 1, -2, -3, 0, 0)
        self.assertTrue(xt.startswith(r'\approx'))

    def test_render_smoke(self):
        # Nếu có matplotlib thì render thật phải ra ảnh WebP, không rỗng
        try:
            import matplotlib  # noqa
        except Exception:
            self.skipTest("matplotlib absent")
        import json, io, base64
        import numpy as np
        matplotlib = __import__('matplotlib'); matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        src = open(APP, encoding="utf-8").read(); tree = ast.parse(src); lines = src.splitlines(keepends=True)
        ns = {"math": math, "json": json, "io": io, "base64": base64, "np": np, "plt": plt}
        names = {"_g_isqrt_free", "_g_frac", "_g_ftex", "_g_quad_roots", "_g_rat_tex_or_none",
                 "_g_approx", "_graph_exact_point_labels", "render_math_graph_to_webp_base64", "_GER"}
        for n in tree.body:
            if isinstance(n, ast.ImportFrom) and n.module == "fractions":
                exec(compile("".join(lines[n.lineno - 1:n.end_lineno]), APP, "exec"), ns)
            if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name in names:
                exec(compile("".join(lines[n.lineno - 1:n.end_lineno]), APP, "exec"), ns)
        uri = ns["render_math_graph_to_webp_base64"]({"type": "cubic", "a": 1, "b": 0, "c": -6, "d": 0})
        self.assertTrue(uri.startswith("data:image/webp;base64,"))
        self.assertGreater(len(uri), 2000)


if __name__ == "__main__":
    unittest.main()
