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
        self.assertIn("HD Socratic", guide)
        self.assertIn("explain", guide.lower())
        self.assertIn("2;4", guide.replace("$", ""))
        self.assertIn("tần số", guide.lower())
        self.assertNotIn("đáp án là A", guide.lower())
        self.assertNotIn("Me = 3", guide)
        self.assertIn("Câu hỏi định hướng", guide)

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
        self.assertTrue("phân thức" in guide.lower() or "a=2" in guide)
        self.assertNotIn("Chọn A", guide)
        self.assertIn("không giải hộ", guide.lower())

    def test_looks_like_explain(self):
        self.assertTrue(looks_like_explain_solution("Vậy chọn phương án B. Đáp án là B."))
        self.assertFalse(looks_like_explain_solution("Em sẽ xét dấu đạo hàm như thế nào?"))


if __name__ == "__main__":
    unittest.main()
