# -*- coding: utf-8 -*-
"""Trạm 3: chống trùng stem / họ mẫu dù exact JSON khác (scan vs phục dựng)."""
from __future__ import annotations

import unittest

from dedupe_bank import q_fingerprint, q_family_fingerprint, q_stem_fingerprint


class StemDedupeUnitTests(unittest.TestCase):
    def test_same_stem_ignores_image_and_explain(self):
        a = {
            "q": "Đường cong dưới đây là đồ thị của hàm số nào?",
            "opt": [r"$y=\dfrac{2x+3}{x-1}$", r"$y=\dfrac{x^2-x+3}{x-1}$"],
            "ans": "A",
            "explain": "bản scan",
            "image_base64": "data:image/png;base64," + ("A" * 200),
        }
        b = {
            "q": "Đường cong dưới đây là đồ thị của hàm số nào?",
            "opt": [r"$y=\dfrac{2x+3}{x-1}$", r"$y=\dfrac{x^2-x+3}{x-1}$"],
            "ans": "A",
            "explain": "bản phục dựng dài hơn nhiều chữ",
            "f": {"type": "func_1_1", "a": 2, "b": 3, "c": 1, "d": -1},
        }
        self.assertEqual(q_stem_fingerprint(a), q_stem_fingerprint(b))
        self.assertNotEqual(q_fingerprint(a), q_fingerprint(b))

    def test_family_masks_digits(self):
        a = {"q": "Tính f(2) biết f(x)=x+1", "opt": ["3", "4"], "ans": "A"}
        b = {"q": "Tính f(5) biết f(x)=x+1", "opt": ["6", "7"], "ans": "A"}
        self.assertEqual(q_family_fingerprint(a), q_family_fingerprint(b))
        self.assertNotEqual(q_stem_fingerprint(a), q_stem_fingerprint(b))


if __name__ == "__main__":
    unittest.main()
