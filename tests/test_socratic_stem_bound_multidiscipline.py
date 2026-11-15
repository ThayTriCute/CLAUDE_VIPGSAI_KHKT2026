# -*- coding: utf-8 -*-
"""HD Socratic bám ngữ liệu đa môn — đỡ đẻ ý tưởng, không lộ đáp án, không generic."""
from __future__ import annotations

import unittest

from services.socratic_context import (
    build_tram3_socratic_guide,
    build_socratic_guide,
    looks_like_explain_solution,
)


class StemBoundSocraticTests(unittest.TestCase):
    def test_physics_melting_not_generic_and_no_answer_letter(self):
        q = {
            "q": (
                "Nhiệt lượng cần cung cấp để làm nóng chảy hoàn toàn một khối lượng $m$ "
                "chất rắn ở nhiệt độ nóng chảy được tính theo công thức:"
            ),
            "opt": [
                r"A. $Q = UIt$",
                r"B. $Q = \lambda m$",
                r"C. $Q = Lm$",
                r"D. $Q = mc\Delta t$",
            ],
            "ans": "B",
            "explain": "Đáp án B vì Q=λm.",
            "hint": "Vậy chọn B.",
            "level": "NB",
        }
        guide = build_tram3_socratic_guide(q, subject="Vật lý", grade_num=12)
        low = guide.lower()
        self.assertNotIn("bám đúng ngữ liệu câu này — chi tiết", low)
        self.assertNotIn("đối chiếu khái niệm đúng môn với đúng ngữ liệu này", low)
        self.assertIn("nóng chảy", low)
        self.assertTrue("chuyển thể" in low or "nhiệt độ không đổi" in low or "λ" in guide or "lambda" in low)
        # Không lộ chữ đáp / chọn hộ
        self.assertNotIn("đáp án B", low)
        self.assertNotIn("chọn B", low)
        self.assertNotIn("vậy chọn", low)
        self.assertFalse(looks_like_explain_solution(guide))
        # Phân biệt với hóa hơi / ΔT / điện — không chỉ một công thức = đáp án
        self.assertTrue(
            "hóa hơi" in low or "delta" in low or "Δ" in guide or "uit" in low or "điện" in low
        )

    def test_tram1_question_keys_normalized(self):
        q = {
            "question": "Nhiệt lượng để làm nóng chảy hoàn toàn khối lượng m ở nhiệt độ nóng chảy:",
            "options": ["A. Q=UIt", "B. Q=λm", "C. Q=Lm", "D. Q=mcΔt"],
            "correct": "B",
        }
        guide = build_socratic_guide(q, subject="Vật lý", grade_num=10)
        self.assertIn("nóng chảy", guide.lower())
        self.assertNotIn("Bám đúng ngữ liệu câu này — chi tiết", guide)

    def test_math_gtln_still_quotes_function(self):
        guide = build_tram3_socratic_guide({
            "q": r"Giá trị lớn nhất của hàm số bậc hai $y=-x^2+6x-5$ trên đoạn $[0;5]$ bằng bao nhiêu?",
            "ans": "4",
            "level": "VD",
        }, subject="Toán học", grade_num=10)
        self.assertIn("[0;5]", guide.replace(" ", ""))
        self.assertIn("-x^2+6x-5", guide.replace(" ", ""))
        self.assertNotIn("GTLN =", guide)

    def test_chemistry_ester_uses_anchor_not_generic(self):
        guide = build_tram3_socratic_guide({
            "q": "Trong phản ứng xà phòng hóa ester RCOOR', sản phẩm muối tạo thành có công thức nào?",
            "opt": ["A. RCOONa", "B. R'OH", "C. RCOOH", "D. NaCl"],
            "ans": "A",
        }, subject="Hóa học", grade_num=12)
        low = guide.lower()
        self.assertNotIn("bám đúng ngữ liệu câu này — chi tiết", low)
        self.assertTrue("ester" in low or "xà phòng" in low or "rcoor" in low)

    def test_alias_equals_tram3_builder(self):
        q = {"q": "Cho y=x^3-3x. Tìm cực trị.", "ans": "A"}
        self.assertEqual(
            build_socratic_guide(q, subject="Toán học", grade_num=12),
            build_tram3_socratic_guide(q, subject="Toán học", grade_num=12),
        )


if __name__ == "__main__":
    unittest.main()
