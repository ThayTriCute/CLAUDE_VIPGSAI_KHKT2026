# -*- coding: utf-8 -*-
"""Ngôn ngữ đề/bài theo môn — cổng shared đa môn × lớp."""
import unittest

from services.academic_context import subjects_for_grade
from services.curriculum_policy import (
    exam_generation_request,
    exam_prompt,
    item_display_language_issue,
    item_language_policy,
    policy_prompt,
    prepare_exam_for_delivery,
    validate_exam_item_language,
)


class ItemLanguagePolicyTests(unittest.TestCase):
    def test_policy_codes(self):
        self.assertEqual(item_language_policy("Tiếng Anh")["code"], "en")
        self.assertEqual(item_language_policy("Toán học")["code"], "vi")
        self.assertIn("tiếng Việt", item_language_policy("Vật lý")["prompt"])

    def test_detects_english_math_stems(self):
        self.assertEqual(
            item_display_language_issue(
                "Find the maximum value of the function $f(x)=-x^4+2x^2+3$ on $[0;2]$.",
                "Toán học",
            ),
            "english_stem_outside_english_subject",
        )
        self.assertEqual(
            item_display_language_issue(
                "The variance of a grouped data set is calculated as $s^2=4.5$. What is the standard deviation?",
                "Toán học",
            ),
            "english_stem_outside_english_subject",
        )
        self.assertEqual(
            item_display_language_issue(
                "Cho hàm số $y=f(x)$ có bảng biến thiên. Hàm số đồng biến trên khoảng nào?",
                "Toán học",
            ),
            "",
        )
        # English subject: EN stems OK; VI stems not hard-blocked (prompt-led).
        self.assertEqual(
            item_display_language_issue("Choose the correct answer to complete the sentence.", "Tiếng Anh"),
            "",
        )
        self.assertEqual(
            item_display_language_issue(
                "Cho hàm số $y=x^2$. Mệnh đề nào sau đây đúng?",
                "Tiếng Anh",
            ),
            "",
        )

    def test_prompts_carry_language_rule_all_subjects(self):
        for grade in (6, 9, 12):
            for subject in subjects_for_grade(grade):
                with self.subTest(subject=subject, grade=grade):
                    prompt = policy_prompt(subject, grade, 3)
                    if subject == "Tiếng Anh":
                        self.assertIn("tiếng anh", prompt.lower())
                    else:
                        self.assertIn("tiếng việt", prompt.lower())
                        self.assertIn("không viết đề", prompt.lower())

    def test_exam_prompt_math_forbids_english_stems(self):
        text = exam_prompt("Toán học", 12, ["Ứng dụng đạo hàm"], (12, 4, 6), "7883")
        self.assertIn("tiếng Việt", text)
        self.assertIn("không viết đề", text.lower())
        system, _ = exam_generation_request("Toán học", 12, ["Ứng dụng đạo hàm"], (12, 4, 6), "7883")
        self.assertIn("tiếng Việt", system)

    def test_delivery_rejects_english_math_exam(self):
        exam = {
            "code": "7883",
            "subject": "Toán học",
            "grade": 12,
            "p1": [{
                "q": "Find the maximum value of the function $f(x)=x^2$ on the interval $[0;2]$.",
                "opt": ["A. 1", "B. 2", "C. 3", "D. 4"],
                "ans": "B",
                "topic": "t",
                "explain": "x",
            }],
            "p2": [],
            "p3": [],
        }
        with self.assertRaisesRegex(ValueError, "ngôn ngữ không khớp"):
            prepare_exam_for_delivery(exam, "Toán học", 12, 90)

    def test_delivery_accepts_vietnamese_math_exam(self):
        exam = {
            "code": "1011",
            "subject": "Toán học",
            "grade": 12,
            "p1": [{
                "q": "Cho hàm số $y=x^2$. Giá trị lớn nhất trên $[0;2]$ bằng?",
                "opt": ["A. 1", "B. 2", "C. 3", "D. 4"],
                "ans": "D",
                "topic": "t",
                "explain": "x",
            }],
            "p2": [],
            "p3": [],
        }
        out = prepare_exam_for_delivery(exam, "Toán học", 12, 90)
        self.assertEqual(out["subject"], "Toán học")

    def test_p2_english_statement_rejected(self):
        exam = {
            "code": "1",
            "subject": "Toán học",
            "grade": 12,
            "p1": [],
            "p2": [{
                "q": "Cho hàm số phân thức.",
                "stmts": [
                    {"t": "The function is increasing on its domain.", "a": False},
                    {"t": "Hàm số nghịch biến trên từng khoảng xác định.", "a": True},
                    {"t": "Có tiệm cận đứng.", "a": True},
                    {"t": "Có tiệm cận ngang.", "a": True},
                ],
                "topic": "t",
                "explain": "x",
            }],
            "p3": [],
        }
        with self.assertRaisesRegex(ValueError, "ngôn ngữ không khớp"):
            validate_exam_item_language(exam, "Toán học")


if __name__ == "__main__":
    unittest.main()
