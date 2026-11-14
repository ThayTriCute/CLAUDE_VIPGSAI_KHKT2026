# -*- coding: utf-8 -*-
"""Hồi quy nhẹ: cấu hình Trạm 3 (counts/weights/minutes) khớp môn×lớp — không AppTest nặng."""
from __future__ import annotations

import unittest

from services.academic_context import subjects_for_grade
from services.curriculum_policy import assessment_profile
from services.scoring_service import grade_exam_by_profile, part2_ladder_caption


class Tram3ProfileControlsTests(unittest.TestCase):
    def test_every_subject_grade_has_consistent_controls(self):
        issues = []
        for grade in range(6, 13):
            for subject in subjects_for_grade(grade):
                p = assessment_profile(subject, grade)
                c1, c2, c3 = p["counts"]
                w1, w2, w3 = p["weights"]
                if any(x < 0 for x in (c1, c2, c3, w1, w2, w3)):
                    issues.append(f"neg {subject} L{grade}")
                if grade < 12 and p["scope"] != "practice":
                    issues.append(f"scope!=practice {subject} L{grade}")
                if grade == 12 and p["scope"] != "graduation_reference":
                    issues.append(f"scope!=grad_ref {subject} L{grade}")
                if subject == "Tiếng Anh" and (c2 or c3 or w2 or w3):
                    # Anh chỉ TN; weight khác có thể bị scale khi thiếu phần — counts P2/P3 phải 0
                    if c2 or c3:
                        issues.append(f"EN has P2/P3 counts {subject} L{grade}")
                if subject == "Ngữ văn" and (c1 or c2 or c3):
                    issues.append(f"NV should use doc/viet not p1/p2/p3 counts {subject} L{grade}")
                if grade == 12 and subject == "Toán học":
                    self.assertEqual(p["counts"], (12, 4, 6))
                    self.assertEqual(p["weights"], (3.0, 4.0, 3.0))
                    self.assertEqual(p["minutes"], 90)
                if grade == 12 and c2 > 0 and abs(w2 / c2 - 1.0) < 1e-9:
                    self.assertIn("QĐ 764", part2_ladder_caption(w2 / c2))
                # Chấm đề rỗng không nổ
                empty = {"p1": [], "p2": [], "p3": []}
                scored = grade_exam_by_profile(empty, {}, subject, grade)
                self.assertEqual(scored["total"], 0.0)
        self.assertEqual(issues, [], msg="; ".join(issues))

    def test_thcs_integrated_vs_thpt_split(self):
        self.assertIn("Khoa học tự nhiên", subjects_for_grade(7))
        self.assertIn("Lịch sử & Địa lý", subjects_for_grade(9))
        self.assertNotIn("Vật lý", subjects_for_grade(8))
        self.assertIn("Vật lý", subjects_for_grade(10))
        self.assertNotIn("Khoa học tự nhiên", subjects_for_grade(12))
        self.assertIn("Giáo dục công dân", subjects_for_grade(6))
        self.assertIn("Giáo dục kinh tế và pháp luật", subjects_for_grade(12))


if __name__ == "__main__":
    unittest.main()
