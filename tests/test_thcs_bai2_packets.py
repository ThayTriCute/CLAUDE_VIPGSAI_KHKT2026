# -*- coding: utf-8 -*-
"""THCS Bài 2: đa môn × lớp 6–9 có trong index và neo được."""
from __future__ import annotations

import json
import unittest
from collections import defaultdict
from pathlib import Path

BUNDLE = Path(__file__).resolve().parents[1] / "textbook_archive_6_12" / "reviewed_lesson_packets"


class ThcsBai2PacketTests(unittest.TestCase):
    def test_bai2_covers_multiple_grades_and_subjects(self):
        index = json.loads((BUNDLE / "index.json").read_text(encoding="utf-8"))
        bai2 = [
            row for row in index["entries"]
            if "bai2" in str(row.get("path") or "").lower()
            and int(row.get("grade") or 0) <= 9
        ]
        by_grade = defaultdict(set)
        for row in bai2:
            by_grade[int(row["grade"])].add(row["subject"])
            self.assertIn("Bài 2", row["topic"])
            self.assertTrue((BUNDLE / row["path"]).is_file())
        self.assertGreaterEqual(len(bai2), 10)
        self.assertGreaterEqual(len(by_grade), 3)
        self.assertGreaterEqual(sum(len(s) for s in by_grade.values()), 8)


if __name__ == "__main__":
    unittest.main()
