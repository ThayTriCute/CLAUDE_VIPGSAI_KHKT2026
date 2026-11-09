"""Lock the agreement between the two Part II (Đúng/Sai) correctness paths.

Two independent code paths decide whether a Part II statement is correct:
- services.scoring_service.grade_part2  -> the SCORE a student sees
- qa_runtime.exam_response_metadata     -> _item_results stored for Trạm 4 psychometrics

They use different matching styles (string compare vs normalize_bool on both sides).
For every answer encoding the radio widget actually produces ("Đúng" / "Sai" /
"Chưa chọn" / missing) they MUST agree, otherwise a student's score and the research
item-matrix would diverge. This test is a regression lock, not a logic change: if a
future edit makes the two paths disagree on real inputs, it fails here.
"""
import unittest

from services.scoring_service import grade_part2
from qa_runtime import exam_response_metadata


def _p2_true_count(exam, answers):
    meta = exam_response_metadata(exam, answers)
    return sum(1 for k, v in meta["_item_results"].items() if k.startswith("p2_") and v is True)


class TestGradingPathConsistency(unittest.TestCase):
    def _assert_consistent(self, p2, answers):
        exam = {"p1": [], "p2": p2, "p3": []}
        _, correct_stmts, _ = grade_part2(p2, answers)
        self.assertEqual(
            correct_stmts, _p2_true_count(exam, answers),
            msg="grade_part2 and exam_response_metadata disagree on Part II correctness")

    def test_mixed_answers(self):
        p2 = [
            {"stmts": [{"a": True}, {"a": False}, {"a": True}, {"a": False}]},
            {"stmts": [{"a": False}, {"a": True}]},
        ]
        answers = {
            "p2_0_0": "Đúng", "p2_0_1": "Đúng", "p2_0_2": "Sai", "p2_0_3": "Sai",
            "p2_1_0": "Chưa chọn", "p2_1_1": "Đúng",
        }
        self._assert_consistent(p2, answers)
        # Sanity: 4 correct statements (0_0, 0_3, 1_1 ... recompute) via grade_part2.
        _, correct_stmts, total = grade_part2(p2, answers)
        self.assertEqual((correct_stmts, total), (3, 6))

    def test_all_correct(self):
        p2 = [{"stmts": [{"a": True}, {"a": False}]}]
        answers = {"p2_0_0": "Đúng", "p2_0_1": "Sai"}
        self._assert_consistent(p2, answers)

    def test_all_blank_or_missing(self):
        p2 = [{"stmts": [{"a": True}, {"a": False}]}]
        # one explicit "Chưa chọn", one missing key entirely
        answers = {"p2_0_0": "Chưa chọn"}
        self._assert_consistent(p2, answers)
        _, correct_stmts, _ = grade_part2(p2, answers)
        self.assertEqual(correct_stmts, 0)

    def test_ans_key_variant(self):
        # statements may carry the answer under "ans" instead of "a"
        p2 = [{"stmts": [{"ans": True}, {"ans": False}]}]
        answers = {"p2_0_0": "Đúng", "p2_0_1": "Đúng"}
        self._assert_consistent(p2, answers)


if __name__ == "__main__":
    unittest.main()
