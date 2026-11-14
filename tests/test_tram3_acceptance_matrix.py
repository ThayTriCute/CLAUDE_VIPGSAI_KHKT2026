# -*- coding: utf-8 -*-
"""Nghiệm thu Trạm 3: profile + blend + chấm đúng môn/lớp (giáo viên khó tính)."""
from __future__ import annotations

import unittest

import real_exam_engine as ree
from services.academic_context import subjects_for_grade
from services.curriculum_policy import assessment_profile
from services.scoring_service import grade_exam_by_profile


def _perfect_from_exam(exam: dict) -> dict:
    ans = {}
    for i, q in enumerate(exam.get("p1") or []):
        ans[f"p1_{i}"] = (q.get("opt") or ["A"])[0] if mcq_letter(q) is None else opt_by_letter(q, mcq_letter(q))
        # Prefer keyed ans when present
        letter = str(q.get("ans") or "").strip().upper()
        if letter in "ABCD" and q.get("opt"):
            idx = ord(letter) - 65
            if 0 <= idx < len(q["opt"]):
                ans[f"p1_{i}"] = q["opt"][idx]
            else:
                ans[f"p1_{i}"] = letter
        elif letter:
            ans[f"p1_{i}"] = letter
    for i, q in enumerate(exam.get("p2") or []):
        for j, stmt in enumerate(q.get("stmts") or []):
            from qa_runtime import normalize_bool
            expected = normalize_bool(stmt["a"] if "a" in stmt else stmt.get("ans"))
            ans[f"p2_{i}_{j}"] = "Đúng" if expected else "Sai" if expected is False else "Chưa chọn"
    for i, q in enumerate(exam.get("p3") or []):
        ans[f"p3_{i}"] = str(q.get("ans") or "").strip()
    return ans


def mcq_letter(q):
    letter = str(q.get("ans") or "").strip().upper()
    return letter if letter in "ABCD" else None


def opt_by_letter(q, letter):
    idx = ord(letter) - 65
    opts = q.get("opt") or []
    return opts[idx] if 0 <= idx < len(opts) else letter


class Tram3AcceptanceMatrixTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        ree._RECENT_QUESTION_COOLDOWN.clear()

    def test_profiles_cover_every_valid_subject_grade(self):
        for grade in range(6, 13):
            for subject in subjects_for_grade(grade):
                profile = assessment_profile(subject, grade)
                self.assertIn(profile["scope"], {"practice", "graduation_reference"})
                self.assertEqual(len(profile["counts"]), 3)
                self.assertEqual(len(profile["weights"]), 3)
                self.assertGreater(profile["minutes"], 0)
                if grade == 12 and subject != "Ngữ văn":
                    self.assertEqual(sum(profile["weights"]), 10.0, msg=f"{subject} L12")

    def test_blend_and_grade_smoke_selected_cells(self):
        """Smoke tạo đề + chấm trên các ô đại diện (không quét hết bank nặng)."""
        cells = [
            ("Toán học", 12, ["[Lớp 12] Chuyên đề 1"], (6, 2, 2)),
            ("Vật lý", 12, ["[Lớp 12] Nội năng và nhiệt động lực học"], (6, 2, 2)),
            ("Hóa học", 12, None, (6, 2, 0)),
            ("Lịch sử", 12, None, (8, 2, 0)),
            ("Tiếng Anh", 12, None, (10, 0, 0)),
            ("Toán học", 6, None, (6, 2, 2)),
            ("Khoa học tự nhiên", 8, None, (6, 2, 2)),
            ("Lịch sử & Địa lý", 9, None, (6, 2, 2)),
            ("Tin học", 10, None, (6, 2, 0)),
            ("Giáo dục kinh tế và pháp luật", 11, None, (6, 2, 0)),
        ]
        for subject, grade, topics, counts in cells:
            with self.subTest(subject=subject, grade=grade):
                ree._RECENT_QUESTION_COOLDOWN.clear()
                exam = ree.generate_blended_real_exam(subject, grade, topics, counts)
                self.assertIsInstance(exam, dict)
                self.assertEqual(exam.get("subject"), subject)
                # Không lẫn môn: mọi câu có subject thì phải khớp (nếu gắn)
                for part in ("p1", "p2", "p3"):
                    for q in exam.get(part) or []:
                        declared = q.get("subject")
                        if declared:
                            from services.academic_context import canonical_subject
                            self.assertEqual(canonical_subject(declared), subject)
                total_q = sum(len(exam.get(p) or []) for p in ("p1", "p2", "p3"))
                if total_q == 0:
                    self.skipTest(f"empty bank cell {subject} L{grade}")
                scored = grade_exam_by_profile(exam, _perfect_from_exam(exam), subject, grade)
                self.assertGreaterEqual(scored["total"], 0.0)
                self.assertLessEqual(scored["total"], 10.0)
                # Làm đúng hết (trừ câu thiếu ans) → điểm phần hiện có phải > 0 nếu có ans
                if scored["p1_total"] and scored["p1_correct"] == scored["p1_total"]:
                    self.assertGreater(scored["score_p1"], 0)


if __name__ == "__main__":
    unittest.main()
