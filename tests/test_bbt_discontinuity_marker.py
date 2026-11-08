"""Khóa fix: ký hiệu tiệm cận đứng BBT phải là vạch đôi VECTOR, không lọt mã TeX.

Lỗi gốc (owner phát hiện 09/11/2026): model đôi khi xuất \\parallel/∥/║ thay vì '||'
trong hàng giá trị BBT. Bộ dựng SVG không nhận ra -> (1) in '\\parallel' thô ra hình,
(2) dồn 'giới-hạn-trái ∥ giới-hạn-phải' vào một ô nên ±∞ đặt sai cao độ.

Fix: _normalize_bbt_discontinuity() quy mọi biến thể về '||' tại các chokepoint, để
renderer vẽ vạch đôi bằng nét vector (đồng nhất Android/iOS/Windows/Mac, không phụ thuộc
font) và tách đúng hai giới hạn một phía.

app.py chạy UI Streamlit khi import nên test trích riêng các hàm BBT thuần (re/html/math).
"""
import ast
import html
import math
import os
import re
import unittest

APP = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app.py")
_NEEDED = ["_normalize_bbt_discontinuity", "_parse_bbt_cells_safe",
           "_render_math_html_token", "_normalize_moet_bbt_grid",
           "_build_svg_bbt_from_rows"]


def _load_bbt_funcs():
    src = open(APP, encoding="utf-8").read()
    tree = ast.parse(src)
    lines = src.splitlines(keepends=True)
    ns = {"re": re, "html": html, "math": math}
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name in _NEEDED:
            seg = "".join(lines[node.lineno - 1:node.end_lineno])
            exec(compile(seg, APP, "exec"), ns)
    for n in _NEEDED:
        assert n in ns, "missing " + n
    return ns


NS = _load_bbt_funcs()


class TestDiscontinuityMarker(unittest.TestCase):
    def test_normalizer_folds_all_variants(self):
        norm = NS["_normalize_bbt_discontinuity"]
        self.assertEqual(norm(r"-\infty \parallel +\infty"), r"-\infty || +\infty")
        self.assertEqual(norm("−∞ ∥ +∞"), "−∞ || +∞")
        self.assertEqual(norm("a ║ b"), "a || b")
        self.assertEqual(norm(r"d \Vert e"), "d || e")

    def test_normalizer_preserves_pipes_and_absvalue(self):
        norm = NS["_normalize_bbt_discontinuity"]
        self.assertEqual(norm("|x|"), "|x|")                 # trị tuyệt đối
        self.assertEqual(norm("| x | 0 | 1 |"), "| x | 0 | 1 |")  # cột bảng

    def _render_image1(self):
        rows = [
            r"| x | $-\infty$ | 0 | 1 | 2 | $+\infty$ |",
            r"| y' | | + | 0 | $-$ | \parallel | $-$ | 0 | + | |",
            r"| y | $-\infty$ | \nearrow | $-1$ | \searrow | $-\infty$ \parallel $+\infty$ "
            r"| \searrow | 3 | \nearrow | $+\infty$ |",
        ]
        dr = [NS["_parse_bbt_cells_safe"](l) for l in rows]
        return NS["_build_svg_bbt_from_rows"](dr[0], dr[1], dr[2])

    def test_no_raw_tex_leaks(self):
        svg = self._render_image1()
        self.assertNotIn("\\parallel", svg)
        self.assertNotIn("parallel", svg.lower())

    def test_vector_double_bar_device_independent(self):
        svg = self._render_image1()
        # vạch đôi vẽ bằng border (nét vector), không phải glyph font
        self.assertIn("border-left:1.8px solid #dc2626", svg)
        self.assertIn("border-right:1.8px solid #dc2626", svg)

    def test_one_sided_limits_split_and_positioned(self):
        svg = self._render_image1()
        self.assertGreaterEqual(svg.count("−∞"), 1)
        self.assertGreaterEqual(svg.count("+∞"), 1)
        # cao độ ±∞ do chiều biến thiên quyết định (không dồn giữa)
        self.assertTrue("vertical-align:bottom" in svg or "vertical-align:top" in svg)


if __name__ == "__main__":
    unittest.main()
