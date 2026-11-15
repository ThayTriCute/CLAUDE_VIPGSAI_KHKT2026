# -*- coding: utf-8 -*-
"""Local regression: print-style + Azota TikZ + soft reviewed visuals (no VIP hash lock)."""
from __future__ import annotations

import json
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest.mock import patch

from services.azota_visual_sources import export_azota_visual_sources, numeric_model_picture
from services.context_recovery import recover_visual
from services.exam_print_style import DRAWING_METHODS, exam_bbt_html, exam_svg, exam_tikz, picture_width_inches
from services import reviewed_question_visuals as rqv


class ExamPrintStyleLocalTests(unittest.TestCase):
    def test_svg_keeps_geometry_and_print_ink(self):
        svg = (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 20">'
            '<polygon points="0,0 9,0 5,8" fill="#dbeafe" stroke="blue"/>'
            '<path d="M0,0L5,8" stroke="red" stroke-dasharray="4 2" fill="none"/>'
            '<text x="2" y="3" fill="red">A</text></svg>'
        )
        result = ET.fromstring(exam_svg(svg))
        original = ET.fromstring(svg)
        self.assertEqual(result.attrib["viewBox"], original.attrib["viewBox"])
        self.assertEqual(result[1].get("stroke"), "#000000")
        self.assertEqual(result[2].text, "A")
        self.assertEqual(svg.count("blue"), 1)

    def test_bbt_print_strips_banner_only(self):
        raw = (
            '<div><div style="background:#0f172a;">📐 Bảng Biến Thiên Chuẩn Sư Phạm '
            "(CT GDPT 2018)</div><table><tr><td>−∞</td><td>2</td></tr></table></div>"
        )
        result = exam_bbt_html(raw)
        self.assertNotIn("Bảng Biến Thiên Chuẩn", result)
        self.assertIn("<td>−∞</td><td>2</td>", result)

    def test_picture_fit_and_tikz_recolor(self):
        self.assertEqual(picture_width_inches(60, 30), 0.5)
        self.assertIn("black", exam_tikz(r"\draw[blue] (0,0) -- (1,1);"))
        self.assertIn("reviewed_diagram", DRAWING_METHODS)


class AzotaVisualSourcesLocalTests(unittest.TestCase):
    def test_text_only_exam_exports_empty(self):
        self.assertEqual(export_azota_visual_sources({"p1": [{"q": "Câu hỏi văn bản"}]}), "")

    def test_numeric_tikz_no_invented_degenerate(self):
        model = dict(type="func_1_1", a="2", b="3", c="1", d="-2")
        picture = numeric_model_picture(model)
        self.assertIn(r"\begin{tikzpicture}", picture)
        self.assertNotIn("blue", picture)
        self.assertEqual(numeric_model_picture(dict(type="func_1_1", a=2, b=4, c=1, d=2)), "")

    def test_bbt_complete_exports_tikz_or_notes(self):
        complete = "x | -5 | 1 | 7\ny' | - | 0 | +\ny | 6 | 2 | 9 ||"
        missing = "x | -inf | 1 | +inf\ny' | + | || | +\ny | 0 | || | 0"
        result = export_azota_visual_sources(
            {"subject": "Toán học", "grade": 12, "p1": [{"bbt": complete}, {"bbt": missing}]}
        )
        self.assertTrue(result)
        self.assertTrue(
            r"\begin{tikzpicture}" in result or "thiếu dữ kiện" in result
        )


class ReviewedSoftIdentityLocalTests(unittest.TestCase):
    def setUp(self):
        rqv.clear_reviewed_visual_index_cache()

    def tearDown(self):
        rqv.clear_reviewed_visual_index_cache()

    def test_empty_registry_miss_is_none(self):
        q = {"q": "Hình bên. GTLN bằng?", "ans": "4", "source": "VIP-HASH-WILL-MISS"}
        self.assertIsNone(rqv.reviewed_question_visual(q, "Toán học", 12))
        self.assertIsNone(rqv.reviewed_question_specification(q, "Toán học", 12))

    def test_explicit_visual_id_preferred_over_stem_hash(self):
        q_a = {"q": "Stem A khác nhau", "visual_id": "pbc1203-i3", "ans": "A"}
        q_b = {"q": "Stem B hoàn toàn khác", "visual_id": "pbc1203-i3", "ans": "B"}
        self.assertEqual(
            rqv.visual_identity(q_a, "Toán học", 12),
            rqv.visual_identity(q_b, "Toán học", 12),
        )
        self.assertTrue(rqv.visual_identity(q_a, "Toán học", 12).startswith("id:"))

    def test_soft_source_number_key(self):
        q = {"q": "anything", "source": "PBC1203", "original_number": 3}
        key = rqv.visual_identity(q, "Toán học", 12)
        self.assertEqual(key, "soft:Toán học:12:PBC1203:3")

    def test_recover_visual_miss_does_not_break_existing_path(self):
        q = {"q": "Tính đạo hàm của y = x^2", "ans": "2x"}
        out = recover_visual(q, "Toán học", 12)
        self.assertIsInstance(out, dict)
        self.assertNotEqual(out.get("visual_recovery", {}).get("method"), "reviewed_source_figure_restored")

    def test_local_registry_hit_by_visual_id_without_vip_stem_hash(self):
        from PIL import Image
        import hashlib

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            png = root / "fig.png"
            Image.new("RGB", (8, 8), color=(240, 240, 240)).save(png, format="PNG")
            sha = hashlib.sha256(png.read_bytes()).hexdigest()
            identity = "id:Toán học:12:local-fig-1"
            (root / "index.json").write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "figures": {
                            identity: {
                                "review_status": "source_region_reviewed",
                                "file": "fig.png",
                                "sha256": sha,
                                "source_sha256": "abc",
                                "source_url": "local",
                                "page": 1,
                                "bbox": [0, 0, 1, 1],
                            }
                        },
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            with patch.object(rqv, "ROOT", root):
                rqv.clear_reviewed_visual_index_cache()
                hit = rqv.reviewed_question_visual(
                    {"q": "stem không khớp VIP", "visual_id": "local-fig-1"},
                    "Toán học",
                    12,
                )
                self.assertIsNotNone(hit)
                self.assertTrue(hit["image_base64"].startswith("data:image/png;base64,"))
                miss = rqv.reviewed_question_visual(
                    {"q": "stem không khớp VIP", "visual_id": "other"},
                    "Toán học",
                    12,
                )
                self.assertIsNone(miss)


if __name__ == "__main__":
    unittest.main()
