"""Khóa fix: _render_math_html_token không để lọt mã LaTeX thô ra màn hình học sinh.

Mở rộng từ fix marker tiệm cận: map ký hiệu LaTeX phổ biến ĐA MÔN (so sánh, mũi tên,
tập hợp, hình học, Hy Lạp, hàm) -> Unicode BMP (phổ cập Android/iOS/Windows/Mac), và
gỡ mọi macro chưa ánh xạ. app.py chạy UI Streamlit khi import nên trích hàm thuần.
"""
import ast
import html
import math
import os
import re
import unittest

APP = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app.py")


def _load():
    src = open(APP, encoding="utf-8").read()
    tree = ast.parse(src)
    lines = src.splitlines(keepends=True)
    ns = {"re": re, "html": html, "math": math}
    # module-level _MOET_* tables
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id.startswith("_MOET") for t in node.targets
        ):
            exec(compile("".join(lines[node.lineno - 1:node.end_lineno]), APP, "exec"), ns)
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name in (
            "_render_math_html_token", "_moet_plaintext_math"
        ):
            exec(compile("".join(lines[node.lineno - 1:node.end_lineno]), APP, "exec"), ns)
    return ns["_render_math_html_token"], ns["_moet_plaintext_math"]


render, plaintext = _load()
_BACKSLASH_MACRO = re.compile(r"\\[a-zA-Z]+")


class TestNoTexLeak(unittest.TestCase):
    def _no_leak(self, out):
        self.assertFalse(_BACKSLASH_MACRO.search(out), f"raw TeX leaked: {out!r}")

    def test_comparison_relations(self):
        out = render(r"x \leq 3 \neq 5 \geq 2")
        self.assertIn("≤", out); self.assertIn("≠", out); self.assertIn("≥", out)
        self._no_leak(out)

    def test_le_does_not_eat_leftarrow(self):
        out = render(r"a \le b \leftarrow c")
        self.assertIn("≤", out); self.assertIn("←", out)
        self._no_leak(out)

    def test_chemistry_arrows(self):
        out = render(r"A \rightarrow B \rightleftharpoons C")
        self.assertIn("→", out); self.assertIn("⇌", out)
        self._no_leak(out)

    def test_greek_and_funcs(self):
        out = render(r"\theta \tau \tan \omega")
        self.assertIn("θ", out); self.assertIn("τ", out); self.assertIn("tan", out); self.assertIn("ω", out)
        self._no_leak(out)

    def test_sets_and_logic(self):
        out = render(r"x \in \mathbb{R} \cup \mathbb{Q}")
        self.assertIn("∈", out); self.assertIn("ℝ", out); self.assertIn("∪", out); self.assertIn("ℚ", out)
        self._no_leak(out)

    def test_degree_superscript(self):
        self.assertIn("°", render(r"90^\circ"))
        self.assertIn("°", render(r"45^{\circ}"))

    def test_structural_sqrt_frac_still_work(self):
        out = render(r"\sqrt{2}")
        self.assertIn("√", out)
        out2 = render(r"\dfrac{1}{2}")
        self.assertIn("border-bottom", out2)  # phân số dọc vẫn dựng
        self._no_leak(out); self._no_leak(out2)

    def test_unmapped_macro_stripped_not_leaked(self):
        out = render(r"\vec{v} + \overrightarrow{AB}")
        self.assertIn("v", out); self.assertIn("AB", out)
        self._no_leak(out)

    def test_infinity_and_plusminus_preserved(self):
        out = render(r"-\infty \pm +\infty")
        self.assertIn("∞", out); self.assertIn("±", out)
        self._no_leak(out)

    def test_plain_text_untouched(self):
        self.assertEqual(render("3"), "3")
        self.assertIn("|x|", render("|x|"))


class TestPlaintextMathForImages(unittest.TestCase):
    """_moet_plaintext_math: ô BBT ảnh WebP (matplotlib vẽ chữ thuần) — Unicode, không lọt TeX."""

    def _no_leak(self, out):
        self.assertFalse(_BACKSLASH_MACRO.search(out), f"raw TeX leaked: {out!r}")

    def test_sqrt_becomes_unicode(self):
        self.assertEqual(plaintext(r"\sqrt{2}"), "√(2)")
        self.assertEqual(plaintext(r"\sqrt3"), "√3")
        self._no_leak(plaintext(r"y = \sqrt{3}"))

    def test_fraction_flattened(self):
        self.assertEqual(plaintext(r"\dfrac{1}{2}"), "1/2")
        self._no_leak(plaintext(r"\frac{a}{b}"))

    def test_irrational_extremum_no_leak(self):
        # cực trị vô tỷ ở ô BBT ảnh phải hiện √, không phải '\sqrt{2}'
        out = plaintext(r"-2\sqrt{2}")
        self.assertIn("√", out)
        self._no_leak(out)

    def test_symbols_and_degree(self):
        self.assertIn("≤", plaintext(r"x \leq 3"))
        self.assertIn("°", plaintext(r"90^\circ"))
        self.assertIn("α", plaintext(r"\alpha"))
        self._no_leak(plaintext(r"\theta \geq \pi"))

    def test_infinity_preserved(self):
        self.assertEqual(plaintext("+∞"), "+∞")
        self.assertEqual(plaintext("3"), "3")


if __name__ == "__main__":
    unittest.main()
