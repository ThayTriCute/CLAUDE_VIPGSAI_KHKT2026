# -*- coding: utf-8 -*-
"""Trạm 3 — chấm điểm thống nhất theo assessment_profile (đa môn × lớp 6–12)."""
import unittest

from services.academic_context import subjects_for_grade
from services.curriculum_policy import assessment_profile
from services.scoring_service import grade_exam_by_profile, part2_ladder_caption
from qa_runtime import canonicalize_mcq_key, mcq_answer_matches, short_answer_matches


def synth_exam(subject, grade, counts):
    c1, c2, c3 = counts
    exam = {"code": "1011", "subject": subject, "grade": grade, "p1": [], "p2": [], "p3": []}
    for i in range(c1):
        exam["p1"].append({
            "q": f"Câu {i+1}?",
            "opt": ["A. a", "B. b", "C. c", "D. d"],
            "ans": "B",
            "topic": "T",
            "explain": "x",
        })
    for i in range(c2):
        exam["p2"].append({
            "q": f"Ngữ liệu {i+1}",
            "stmts": [{"t": f"m{j}", "a": j % 2 == 0} for j in range(4)],
            "topic": "T",
            "explain": "x",
        })
    for i in range(c3):
        exam["p3"].append({"q": f"TLN {i+1}?", "ans": "2.5", "topic": "T", "explain": "x"})
    return exam


def perfect_answers(exam):
    answers = {}
    for idx, q in enumerate(exam.get("p1") or []):
        answers[f"p1_{idx}"] = q["opt"][ord(str(q["ans"]).upper()) - ord("A")]
    for idx, q in enumerate(exam.get("p2") or []):
        for s_idx, stmt in enumerate(q.get("stmts") or []):
            answers[f"p2_{idx}_{s_idx}"] = "Đúng" if stmt["a"] else "Sai"
    for idx, q in enumerate(exam.get("p3") or []):
        answers[f"p3_{idx}"] = str(q.get("ans", ""))
    return answers


ALL = [(s, g) for g in range(6, 13) for s in subjects_for_grade(g) if s != "Ngữ văn"]


class GradeExamByProfileTests(unittest.TestCase):
    def test_perfect_paper_reaches_ten_all_subjects_grades(self):
        for subject, grade in ALL:
            with self.subTest(subject=subject, grade=grade):
                counts = assessment_profile(subject, grade)["counts"]
                if counts == (0, 0, 0):
                    continue
                exam = synth_exam(subject, grade, counts)
                result = grade_exam_by_profile(exam, perfect_answers(exam), subject, grade)
                self.assertEqual(result["total"], 10.0)

    def test_math12_absolute_p2_ladder_and_weights(self):
        exam = synth_exam("Toán học", 12, (12, 4, 6))
        result = grade_exam_by_profile(exam, perfect_answers(exam), "Toán học", 12)
        self.assertTrue(result["p2_absolute_ladder"])
        self.assertEqual(result["w_p1"], 3.0)
        self.assertEqual(result["w_p2"], 4.0)
        self.assertEqual(result["w_p3"], 3.0)
        self.assertIn("QĐ 764", result["p2_label"])

    def test_practice_grade_uses_scaled_ladder_caption(self):
        exam = synth_exam("Toán học", 8, (12, 2, 2))
        result = grade_exam_by_profile(exam, perfect_answers(exam), "Toán học", 8)
        self.assertFalse(result["p2_absolute_ladder"])
        self.assertIn("tỷ lệ", result["p2_label"])
        self.assertEqual(result["total"], 10.0)

    def test_geography12_shows_p3_weight(self):
        exam = synth_exam("Địa lý", 12, (18, 4, 6))
        result = grade_exam_by_profile(exam, perfect_answers(exam), "Địa lý", 12)
        self.assertTrue(result["has_p3"])
        self.assertEqual(result["w_p3"], 1.5)
        self.assertEqual(result["total"], 10.0)

    def test_partial_p2_one_statement(self):
        exam = synth_exam("Toán học", 12, (0, 1, 0))
        exam["p2"] = [{"q": "x", "stmts": [{"t": "a", "a": True}, {"t": "b", "a": False},
                                           {"t": "c", "a": True}, {"t": "d", "a": False}]}]
        # only 1 correct statement chosen
        answers = {"p2_0_0": "Đúng", "p2_0_1": "Đúng", "p2_0_2": "Sai", "p2_0_3": "Đúng"}
        # correct would be T F T F — user got only stmt0 right → k=1 → 0.1 * (10/1) after scale
        # present only p2, base weight 4 → scale 10/4, w_per_q=10 → 0.1*10=1.0
        result = grade_exam_by_profile(exam, answers, "Toán học", 12)
        self.assertEqual(result["score_p2"], 1.0)
        self.assertEqual(result["total"], 1.0)


class MatcherSharedLayerTests(unittest.TestCase):
    def test_mcq_accepts_option_text_key(self):
        q = {"opt": ["A. 1", "B. 2", "C. 3", "D. 4"], "ans": "B. 2"}
        self.assertEqual(canonicalize_mcq_key(q), "B")
        self.assertTrue(mcq_answer_matches(q, "B. 2"))
        self.assertTrue(mcq_answer_matches(q, "B"))

    def test_short_answer_text_and_numeric(self):
        self.assertTrue(short_answer_matches("2,5", "2.5"))
        self.assertTrue(short_answer_matches("Hà Nội", "hà nội"))
        self.assertFalse(short_answer_matches("2.6", "2.5"))
        self.assertFalse(short_answer_matches("Sai", "2.5"))

    def test_ladder_caption(self):
        self.assertIn("QĐ 764", part2_ladder_caption(1.0))
        self.assertIn("tỷ lệ", part2_ladder_caption(2.0))


if __name__ == "__main__":
    unittest.main()
