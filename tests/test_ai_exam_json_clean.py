# -*- coding: utf-8 -*-
"""AI exam JSON: forbid duplicate keys + one-retry contract."""
from __future__ import annotations

import unittest

from services.ai_json import (
    DUP_KEY_MESSAGE,
    JSON_CLEAN_RETRY_SUFFIX,
    JSON_UNIQUE_KEYS_RULE,
    is_duplicate_key_error,
    parse_ai_json,
)
from services.curriculum_policy import exam_generation_request, exam_prompt


class AiExamJsonCleanTests(unittest.TestCase):
    def test_identical_duplicate_keys_keep_one_value(self):
        parsed = parse_ai_json('{"p1":[],"p1":[]}')
        self.assertEqual(parsed, {"p1": []})
        self.assertTrue(is_duplicate_key_error(DUP_KEY_MESSAGE))
        self.assertFalse(is_duplicate_key_error("timeout"))

    def test_duplicate_question_lists_are_concatenated_without_invention(self):
        raw = (
            '{"p1":[{"q":"Câu một","opt":["A. 1","B. 2"],"ans":"A"}],'
            '"p1":[{"q":"Câu hai","opt":["A. 3","B. 4"],"ans":"B"},'
            '{"q":"Câu một","opt":["A. 1","B. 2"],"ans":"A"}]}'
        )
        parsed = parse_ai_json(raw)
        stems = [item["q"] for item in parsed["p1"]]
        self.assertEqual(stems, ["Câu một", "Câu hai"])

    def test_conflicting_scalar_duplicate_still_rejected(self):
        with self.assertRaises(ValueError) as ctx:
            parse_ai_json('{"ans":"A","ans":"B"}')
        self.assertIn("khóa trùng", str(ctx.exception))
        self.assertTrue(is_duplicate_key_error(ctx.exception))

    def test_exam_prompt_forbids_duplicate_keys(self):
        prompt = exam_prompt(
            "Toán học", 8, ["Đơn thức"], (2, 0, 0), "1011", "", ""
        )
        self.assertIn("mỗi khóa một lần", prompt)
        self.assertIn(JSON_UNIQUE_KEYS_RULE.split("(")[0].strip(), prompt)

    def test_exam_generation_request_keeps_unique_rule(self):
        system, user = exam_generation_request(
            "Toán học", 8, ["Đơn thức"], (2, 0, 0), "1011", "", ""
        )
        self.assertTrue(system)
        self.assertIn("mỗi khóa một lần", user)

    def test_retry_suffix_is_bounded_and_explicit(self):
        self.assertIn("RETRY", JSON_CLEAN_RETRY_SUFFIX)
        self.assertIn("khóa JSON trùng", JSON_CLEAN_RETRY_SUFFIX)
        self.assertIn("đúng một lần", JSON_CLEAN_RETRY_SUFFIX)
        self.assertLess(len(JSON_CLEAN_RETRY_SUFFIX), 400)


if __name__ == "__main__":
    unittest.main()
