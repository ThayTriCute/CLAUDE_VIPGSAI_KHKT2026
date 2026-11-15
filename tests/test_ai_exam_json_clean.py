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
    def test_unique_object_rejects_duplicate_keys(self):
        with self.assertRaises(ValueError) as ctx:
            parse_ai_json('{"p1":[],"p1":[]}')
        self.assertIn("khóa trùng", str(ctx.exception))
        self.assertTrue(is_duplicate_key_error(ctx.exception))
        self.assertTrue(is_duplicate_key_error(DUP_KEY_MESSAGE))
        self.assertFalse(is_duplicate_key_error("timeout"))

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
