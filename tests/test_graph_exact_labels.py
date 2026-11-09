"""B1 (owner 05/11/2026): nhãn tọa độ đồ thị phải CHÍNH XÁC, không làm tròn.

Khóa hành vi của bộ định dạng nhãn chính xác trong precision_visual_engine:
- Giá trị hữu tỷ -> phân số/số nguyên đúng (không thập phân xấp xỉ).
- Nghiệm vô tỷ (cực trị) -> căn thức rút gọn đúng, KHÔNG quy về '1.7'.
- Tọa độ VẼ vẫn là số thực (để render được), chỉ NHÃN mới chính xác.
- Có tự-kiểm số học: biểu thức chính xác luôn khớp float -> không bao giờ in nhãn sai.

Thuần numpy/stdlib + import precision_visual_engine (không cần streamlit).
"""
import math
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import precision_visual_engine as P


class TestExactCoordHelpers(unittest.TestCase):
    def test_radical_simplify(self):
        self.assertEqual(P._pve_simplify_radical(12), (2, 3))
        self.assertEqual(P._pve_simplify_radical(8), (2, 2))
        self.assertEqual(P._pve_simplify_radical(9), (3, 1))
        self.assertEqual(P._pve_simplify_radical(0), (0, 1))

    def test_rational_label_is_fraction_not_decimal(self):
        tex = P._pve_rational_label(-2.0 / 3.0)
        self.assertIn("dfrac", tex)
        self.assertNotIn("0.66", tex)
        self.assertEqual(P._pve_rational_label(2.0), "2")

    def test_quadratic_roots_irrational_surd(self):
        roots = P._pve_quadratic_roots(1, -2, -1)  # 1 ± sqrt2
        hi = max(roots, key=lambda r: r.to_float())
        self.assertTrue(math.isclose(hi.to_float(), 1 + math.sqrt(2), rel_tol=1e-9))
        self.assertEqual(hi.to_latex(), r"1 + \sqrt{2}")

    def test_field_eval_matches_float(self):
        import random
        rng = random.Random(1109)
        checks = 0
        for _ in range(2000):
            a, b, c = rng.randint(-5, 5), rng.randint(-6, 6), rng.randint(-6, 6)
            d, e = rng.randint(-5, 5), rng.randint(-6, 6)
            if a == 0 or d == 0:
                continue
            A, B, C = a * d, 2 * a * e, b * e - c * d
            for r in P._pve_quadratic_roots(A, B, C):
                denom = P._PveExactReal.rational(d) * r + P._PveExactReal.rational(e)
                if abs(denom.to_float()) < 1e-9:
                    continue
                x = r.to_float()
                y_float = (a * x * x + b * x + c) / (d * x + e)
                y_exact = (P._PveExactReal.rational(a) * r * r
                           + P._PveExactReal.rational(b) * r
                           + P._PveExactReal.rational(c)) / denom
                _, ok = P._pve_coord_label(y_exact, y_float)
                self.assertTrue(ok, (a, b, c, d, e))
                checks += 1
        self.assertGreater(checks, 300)


class TestTikzLabelsExact(unittest.TestCase):
    def test_rational_1_1_labels_no_decimal(self):
        t = P.build_rational_1_1_tikz(1, 1, 1, -1)  # y=(x+1)/(x-1): x=1,y=1
        self.assertIn("x=1", t)
        self.assertIn("y=1", t)

    def test_rational_2_1_irrational_extrema_exact(self):
        # y=(x^2+2)/(x+1): extrema at x=-1±sqrt3 (irrational)
        t = P.build_rational_2_1_tikz(1, 0, 2, 1, 1)
        self.assertIn(r"\sqrt{3}", t)
        self.assertNotIn(r"\approx", t)   # self-check never fell back
        # drawing coordinates remain decimals so TikZ can still render
        self.assertIn("filldraw[red]", t)

    def test_rational_2_1_rational_extrema_no_approx(self):
        t = P.build_rational_2_1_tikz(1, 1, 1, 1, 1)  # extrema at 0 and -2 (rational)
        self.assertNotIn(r"\approx", t)


if __name__ == "__main__":
    unittest.main()
