# -*- coding: utf-8 -*-
"""Owner 13/11/2026: gói neo lớp 6–9 phải cite ≥2/3 cổng chính thức."""
from __future__ import annotations

import json
import lzma
import unittest
from pathlib import Path
from urllib.parse import urlparse

BUNDLE = Path(__file__).resolve().parents[1] / "textbook_archive_6_12" / "reviewed_lesson_packets"

# Ba cổng chính thức (hostname).
_OFFICIAL_HOSTS = (
    "vniteach.com",
    "taphuan.nxbgd.vn",
    "nxbgd.vn",
    "thsqg.vn",
    "truonghocsoquocgia.vn",
    "truonghocsoquocgia.nxbgd.vn",
)


def _portal_key(url: str) -> str | None:
    host = (urlparse(url).hostname or "").lower()
    if not host:
        return None
    if host == "vniteach.com" or host.endswith(".vniteach.com"):
        return "vniteach"
    if "taphuan.nxbgd.vn" in host or host.endswith(".nxbgd.vn") or host == "nxbgd.vn":
        return "nxbgd_taphuan"
    if "thsqg.vn" in host or "truonghocsoquocgia" in host:
        return "thsqg"
    return None


class PacketSourceRuleTests(unittest.TestCase):
    def test_grade_6_to_9_packets_cite_at_least_two_official_portals(self):
        index = json.loads((BUNDLE / "index.json").read_text(encoding="utf-8"))
        thcs = [row for row in index["entries"] if int(row.get("grade", 0)) <= 9]
        # Chưa có gói THCS → không fail; khi có thì bắt buộc ≥2 cổng.
        for row in thcs:
            packet = BUNDLE / row["path"]
            payload = json.loads(lzma.open(packet).read())
            portals = {
                key
                for src in payload.get("sources") or []
                if isinstance(src, dict)
                for key in [_portal_key(str(src.get("url") or ""))]
                if key
            }
            self.assertGreaterEqual(
                len(portals),
                2,
                f"{row['path']}: cần ≥2/3 cổng chính thức, đang có {sorted(portals)}",
            )
            note = str(payload.get("coverage_note") or "")
            self.assertTrue(
                note.strip(),
                f"{row['path']}: coverage_note phải ghi rõ căn cứ đã dùng / còn thiếu",
            )

    def test_guidance_documents_two_of_three_rule(self):
        from services.curriculum_policy import ACADEMIC_GROUNDING_GUIDANCE

        self.assertIn("≥2/3", ACADEMIC_GROUNDING_GUIDANCE)
        rule = Path(__file__).resolve().parents[1] / "docs" / "AI_TEXTBOOK_SOURCE_RULE.md"
        text = rule.read_text(encoding="utf-8")
        self.assertIn("≥ 2 / 3", text)
        self.assertIn("vniteach.com", text)
        self.assertIn("taphuan.nxbgd.vn", text)
        self.assertIn("thsqg.vn", text)


if __name__ == "__main__":
    unittest.main()
