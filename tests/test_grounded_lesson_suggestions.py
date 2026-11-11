"""Bài có gói neo phải tự hiện trong gợi ý và neo đúng khi học sinh chọn.

Trước đây 0/26 gói khớp danh sách gợi ý (gợi ý cấp 'Chuyên đề', gói cấp 'Bài') nên
grounding gần như không kích hoạt. Test này khóa cơ chế khớp mới.
"""
import json
import re
import unittest
from pathlib import Path

from services.lesson_sources import grounded_lesson_topics, local_textbook_grounding

INDEX = Path(__file__).resolve().parents[1] / "textbook_archive_6_12" / "reviewed_lesson_packets" / "index.json"

# Đúng biểu thức dùng trong app.py (bộ chọn bài Trạm 1): chỉ bỏ tiền tố liệt kê chương/bài,
# giữ nguyên dấu ':' bên trong tên bài, và để tên bài có gói đi qua nguyên vẹn.
PREFIX = re.compile(r"^\s*(?:Chuyên đề|Bài|Chủ đề)\s*\d+\s*:\s*")


def picker_value(option):
    return PREFIX.sub("", option).strip()


class GroundedSuggestionTests(unittest.TestCase):
    def setUp(self):
        self.entries = json.loads(INDEX.read_text(encoding="utf-8"))["entries"]

    def test_every_packet_is_offered_and_fires_when_selected(self):
        for row in self.entries:
            with self.subTest(subject=row["subject"], grade=row["grade"]):
                options = grounded_lesson_topics(row["subject"], row["grade"])
                self.assertIn(row["topic"], options, "Bài có gói phải nằm trong gợi ý")
                picked = picker_value(row["topic"])
                status = local_textbook_grounding(row["subject"], row["grade"], picked)["status"]
                self.assertEqual(status, "reviewed_excerpt_packet_loaded")

    def test_chapter_prefix_stripped_but_inner_colon_kept(self):
        self.assertEqual(picker_value("Chuyên đề 1: Ứng dụng đạo hàm (KSHS)"), "Ứng dụng đạo hàm (KSHS)")
        self.assertEqual(picker_value("Chuyên đề 2: ASEAN: những chặng đường"), "ASEAN: những chặng đường")
        self.assertEqual(picker_value("Bài 4: Bên trong máy tính"), "Bên trong máy tính")

    def test_lesson_topic_with_leading_unit_is_not_truncated(self):
        topic = "Unit 1: Life stories — Tiếng Anh 12 Global Success"
        self.assertEqual(picker_value(topic), topic)

    def test_grounded_topics_safe_on_bad_input(self):
        self.assertEqual(grounded_lesson_topics("Môn lạ", 12), [])
        self.assertEqual(grounded_lesson_topics("Toán học", 99), [])

    def test_app_wires_suggestions_and_prefix_strip(self):
        source = (Path(__file__).resolve().parents[1] / "app.py").read_text(encoding="utf-8")
        self.assertIn("grounded_lesson_topics(subject, grade_num)", source)
        self.assertIn("grounded_options + curr_curriculum", source)
        self.assertIn('re.sub(r"^\\s*(?:Chuyên đề|Bài|Chủ đề)\\s*\\d+\\s*:\\s*"', source)
        self.assertNotIn('chosen_sgk_lesson.split(":")[-1]', source)


if __name__ == "__main__":
    unittest.main()
