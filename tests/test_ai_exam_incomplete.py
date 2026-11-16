import unittest

from services.context_recovery import repair_exam_context
from services.neuro_symbolic_verifier import audit_ai_generated_question_sympy


def _mcq(stem, ans="A", options=None):
    return {
        "q": stem,
        "opt": options or ["A. 1", "B. 2", "C. 3", "D. 4"],
        "ans": ans,
        "topic": "Xác suất có điều kiện",
    }


class TestAiExamDoesNotDieOnOneItem(unittest.TestCase):
    def test_one_broken_ai_item_is_withheld_and_the_rest_open(self):
        exam = {
            "is_ai_generated": True,
            "p1": [
                _mcq("Túi có 3 bi đỏ và 2 bi xanh. Xác suất lấy được bi đỏ là bao nhiêu?"),
                _mcq("Quan sát hình bên và cho biết xác suất biến cố A."),
                _mcq("Hai biến cố độc lập có xác suất 0,2 và 0,5. Xác suất giao là bao nhiêu?"),
            ],
        }
        repaired = repair_exam_context(exam, "Toán học", 12, topics=["Xác suất có điều kiện, Công thức Bayes"])
        recovery = repaired["context_recovery"]
        self.assertEqual(recovery["unresolved"], 0)
        self.assertEqual(recovery["withheld"], 1)
        self.assertEqual(len(repaired["p1"]), 2)
        self.assertEqual(sum(event["action"] == "withheld_unplayable" for event in recovery["events"]), 1)
        self.assertNotIn("hình bên", " ".join(item["q"] for item in repaired["p1"]))

    def test_bank_paper_withholds_the_broken_item_and_opens_the_rest(self):
        exam = {
            "p1": [
                _mcq("Câu đủ dữ kiện."),
                _mcq("Quan sát hình bên."),
            ],
        }
        repaired = repair_exam_context(exam, "Toán học", 12, topics=["Xác suất"])
        self.assertEqual(repaired["context_recovery"]["unresolved"], 0)
        self.assertEqual(repaired["context_recovery"]["withheld"], 1)
        self.assertEqual(len(repaired["p1"]), 1)
        self.assertNotIn("hình bên", repaired["p1"][0]["q"])

    def test_all_broken_ai_items_still_block_the_paper(self):
        exam = {
            "is_ai_generated": True,
            "p1": [_mcq("Nhìn hình bên, câu 1."), _mcq("Nhìn đồ thị sau, câu 2.")],
        }
        repaired = repair_exam_context(exam, "Toán học", 12, topics=["Đạo hàm"])
        self.assertEqual(repaired["context_recovery"]["unresolved"], 2)
        self.assertEqual(len(repaired["p1"]), 2)

    def test_inline_frequency_table_is_playable(self):
        stem = (
            "Cho bảng số liệu sau về một lớp 12.\n"
            "Nam 18\n"
            "Nữ 22\n"
            "Tổng 40\n"
            "Chọn ngẫu nhiên một học sinh. Xác suất chọn được nữ là bao nhiêu?"
        )
        exam = {"is_ai_generated": True, "p1": [_mcq(stem, "B")]}
        repaired = repair_exam_context(exam, "Toán học", 12, topics=["Xác suất có điều kiện"])
        self.assertEqual(repaired["context_recovery"]["unresolved"], 0)
        self.assertEqual(repaired["context_recovery"]["withheld"], 0)
        self.assertEqual(len(repaired["p1"]), 1)

    def test_letter_key_with_punctuation_is_kept_not_invented(self):
        question = _mcq("Một câu trắc nghiệm đủ bốn phương án.", ans="B.")
        exam = {"is_ai_generated": True, "p1": [question]}
        repaired = repair_exam_context(exam, "Toán học", 12, topics=["Xác suất"])
        self.assertEqual(repaired["p1"][0]["ans"], "B")
        self.assertEqual(repaired["context_recovery"]["unresolved"], 0)

    def test_option_text_key_maps_to_its_letter(self):
        question = _mcq("Chọn phương án.", ans="2", options=["A. 1", "B. 2", "C. 3", "D. 4"])
        exam = {"p1": [question]}
        repaired = repair_exam_context(exam, "Toán học", 12, topics=["Xác suất"])
        self.assertEqual(repaired["p1"][0]["ans"], "B")

    def test_unknown_key_is_not_assigned_a_letter(self):
        question = _mcq("Chọn phương án.", ans="không có trong đề")
        exam = {"is_ai_generated": True, "p1": [question, _mcq("Câu còn lại.")]}
        repaired = repair_exam_context(exam, "Toán học", 12, topics=["Xác suất"])
        self.assertEqual(repaired["context_recovery"]["withheld"], 1)
        self.assertEqual(len(repaired["p1"]), 1)
        self.assertEqual(repaired["p1"][0]["q"], "Câu còn lại.")

    def test_count_phrase_matches_sympy_and_interval_choices_do_not_false_flag(self):
        counted = {
            "q": "Cho hàm số y = x^3 - 3x. Số điểm cực trị của hàm số là",
            "opt": ["A. 1 điểm", "B. 2 điểm", "C. 3 điểm", "D. 4 điểm"],
            "ans": "B",
        }
        report = audit_ai_generated_question_sympy(counted)
        self.assertFalse(report.get("hallucination_detected"))
        self.assertTrue(report.get("verified"))
        wrong = dict(counted, ans="A")
        self.assertTrue(audit_ai_generated_question_sympy(wrong).get("hallucination_detected"))
        interval = {
            "q": "Cho hàm số y = x^3 - 3x. Tìm số cực trị rồi chọn khoảng chứa hoành độ điểm cực trị dương.",
            "opt": ["A. (-1; 0)", "B. (0; 2)", "C. (2; 4)", "D. (4; 6)"],
            "ans": "B",
        }
        self.assertFalse(audit_ai_generated_question_sympy(interval).get("hallucination_detected"))


if __name__ == "__main__":
    unittest.main()
