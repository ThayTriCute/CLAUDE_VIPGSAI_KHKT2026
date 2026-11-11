"""Giới hạn lượt gọi AI mỗi phiên: parse hạn mức an toàn, chặn đúng khi hết lượt."""
import unittest

from services.ai_budget import (DEFAULT_LIMIT, MAX_LIMIT, MIN_LIMIT, ai_call_limit,
                                 is_over_budget, low_budget_notice, over_budget_message,
                                 remaining_calls)


class AiBudgetTests(unittest.TestCase):
    def test_limit_parsing_and_bounds(self):
        self.assertEqual(ai_call_limit(""), DEFAULT_LIMIT)
        self.assertEqual(ai_call_limit("60"), 60)
        self.assertEqual(ai_call_limit("60.0"), 60)
        self.assertEqual(ai_call_limit(" 25 "), 25)
        self.assertEqual(ai_call_limit("abc"), DEFAULT_LIMIT)
        self.assertEqual(ai_call_limit(None), DEFAULT_LIMIT)
        self.assertEqual(ai_call_limit(True), DEFAULT_LIMIT)
        self.assertEqual(ai_call_limit("1"), MIN_LIMIT)
        self.assertEqual(ai_call_limit("99999"), MAX_LIMIT)

    def test_remaining_and_over_budget(self):
        self.assertEqual(remaining_calls(5, 40), 35)
        self.assertEqual(remaining_calls(-3, 40), 40)
        self.assertEqual(remaining_calls("x", 40), 40)
        self.assertFalse(is_over_budget(39, 40))
        self.assertTrue(is_over_budget(40, 40))
        self.assertTrue(is_over_budget(41, 40))

    def test_messages(self):
        self.assertIn("40", over_budget_message(40))
        self.assertIsNone(low_budget_notice(10, 40))
        self.assertIsNone(low_budget_notice(0, 40))
        self.assertIn("3", low_budget_notice(3, 40))

    def test_app_gates_both_ai_entry_points(self):
        with open("app.py", encoding="utf-8") as handle:
            source = handle.read()
        self.assertEqual(source.count('st.session_state["ai_calls_used"] = _ai_used + 1'), 2)
        self.assertEqual(source.count("raise RuntimeError(over_budget_message(_ai_limit))"), 2)


if __name__ == "__main__":
    unittest.main()
