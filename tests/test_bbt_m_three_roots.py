# -*- coding: utf-8 -*-
"""BBT extrema must drive m-interval for exactly 3 distinct roots (multi-grade Toán)."""
import unittest

from services.curriculum_policy import repair_bbt_m_three_roots_question, repair_exam_bbt_m_consistency
from services.math_conditions import math_condition_conflict


BBT_MIN1_MAX4 = """| $x$ | $-\\infty$ | $-1$ | $1$ | $+\\infty$ |
| $y'$ |  | $+$ | $0$ | $-$ | $0$ | $+$ |  |
| $y$ | $-\\infty$ | $4$ | $1$ | $+\\infty$ |"""


class BbtMThreeRootsTests(unittest.TestCase):
    def _question(self, **extra):
        q = {
            "subject": "Toán học",
            "q": (
                "Cho hàm số bậc ba $y = f(x)$ có bảng biến thiên như sau. "
                "Tìm tất cả các giá trị thực của tham số $m$ để phương trình "
                "$f(x) - m = 0$ có đúng 3 nghiệm phân biệt."
            ),
            "bbt": BBT_MIN1_MAX4,
            "opt": [
                "A. $0 \\leq m \\leq 4$",
                "B. $m = 0$ hoặc $m = 4$",
                "C. $0 < m < 4$",
                "D. $m < 0$ hoặc $m > 4$",
            ],
            "ans": "C",
        }
        q.update(extra)
        return q

    def test_detects_wrong_open_interval_using_zero(self):
        conflict = math_condition_conflict(self._question())
        self.assertEqual(conflict, "bbt_m_three_roots_options_mismatch")

    def test_repair_rewrites_to_ymin_m_ymax(self):
        fixed = repair_bbt_m_three_roots_question(self._question(), "Toán học", 12)
        opts = " ".join(str(o) for o in fixed["opt"])
        self.assertIn("1 < m < 4", opts.replace("$", ""))
        self.assertNotIn("0 < m < 4", opts.replace("$", ""))
        self.assertEqual(fixed.get("ans"), "C")
        self.assertFalse(math_condition_conflict(fixed))

    def test_tram1_field_names(self):
        q = {
            "subject": "Toán học",
            "question": self._question()["q"],
            "bbt": BBT_MIN1_MAX4,
            "options": self._question()["opt"],
            "correct": "C",
        }
        fixed = repair_bbt_m_three_roots_question(q, "Toán học", 11)
        self.assertIn("1 < m < 4", " ".join(str(o) for o in fixed["options"]).replace("$", ""))
        self.assertEqual(fixed["correct"], "C")

    def test_consistent_question_untouched(self):
        q = self._question()
        q["opt"][2] = "C. $1 < m < 4$"
        self.assertEqual(math_condition_conflict(q), "")
        fixed = repair_bbt_m_three_roots_question(q, "Toán học", 12)
        self.assertEqual(fixed["opt"][2], q["opt"][2])

    def test_exam_batch_repair(self):
        exam = {"p1": [self._question()], "p2": [], "p3": []}
        out = repair_exam_bbt_m_consistency(exam, "Toán học", 12)
        self.assertIn("1 < m < 4", " ".join(str(o) for o in out["p1"][0]["opt"]).replace("$", ""))

    def test_non_math_subject_skipped(self):
        q = self._question(subject="Ngữ văn")
        self.assertEqual(math_condition_conflict(q), "")


if __name__ == "__main__":
    unittest.main()
