# -*- coding: utf-8 -*-
"""Hồi quy chấm điểm theo cấu trúc Bộ (QĐ 764 lớp 12 + luyện tập 6–11)."""
from __future__ import annotations

import unittest

from services.academic_context import academic_context, subjects_for_grade
from services.curriculum_policy import assessment_profile
from services.scoring_service import calculate_part2_statement_score, grade_exam_by_profile


def _exam(n1, n2, n3, stmts=4):
    return {
        "p1": [{"q": f"q{i}", "opt": ["A", "B", "C", "D"], "ans": "A"} for i in range(n1)],
        "p2": [
            {"q": f"p2-{i}", "stmts": [{"t": f"s{j}", "a": True} for j in range(stmts)]}
            for i in range(n2)
        ],
        "p3": [{"q": f"p3-{i}", "ans": "1"} for i in range(n3)],
    }


def _perfect(exam):
    ans = {}
    for i, _ in enumerate(exam["p1"]):
        ans[f"p1_{i}"] = "A"
    for i, q in enumerate(exam["p2"]):
        for j, _ in enumerate(q["stmts"]):
            ans[f"p2_{i}_{j}"] = "Đúng"
    for i, _ in enumerate(exam["p3"]):
        ans[f"p3_{i}"] = "1"
    return ans


class BoScoringMatrixTests(unittest.TestCase):
    def test_grade12_profiles_match_qd764_families(self):
        expected = {
            "Toán học": ((12, 4, 6), (3.0, 4.0, 3.0), 90),
            "Tiếng Anh": ((40, 0, 0), (10.0, 0.0, 0.0), 50),
            "Vật lý": ((18, 4, 6), (4.5, 4.0, 1.5), 50),
            "Hóa học": ((18, 4, 6), (4.5, 4.0, 1.5), 50),
            "Sinh học": ((18, 4, 6), (4.5, 4.0, 1.5), 50),
            "Địa lý": ((18, 4, 6), (4.5, 4.0, 1.5), 50),
            "Lịch sử": ((24, 4, 0), (6.0, 4.0, 0.0), 50),
            "Tin học": ((24, 4, 0), (6.0, 4.0, 0.0), 50),
            "Công nghệ": ((24, 4, 0), (6.0, 4.0, 0.0), 50),
            "Giáo dục kinh tế và pháp luật": ((24, 4, 0), (6.0, 4.0, 0.0), 50),
            "Ngữ văn": ((0, 0, 0), (4.0, 6.0, 0.0), 120),
        }
        for subject, (counts, weights, minutes) in expected.items():
            profile = assessment_profile(subject, 12)
            self.assertEqual(profile["counts"], counts, subject)
            self.assertEqual(profile["weights"], weights, subject)
            self.assertEqual(profile["minutes"], minutes, subject)
            self.assertEqual(profile["scope"], "graduation_reference", subject)

    def test_perfect_score_ten_all_auto_subjects_all_grades(self):
        for grade in range(6, 13):
            for subject in subjects_for_grade(grade):
                if subject == "Ngữ văn":
                    continue
                profile = assessment_profile(subject, grade)
                counts = profile["counts"]
                if counts == (0, 0, 0):
                    continue
                exam = _exam(*counts)
                scored = grade_exam_by_profile(exam, _perfect(exam), subject, grade)
                self.assertAlmostEqual(
                    scored["total"], 10.0, places=6, msg=f"{subject} L{grade}"
                )
                if grade == 12 and counts[1] > 0 and abs(profile["weights"][1] / counts[1] - 1.0) < 1e-9:
                    self.assertTrue(scored["p2_absolute_ladder"], msg=subject)
                    self.assertIn("QĐ 764", scored["p2_label"])

    def test_part2_ladder_and_toan12_partial(self):
        self.assertEqual(
            [calculate_part2_statement_score(k) for k in range(5)],
            [0.0, 0.1, 0.25, 0.5, 1.0],
        )
        exam = _exam(12, 4, 6)
        ans = _perfect(exam)
        ans["p2_0_2"] = "Sai"
        ans["p2_0_3"] = "Sai"
        scored = grade_exam_by_profile(exam, ans, "Toán học", 12)
        self.assertAlmostEqual(scored["score_p2"], 3.25, places=6)
        self.assertAlmostEqual(scored["total"], 9.25, places=6)

    def test_integrated_subjects_blocked_outside_band(self):
        with self.assertRaises(ValueError):
            academic_context("Vật lý", 8)
        with self.assertRaises(ValueError):
            academic_context("Khoa học tự nhiên", 12)
        with self.assertRaises(ValueError):
            academic_context("Lịch sử & Địa lý", 11)


if __name__ == "__main__":
    unittest.main()
