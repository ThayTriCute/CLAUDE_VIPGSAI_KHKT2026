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

    def test_physics_kinetic_theory_negation_mc_midwifery(self):
        """Ảnh anh: phát biểu không đúng về mô hình ĐHPT — đỡ đẻ sát ngữ liệu, không lộ đáp."""
        q = {
            "q": (
                "Phát biểu nào sau đây không đúng khi nói về mô hình động học phân tử của chất khí?"
            ),
            "opt": [
                "A. Nhiệt độ càng cao thì các phân tử khí chuyển động càng nhanh.",
                "B. Các phân tử khí chuyển động hỗn loạn không ngừng về mọi phía.",
                "C. Các phân tử khí ở rất gần nhau và có lực tương tác rất mạnh.",
                "D. Thể tích của các phân tử khí rất nhỏ so với khoảng cách giữa chúng.",
            ],
            "ans": "C",
            "explain": "Đáp án C vì lực tương tác khí rất yếu.",
            "level": "NB",
        }
        guide = build_tram3_socratic_guide(q, subject="Vật lý", grade_num=10)
        low = guide.lower()
        self.assertNotIn("hướng đi từ đúng ngữ liệu", low)
        self.assertNotIn("bám đúng ngữ liệu câu này — chi tiết", low)
        self.assertTrue(
            "động học" in low or "phân tử" in low or "chất khí" in low or "khí" in low
        )
        self.assertTrue(
            "hỗn loạn" in low
            or "lực tương tác" in low
            or "khoảng cách" in low
            or "pV" in guide
            or "nrt" in low
        )
        # Negation midwifery + theme pillars from options (F VIP style)
        self.assertTrue("không đúng" in low or "lệch" in low)
        self.assertIn("nhiệt độ", low)
        self.assertIn("hỗn loạn", low)
        self.assertIn("tương tác", low)
        self.assertTrue("kích thước" in low or "khoảng cách" in low)
        self.assertIn("1.", guide)
        self.assertIn("2.", guide)
        self.assertIn("3.", guide)
        self.assertNotIn("nóng chảy", low)  # không lẫn trụ nhiệt chuyển thể
        # Không lộ đáp / nguyên văn phương án sai / chọn hộ
        self.assertNotIn("đáp án c", low)
        self.assertNotIn("chọn c", low)
        self.assertNotIn("vậy chọn", low)
        self.assertNotIn("lực tương tác rất mạnh", low)
        self.assertNotIn("ở rất gần nhau", low)
        self.assertFalse(looks_like_explain_solution(guide))

    def test_informatics_cpu_style_not_generic(self):
        guide = build_tram3_socratic_guide({
            "q": "Phát biểu nào sau đây không đúng khi nói về CPU của máy tính?",
            "opt": [
                "A. CPU thực hiện xử lý lệnh.",
                "B. CPU lưu trữ lâu dài mọi tệp như ổ cứng.",
                "C. CPU làm việc với bộ nhớ trong khi chạy chương trình.",
                "D. Tốc độ CPU ảnh hưởng thời gian xử lý.",
            ],
            "ans": "B",
        }, subject="Tin học", grade_num=6)
        low = guide.lower()
        self.assertNotIn("hướng đi từ đúng ngữ liệu", low)
        self.assertTrue("cpu" in low or "không đúng" in low or "lệch" in low)

    def test_biology_conceptual_uses_topic_not_echo(self):
        guide = build_tram3_socratic_guide({
            "q": "Phát biểu nào sau đây đúng khi nói về quang hợp ở thực vật?",
            "opt": [
                "A. Quang hợp chỉ xảy ra ban đêm.",
                "B. Quang hợp tạo glucose và giải phóng O2.",
                "C. Quang hợp không cần ánh sáng.",
                "D. Quang hợp chỉ xảy ra ở rễ.",
            ],
            "ans": "B",
        }, subject="Sinh học", grade_num=11)
        low = guide.lower()
        self.assertNotIn("hướng đi từ đúng ngữ liệu", low)
        self.assertIn("quang hợp", low)


if __name__ == "__main__":
    unittest.main()
