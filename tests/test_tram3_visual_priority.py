# -*- coding: utf-8 -*-
"""Trạm 3: đồ thị phục dựng (f) phải thắng ảnh cắt đề (image_base64)."""
from __future__ import annotations

import unittest
from pathlib import Path


class VisualPrioritySourceTests(unittest.TestCase):
    def test_question_visual_html_prefers_coeff_graph_over_crop(self):
        text = Path(__file__).resolve().parents[1].joinpath("app.py").read_text(encoding="utf-8")
        start = text.index("def question_visual_html(question):")
        end = text.index("\ndef latex_text(value):", start)
        fn = text[start:end]
        coeff_pos = fn.find("render_math_graph_to_webp_base64")
        crop_pos = fn.find("Hình nguồn (chỉ khi chưa có đồ thị phục dựng)")
        self.assertGreater(coeff_pos, 0)
        self.assertGreater(crop_pos, 0)
        self.assertLess(coeff_pos, crop_pos, "Reconstructed f-graph must be attempted before scan crop")
        self.assertIn("if not graph_done and has_source", fn)
        self.assertNotIn(
            "if has_source:\n        pieces.append(\"<img alt='Hình trong ngữ liệu nguồn'",
            fn,
        )


if __name__ == "__main__":
    unittest.main()
