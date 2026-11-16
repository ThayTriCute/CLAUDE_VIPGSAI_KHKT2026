import unittest

from services.tram3_exam_ux import copy_stored_exam, stored_exam_size_label


class StoredExamCopyTests(unittest.TestCase):
    def test_copy_keeps_every_question_in_order(self):
        original = {
            "code": "CK1",
            "title": "Đề cuối kỳ",
            "p1": [
                {"q": "Câu một", "opt": ["A. 1", "B. 2", "C. 3", "D. 4"], "ans": "A"},
                {"q": "Quan sát hình bên.", "opt": ["A. 1", "B. 2", "C. 3", "D. 4"], "ans": "B"},
            ],
            "p2": [{"q": "Đúng sai", "stmts": [{"t": "Ý", "a": True}]}],
            "p3": [{"q": "Ngắn", "ans": "5"}],
        }
        paper = copy_stored_exam(original)
        self.assertEqual([item["q"] for item in paper["p1"]], ["Câu một", "Quan sát hình bên."])
        self.assertEqual(paper["p2"][0]["stmts"][0]["a"], True)
        self.assertEqual(paper["p3"][0]["ans"], "5")
        self.assertTrue(paper["exact_stored_exam"])
        self.assertFalse(paper["is_blended_real"])
        paper["p1"][0]["q"] = "đã sửa"
        self.assertEqual(original["p1"][0]["q"], "Câu một")
        self.assertEqual(stored_exam_size_label(original), "2+1+1 câu")

    def test_empty_exam_is_refused(self):
        with self.assertRaises(ValueError):
            copy_stored_exam({"p1": [], "p2": [], "p3": []})

    def test_literature_size_counts_reading_and_writing(self):
        exam = {"part_doc_hieu": {"questions": [{"q": "Đọc"}]}, "part_viet": [{"q": "Viết"}]}
        self.assertEqual(stored_exam_size_label(exam), "đọc hiểu 1 + viết 1")
        self.assertEqual(copy_stored_exam(exam)["part_viet"][0]["q"], "Viết")
