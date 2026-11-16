import unittest
from unittest.mock import patch

import real_exam_engine as ree
from services.context_recovery import repair_exam_context


EXAMPLE = "Ví dụ: Chỉ lấy Bài 1, 2, 3 không lấy Oxyz; Cho 5 câu đồ thị phân thức 2/1; Không ra câu trùng phương..."
TOPIC = "[Lớp 12] Chuyên đề 1: Ứng dụng đạo hàm khảo sát và vẽ đồ thị hàm số"


def _q(stem, topic, explain="", formula=None):
    item = {
        "q": stem,
        "topic": topic,
        "explain": explain,
        "opt": ["A. 1", "B. 2", "C. 3", "D. 4"],
        "ans": "A",
        "level": "TH",
    }
    if formula:
        item["f"] = formula
    return item


class MixOneLawTests(unittest.TestCase):
    def setUp(self):
        ree._RECENT_QUESTION_COOLDOWN.clear()

    def test_example_sentence_is_not_a_command(self):
        self.assertEqual(ree.effective_custom_prompt(EXAMPLE), "")
        self.assertEqual(ree.effective_custom_prompt("  Chỉ lấy bài khảo sát hàm số  "), "Chỉ lấy bài khảo sát hàm số")

    def test_explain_mention_does_not_admit_or_inject_a_template(self):
        pool = {
            "p1": [
                _q("Tính cực trị của hàm số y = x^3 - 3x.", "Ứng dụng đạo hàm"),
                _q("Tính cực trị của hàm số y = x^3 - 3x.", "Ứng dụng đạo hàm"),
                _q(
                    "Tính xác suất biến cố Bayes.",
                    "Xác suất có điều kiện",
                    explain="khảo sát hàm số đạo hàm cực trị đồ thị phân thức 2/1",
                ),
                _q("Xét tính đơn điệu của y = x^3 + x.", "Khảo sát hàm số", formula={"type": "func_3", "a": 1, "b": 0, "c": 1, "d": 0}),
            ],
            "p2": [],
            "p3": [],
        }
        with patch.object(ree, "get_baseline_questions_pool", return_value=pool):
            exam = ree.generate_blended_real_exam("Toán học", 12, [TOPIC], (4, 0, 0), custom_prompt=EXAMPLE)
        stems = [item["q"] for item in exam["p1"]]
        self.assertEqual(len(stems), len(set(stems)))
        self.assertTrue(all("Bayes" not in stem for stem in stems))
        self.assertTrue(all(not item.get("is_synthetic_template") for item in exam["p1"]))
        self.assertLess(len(stems), 4)
        self.assertTrue(exam["counts_shortfall"])
        self.assertEqual(stems[0], "Xét tính đơn điệu của y = x^3 + x.")

    def test_bank_and_ai_share_the_withhold_gate(self):
        bank = {"p1": [_q("Câu đủ.", "Hàm số"), _q("Quan sát hình bên.", "Hàm số")]}
        ai = {"is_ai_generated": True, "p1": [_q("Câu đủ.", "Hàm số"), _q("Quan sát đồ thị sau.", "Hàm số")]}
        for exam in (bank, ai):
            repaired = repair_exam_context(exam, "Toán học", 12, topics=["Hàm số"])
            self.assertEqual(repaired["context_recovery"]["unresolved"], 0)
            self.assertEqual(repaired["context_recovery"]["withheld"], 1)
            self.assertEqual(len(repaired["p1"]), 1)
