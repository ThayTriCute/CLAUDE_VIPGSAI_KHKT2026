# -*- coding: utf-8 -*-
"""HD Socratic Trạm 3 ≠ explain; bám số liệu câu hỏi; không lộ đáp án."""
from __future__ import annotations

import unittest

from services.socratic_context import build_tram3_socratic_guide, looks_like_explain_solution


class Tram3SocraticGuideTests(unittest.TestCase):
    def test_ignores_explain_and_uses_question_numbers(self):
        q = {
            "q": r"Cho mẫu ghép nhóm với tần số; biết khoảng $[2;4)$ có $n_i=5$. Tìm trung vị.",
            "opt": ["A. 3", "B. 4", "C. 5", "D. 6"],
            "ans": "A",
            "explain": "Vậy đáp án là A vì Me=3 sau khi thay số.",
            "hint": "Vậy đáp án là A. Ta tính được Me = 3.",
            "mslgn_data": {"groups": ["[0;2)", "[2;4)", "[4;6)"], "freq": [3, 5, 2]},
        }
        guide = build_tram3_socratic_guide(q, subject="Toán học", grade_num=12)
        self.assertIn("tần số", guide.lower())
        self.assertNotIn("đáp án là A", guide.lower())
        self.assertNotIn("Me = 3", guide)
        self.assertLess(len(guide), 500)

    def test_graph_question_mentions_asymptote_steps_not_option_body(self):
        q = {
            "q": "Đường cong dưới đây là đồ thị của hàm số nào?",
            "opt": [r"$y=\dfrac{2x+3}{x-1}$", r"$y=\dfrac{x^{2}-x+3}{x-1}$"],
            "ans": "A",
            "explain": "Chọn A vì tiệm cận đứng x=1 và giao Oy là -3.",
            "f": {"type": "func_1_1", "a": 2, "b": 3, "c": 1, "d": -1},
        }
        guide = build_tram3_socratic_guide(q, subject="Toán học", grade_num=12)
        self.assertIn("tiệm cận", guide.lower())
        self.assertNotIn("Chọn A", guide)
        self.assertLess(len(guide), 500)

    def test_domain_and_parabola_vertex_guide_without_answer(self):
        domain = build_tram3_socratic_guide({
            "q": r"Tập xác định của hàm số $y=\sqrt{2x-4}$ là:",
            "opt": [r"A. $[2;+\infty)$", r"B. $(-\infty;2]$", r"C. $\mathbb{R}$", r"D. $(2;+\infty)$"],
            "ans": "A",
            "explain": "Điều kiện 2x-4>=0 nên x>=2. Chọn A.",
        }, subject="Toán học", grade_num=10)
        self.assertIn(r"\sqrt{2x-4}", domain)
        self.assertIn("2x-4", domain)
        self.assertNotIn("[2;+", domain)
        self.assertNotIn("x\\ge 2", domain)
        self.assertNotIn("x>=2", domain)
        self.assertNotIn("Chọn A", domain)
        vertex = build_tram3_socratic_guide({
            "q": r"Tọa độ đỉnh $I$ của parabol $(P): y=x^2-4x+3$ là:",
            "opt": [r"A. $I(2;-1)$", r"B. $I(2;1)$", r"C. $I(-2;15)$", r"D. $I(4;3)$"],
            "ans": "A",
            "explain": "x=-b/2a=2, y=-1. Chọn A.",
        }, subject="Toán học", grade_num=10)
        self.assertIn("x^2-4x+3", vertex)
        self.assertIn("-\\dfrac{b}{2a}", vertex)
        self.assertGreaterEqual(vertex.count("\n"), 4)
        self.assertNotIn("I(2;-1)", vertex)
        self.assertNotIn("y=-1", vertex)
        self.assertNotIn("Chọn A", vertex)

    def test_quadratic_max_quotes_this_function_and_interval(self):
        stem = r"Giá trị lớn nhất của hàm số bậc hai $y=-x^2+6x-5$ trên đoạn $[0;5]$ bằng bao nhiêu?"
        guide = build_tram3_socratic_guide({
            "q": stem, "ans": "4", "explain": "x=3, f(3)=4. GTLN = 4.", "level": "VD",
        }, subject="Toán học", grade_num=10)
        compact = guide.replace(" ", "")
        self.assertIn("-x^2+6x-5", compact)
        self.assertIn("[0;5]", compact)
        self.assertNotIn("[a;b]", guide)
        self.assertNotIn("Các số liệu", guide)
        self.assertNotIn("không phải explain", guide.lower())
        self.assertNotIn("x=3", compact)
        self.assertNotIn("f(3)", guide)
        self.assertNotIn("=4", compact)
        self.assertGreaterEqual(guide.count("\n"), 4)
        plain = build_tram3_socratic_guide({
            "q": "Giá trị lớn nhất của hàm số bậc hai y = -x^2 + 6x - 5 trên đoạn [0; 5] bằng bao nhiêu?",
            "ans": "4",
        }, subject="Toán học", grade_num=10)
        plain_compact = plain.replace(" ", "")
        self.assertIn("-x^2+6x-5", plain_compact)
        self.assertIn("[0;5]", plain_compact)
        self.assertNotIn("=4", plain_compact)

    def test_compound_interest_uses_given_data_without_result(self):
        guide = build_tram3_socratic_guide({
            "q": "Một người tiết kiệm 100 triệu đồng với lãi suất 6%/năm, lãi kép. Sau 3 năm nhận được bao nhiêu triệu đồng?",
            "ans": "119",
            "explain": "100*(1.06)**3 ≈ 119. Chọn 119.",
            "level": "VD",
        }, subject="Toán học", grade_num=10)
        self.assertIn("100", guide)
        self.assertIn("6%", guide)
        self.assertIn("3", guide)
        self.assertIn("A=P(1+r)", guide.replace(" ", ""))
        self.assertNotIn("119", guide)
        self.assertGreaterEqual(guide.count("\n"), 3)

    def test_looks_like_explain(self):
        self.assertTrue(looks_like_explain_solution("Vậy chọn phương án B. Đáp án là B."))
        self.assertFalse(looks_like_explain_solution("Em sẽ xét dấu đạo hàm như thế nào?"))


if __name__ == "__main__":
    unittest.main()
