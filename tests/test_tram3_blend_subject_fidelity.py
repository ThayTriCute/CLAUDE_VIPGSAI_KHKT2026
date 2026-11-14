# -*- coding: utf-8 -*-
"""P0 regression: blend must not apply Toán filters to other subjects; two banks feed pool."""
from __future__ import annotations

import unittest

from services.academic_context import topic_matches
from real_exam_engine import generate_blended_real_exam, get_shard_exams


class TopicMatchUiNoiseTests(unittest.TestCase):
    def test_strips_ui_prefix_and_blocks_cross_grade_generic(self):
        self.assertTrue(topic_matches("Dao động điều hòa", "Dao động điều hòa"))
        self.assertFalse(
            topic_matches(
                "[Lớp 12] Chuyên đề trọng tâm Toán học Lớp 12",
                "Chuyên đề trọng tâm Toán học Lớp 9",
            )
        )


class BlendSubjectFidelityTests(unittest.TestCase):
    def test_physics_ui_chuyen_de_1_does_not_yield_empty_paper(self):
        exam = generate_blended_real_exam(
            "Vật lý",
            12,
            ["[Lớp 12] Chuyên đề 1: Vật lý nhiệt và khí lí tưởng"],
            (12, 4, 6),
        )
        self.assertIsInstance(exam, dict)
        self.assertGreater(len(exam.get("p1") or []), 0)
        # Must not silently become an empty matrix after Toán keyword injection.
        total = sum(len(exam.get(p) or []) for p in ("p1", "p2", "p3"))
        self.assertGreaterEqual(total, 12)

    def test_chemistry_ui_chuyen_de_1_yields_questions(self):
        exam = generate_blended_real_exam(
            "Hóa học",
            12,
            ["[Lớp 12] Chuyên đề 1: Ester - Lipid"],
            (12, 4, 6),
        )
        total = sum(len(exam.get(p) or []) for p in ("p1", "p2", "p3"))
        self.assertGreaterEqual(total, 8)

    def test_gdkt_grade12_reports_empty_honestly(self):
        shard = get_shard_exams("Giáo dục kinh tế và pháp luật", grade=12)
        # Shard file currently holds GDCD 6–9 only; after subject filter + master merge still empty.
        self.assertEqual(len(shard), 0)
        exam = generate_blended_real_exam(
            "Giáo dục kinh tế và pháp luật", 12, None, (12, 4, 6)
        )
        total = sum(len(exam.get(p) or []) for p in ("p1", "p2", "p3"))
        self.assertEqual(total, 0)


if __name__ == "__main__":
    unittest.main()
