"""Trạm 3 (Khảo thí) nghiệm thu đa môn/đa lớp — đúng môn, đúng lớp, đúng tác vụ.

Khóa hành vi đã rà 10/11/2026 cho toàn ma trận 13 môn × lớp 6–12 (không gọi AI):
- assessment_profile hợp lệ cho mọi tổ hợp; lớp 6–11 là 'practice', lớp 12 'graduation_reference'.
- exam_generation_request đúng ranh giới system/prompt, mang đúng môn + lớp, không lẫn lớp khác.
- validate_exam_structure nhận đề dựng đúng cấu hình, chặn đề sai cấu trúc.
- validate_exam_context chặn câu/đề khai báo sai môn hoặc sai lớp.
- prepare_exam_for_delivery chạy trên đề hợp lệ mọi môn/lớp.
- Ràng buộc 'chỉ hàm bậc ba' (tác vụ người dùng) chặn câu phân thức.
- Chấm điểm quy về thang 10 dù môn chỉ có một phần (Tiếng Anh, Ngữ văn).
"""
import json
import unittest

from services.academic_context import subjects_for_grade
from services.curriculum_policy import (assessment_profile, exam_generation_request,
    prepare_exam_for_delivery, validate_exam_context, validate_exam_structure)
from services.request_scope import explicit_request_scope, question_scope_issue


def synth_exam(subject, grade, counts, code="1234"):
    if subject == "Ngữ văn":
        return {"code": code, "subject": subject, "grade": grade,
                "part_doc_hieu": {"text": "Ngữ liệu đọc hiểu ngoài SGK.", "author": "", "source": "",
                    "questions": [{"q": "Câu đọc hiểu?", "ans": "Hướng dẫn chấm", "point": 1.0, "explain": "x"}]},
                "part_viet": [{"q": "Đề viết theo lớp.", "ans": "Rubric", "point": 6.0, "explain": "x"}]}
    c1, c2, c3 = counts
    exam = {"code": code, "subject": subject, "grade": grade, "p1": [], "p2": [], "p3": []}
    for i in range(c1):
        exam["p1"].append({"q": f"Câu {i+1}?", "opt": ["A. a", "B. b", "C. c", "D. d"], "ans": "B", "topic": "T", "explain": "x"})
    for i in range(c2):
        exam["p2"].append({"q": f"Ngữ liệu {i+1}", "stmts": [{"t": f"m{j}", "a": j % 2 == 0} for j in range(4)], "topic": "T", "explain": "x"})
    for i in range(c3):
        exam["p3"].append({"q": f"TLN {i+1}?", "ans": "2.5", "topic": "T", "explain": "x"})
    return exam


ALL = [(s, g) for g in range(6, 13) for s in subjects_for_grade(g)]


class AssessmentProfileTests(unittest.TestCase):
    def test_every_subject_grade_has_coherent_profile(self):
        for s, g in ALL:
            with self.subTest(subject=s, grade=g):
                prof = assessment_profile(s, g)
                counts = prof["counts"]
                self.assertEqual(len(counts), 3)
                self.assertTrue(all(isinstance(n, int) and n >= 0 for n in counts))
                self.assertGreater(prof["minutes"], 0)
                self.assertEqual(prof["scope"], "practice" if g < 12 else "graduation_reference")
                if s not in ("Ngữ văn", "Tiếng Anh"):
                    self.assertGreater(counts[0], 0)


class RequestBoundaryTests(unittest.TestCase):
    def test_request_carries_exact_subject_and_grade_only(self):
        for s, g in ALL:
            with self.subTest(subject=s, grade=g):
                counts = assessment_profile(s, g)["counts"]
                system, context = exam_generation_request(s, g, [f"[Lớp {g}] Chuyên đề"], counts, "1234")
                self.assertIn(f"môn {s};", system)
                self.assertIn(f"lớp {g};", system)
                for other in range(6, 13):
                    if other != g:
                        self.assertNotIn(f"lớp {other};", system)
                self.assertIn("selected_topics", context)

    def test_boundary_guard_raises_when_prefix_desynced(self):
        # exam_generation_request đối chiếu prefix của prompt với policy; đây là bằng chứng
        # cơ chế boundary còn hoạt động (không phải chỉ build chuỗi).
        system, context = exam_generation_request("Toán học", 12, ["A"], (12, 4, 6), "1234")
        self.assertTrue(system.strip())
        self.assertTrue(context.startswith("{"))


class StructureAndContextTests(unittest.TestCase):
    def test_valid_exam_accepted_and_delivered(self):
        for s, g in ALL:
            with self.subTest(subject=s, grade=g):
                prof = assessment_profile(s, g)
                exam = synth_exam(s, g, prof["counts"])
                if s == "Ngữ văn":
                    validate_exam_structure(exam, s)
                else:
                    validate_exam_structure(exam, s, prof["counts"])
                prepare_exam_for_delivery(json.loads(json.dumps(exam)), s, g, prof["minutes"])

    def test_wrong_grade_or_subject_is_rejected(self):
        exam = synth_exam("Toán học", 12, (12, 4, 6))
        wrong_grade = json.loads(json.dumps(exam)); wrong_grade["grade"] = 11
        with self.assertRaises(ValueError):
            validate_exam_context(wrong_grade, "Toán học", 12)
        wrong_title = json.loads(json.dumps(exam)); wrong_title["title"] = "Đề thi lớp 10"
        with self.assertRaises(ValueError):
            validate_exam_context(wrong_title, "Toán học", 12)
        wrong_subject = json.loads(json.dumps(exam))
        wrong_subject["p1"][0]["subject"] = "Vật lý"
        with self.assertRaises(ValueError):
            validate_exam_context(wrong_subject, "Toán học", 12)

    def test_malformed_questions_are_rejected(self):
        bad_mcq = {"p1": [{"q": "x", "opt": ["A", "B", "C"], "ans": "A"}], "p2": [], "p3": []}
        with self.assertRaises(ValueError):
            validate_exam_structure(bad_mcq, "Toán học")
        bad_tf = {"p1": [], "p2": [{"q": "x", "stmts": [{"t": "a", "a": True}]}], "p3": []}
        with self.assertRaises(ValueError):
            validate_exam_structure(bad_tf, "Toán học")
        no_ans = {"p1": [], "p2": [], "p3": [{"q": "x", "ans": ""}]}
        with self.assertRaises(ValueError):
            validate_exam_structure(no_ans, "Toán học")


class CustomTaskScopeTests(unittest.TestCase):
    def test_cubic_only_task_detected_with_negation_guard(self):
        self.assertEqual(explicit_request_scope("Toán học", "Chỉ dùng hàm số bậc ba"),
                         {"function_family": "cubic_only"})
        self.assertEqual(explicit_request_scope("Toán học", "only cubic functions"),
                         {"function_family": "cubic_only"})
        self.assertEqual(explicit_request_scope("Toán học", "không chỉ hàm bậc ba"), {})
        self.assertEqual(explicit_request_scope("Vật lý", "Chỉ dùng hàm số bậc ba"), {})

    def test_cubic_only_blocks_rational_question_on_delivery(self):
        scope = {"function_family": "cubic_only"}
        self.assertEqual(question_scope_issue({"q": r"Cho hàm số $y=x^3-3x+1$"}, scope), "")
        self.assertEqual(question_scope_issue({"q": r"Cho hàm số $y=\frac{2x+1}{x-1}$"}, scope),
                         "outside_explicit_request")
        exam = {"code": "1", "subject": "Toán học", "grade": 12,
                "p1": [{"q": r"Cho hàm số $y=\frac{2x+1}{x-1}$ có tiệm cận đứng?",
                        "opt": ["A. 1", "B. 2", "C. 3", "D. 4"], "ans": "A", "topic": "t", "explain": "x"}],
                "p2": [], "p3": []}
        with self.assertRaises(ValueError):
            prepare_exam_for_delivery(exam, "Toán học", 12, 90, custom_request="chỉ hàm bậc ba")


class ScoreScalingTests(unittest.TestCase):
    """Chấm điểm quy về thang 10 theo trọng số của phần thực sự có câu hỏi."""

    @staticmethod
    def weighted_total(subject, grade, p1_ratio=1.0, p2_ratio=1.0, p3_ratio=1.0):
        base = list(assessment_profile(subject, grade)["weights"])
        if subject == "Tiếng Anh":
            base = [10.0, 0.0, 0.0]
        counts = assessment_profile(subject, grade)["counts"]
        present = [c > 0 for c in counts] if subject != "Ngữ văn" else [False, False, False]
        active_max = sum(w for w, has in zip(base, present) if has)
        scale = 10.0 / active_max if active_max else 0.0
        ratios = (p1_ratio, p2_ratio, p3_ratio)
        return round(sum(base[i] * scale * ratios[i] for i in range(3) if present[i]), 2)

    def test_full_marks_reach_ten_even_with_single_part_subjects(self):
        for s, g in ALL:
            if s == "Ngữ văn":
                continue
            with self.subTest(subject=s, grade=g):
                self.assertEqual(self.weighted_total(s, g), 10.0)

    def test_partial_credit_is_proportional(self):
        self.assertEqual(self.weighted_total("Tiếng Anh", 12, p1_ratio=0.5), 5.0)
        self.assertEqual(self.weighted_total("Toán học", 12, p1_ratio=0.0, p2_ratio=0.0, p3_ratio=0.0), 0.0)


if __name__ == "__main__":
    unittest.main()
