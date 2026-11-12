"""UX helpers Trạm 3 — phiếu đáp án / mã truy cập / lọc đề GV."""
import unittest

from services.tram3_exam_ux import (
    answer_sheet_cells,
    answer_sheet_summary,
    exam_matches_access_code,
    filter_exams_for_listing,
    find_exam_by_access_code,
    is_teacher_uploaded_exam,
    render_answer_sheet_html,
)


class AnswerSheetTests(unittest.TestCase):
    def test_mcq_tf_short_progress_without_leaking_keys(self):
        exam = {
            "p1": [{"q": "a", "opt": ["A", "B", "C", "D"], "ans": "B"}],
            "p2": [{"q": "b", "stmts": [{"t": "1", "a": True}, {"t": "2", "a": False}, {"t": "3", "a": True}, {"t": "4", "a": False}]}],
            "p3": [{"q": "c", "ans": "3"}],
        }
        answers = {"p1_0": "A", "p2_0_0": "Đúng", "p2_0_1": "Sai"}
        cells = answer_sheet_cells(exam, answers, "Toán học")
        self.assertEqual([c["status"] for c in cells], ["filled", "partial", "empty"])
        html = render_answer_sheet_html(cells)
        self.assertIn("I.1", html)
        self.assertIn("II.1", html)
        self.assertNotIn("ans", html.lower().split("đáp án đúng")[0] if False else html)
        # Không lộ khóa đúng
        self.assertNotIn(">B<", html)
        self.assertNotIn("ans\":", html)
        summary = answer_sheet_summary(cells)
        self.assertEqual(summary, {"total": 3, "filled": 1, "partial": 1, "empty": 1})

    def test_literature_progress(self):
        exam = {
            "part_doc_hieu": {"questions": [{"q": "1"}, {"q": "2"}]},
            "part_viet": [{"q": "viết"}],
        }
        cells = answer_sheet_cells(exam, {"nv_dh_0": "ok"}, "Ngữ văn")
        self.assertEqual([c["status"] for c in cells], ["filled", "empty", "empty"])


class AccessCodeAndTeacherFilterTests(unittest.TestCase):
    def test_find_by_code_and_identity(self):
        exams = [
            {"code": "1011", "title": "A"},
            {"code": "2022", "title": "B", "is_teacher_upload": True},
        ]
        self.assertEqual(find_exam_by_access_code(exams, "2022")["title"], "B")
        self.assertTrue(exam_matches_access_code(exams[0], "1011"))
        self.assertIsNone(find_exam_by_access_code(exams, "9999"))

    def test_teacher_filter_and_held(self):
        exams = [
            {"code": "1", "is_teacher_upload": True},
            {"code": "2", "title": "bank"},
            {"code": "3", "is_teacher_upload": True, "held": True},
        ]
        teacher = filter_exams_for_listing(exams, teacher_only=True)
        self.assertEqual([e["code"] for e in teacher], ["1", "3"])
        ready = filter_exams_for_listing(exams, teacher_only=True, exclude_held_fn=lambda e: e.get("held"))
        self.assertEqual([e["code"] for e in ready], ["1"])
        self.assertTrue(is_teacher_uploaded_exam(exams[0]))
        self.assertFalse(is_teacher_uploaded_exam(exams[1]))


if __name__ == "__main__":
    unittest.main()
