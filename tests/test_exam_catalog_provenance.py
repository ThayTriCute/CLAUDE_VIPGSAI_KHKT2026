import ast
import copy
import unittest
from pathlib import Path
from types import SimpleNamespace

from qa_runtime import exam_catalog_label, exam_display_title


class ExamCatalogProvenanceTests(unittest.TestCase):
    def test_declared_origins_are_distinct_and_unknown_is_not_certified(self):
        for metadata, label in [
            ({"is_ai_harvested": True}, "Đề AI tích lũy"),
            ({"exam_source_type": "ai_generated"}, "Đề AI tích lũy"),
            ({"exam_source_type": "mixed_bank"}, "Đề phối hợp nguồn"),
            ({"is_uploaded_teacher_exam": True}, "Đề giáo viên tải lên"),
            ({"is_real_exam": True}, "Đề lưu trong kho"),
            ({}, "Đề lưu trong kho"),
        ]:
            with self.subTest(metadata=metadata):
                self.assertEqual(exam_catalog_label(metadata), f"[{label}]")

    def test_actual_catalog_preserves_question_data_without_false_real_label(self):
        source = Path(__file__).resolve().parents[1].joinpath("app.py")
        tree = ast.parse(source.read_text(encoding="utf-8"))
        node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "get_cached_exams")
        node.decorator_list = []
        exam = {"code": "8551", "is_ai_harvested": True, "p1": [{"q": "Nội dung", "ans": "C"}]}
        original = copy.deepcopy(exam)
        env = {"ree": SimpleNamespace(get_baseline_full_exams=lambda *_: [exam]),
               "exam_catalog_label": exam_catalog_label,
               "os": SimpleNamespace(path=SimpleNamespace(exists=lambda _: False)),
               "EXAM_CACHE_DIR": "unused"}
        exec(compile(ast.Module(body=[node], type_ignores=[]), str(source), "exec"), env)
        rows = env["get_cached_exams"]("Toán học", 12)
        self.assertEqual(rows[0]["topic"], "[Đề AI tích lũy]")
        self.assertNotIn("2025", rows[0]["saved_at"])
        self.assertEqual(rows[0]["data"]["p1"], exam["p1"])
        self.assertEqual(exam, original)

    def test_missing_title_does_not_invent_school_or_standardization(self):
        self.assertEqual(exam_display_title({"school": "Một trường"}), "Đề luyện tập")
        self.assertEqual(exam_display_title({"title": "Đề do thầy soạn"}), "Đề do thầy soạn")


if __name__ == "__main__":
    unittest.main()
