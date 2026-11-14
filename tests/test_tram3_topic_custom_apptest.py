# -*- coding: utf-8 -*-
"""AppTest: checkbox chủ đề + ô tùy biến Trạm 3 theo môn×lớp."""
from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from streamlit.testing.v1 import AppTest


class Tram3TopicCustomAppTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import database
        cls._prev_baseline = os.environ.get("GSAI_LOAD_BASELINE_MASTER")
        os.environ["GSAI_LOAD_BASELINE_MASTER"] = "0"
        cls.temp = tempfile.TemporaryDirectory()
        cls.db = database.DatabaseManager(Path(cls.temp.name) / "tram3_topic.db")
        cls.db_patch = patch.object(database, "db_manager", cls.db)
        cls.db_patch.start()

    @classmethod
    def tearDownClass(cls):
        cls.db_patch.stop()
        cls.temp._ignore_cleanup_errors = True
        cls.temp.cleanup()
        if cls._prev_baseline is None:
            os.environ.pop("GSAI_LOAD_BASELINE_MASTER", None)
        else:
            os.environ["GSAI_LOAD_BASELINE_MASTER"] = cls._prev_baseline

    def _open(self, grade_label: str, subject: str):
        at = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=60)
        at.secrets["ADMIN_PASS"] = "qa-private-password"
        at.run()
        next(s for s in at.selectbox if s.label == "🎯 Chọn khối lớp:").select(grade_label).run()
        next(s for s in at.selectbox if s.label == "📚 Môn học cần hỗ trợ:").select(subject).run()
        at.session_state["selected_station"] = "📝 Trạm 3: Luyện Tập & Khảo Thí"
        at.session_state["exam_state"] = "config"
        at.run(timeout=90)
        self.assertEqual([e.message for e in at.exception], [])
        return at

    def test_topic_checkboxes_and_custom_prompt_bind_to_context(self):
        cells = [
            ("Lớp 8", "Khoa học tự nhiên"),
            ("Lớp 9", "Lịch sử & Địa lý"),
            ("Lớp 12", "Toán học"),
            ("Lớp 12", "Vật lý"),
            ("Lớp 12", "Tiếng Anh"),
            ("Lớp 11", "Hóa học"),
            ("Lớp 10", "Tin học"),
            ("Lớp 6", "Toán học"),
        ]
        for grade_label, subject in cells:
            with self.subTest(subject=subject, grade=grade_label):
                at = self._open(grade_label, subject)
                self.assertTrue(
                    any("Chọn Chuyên đề Khảo thí" in str(m.value) for m in at.markdown),
                    msg="Thiếu khối chọn chuyên đề",
                )
                checks = list(at.checkbox)
                self.assertGreaterEqual(len(checks), 1, msg="Phải có checkbox chủ đề")
                # Tắt hết rồi bật lại checkbox đầu (nếu có) để xác nhận widget sống
                topic_boxes = [c for c in checks if "AI sinh nguyên câu" not in str(c.label)]
                self.assertGreaterEqual(len(topic_boxes), 1)
                first = topic_boxes[0]
                first.set_value(True).run()
                topics = at.session_state.get("policy_selected_topics") or []
                self.assertIsInstance(topics, list)
                self.assertGreaterEqual(len(topics), 1)

                area = next(t for t in at.text_area if "Yêu cầu ma trận" in t.label or "tùy biến" in t.label.lower() or "Nhập yêu cầu" in t.label)
                prompt = f"Ưu tiên {subject} — không lộ đáp án QA"
                area.set_value(prompt).run()
                self.assertEqual(at.session_state.get("custom_matrix_prompt"), prompt)
                # Đổi môn/lớp khác trong cùng vòng → không assert cross-clear (đã có test_station_ui)


if __name__ == "__main__":
    unittest.main()
