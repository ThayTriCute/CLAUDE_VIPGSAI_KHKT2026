# -*- coding: utf-8 -*-
"""AppTest: radio hình thức đề Trạm 3 đổi đúng panel, không văng, mỗi khối 6–12."""
from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from streamlit.testing.v1 import AppTest


class Tram3ExamModeRadioAppTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import database
        cls._prev_baseline = os.environ.get("GSAI_LOAD_BASELINE_MASTER")
        os.environ["GSAI_LOAD_BASELINE_MASTER"] = "0"
        cls.temp = tempfile.TemporaryDirectory()
        cls.db = database.DatabaseManager(Path(cls.temp.name) / "tram3_mode_radio.db")
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

    def test_exam_mode_radio_switches_panel_every_grade(self):
        cells = [
            ("Lớp 6", "Toán học"),
            ("Lớp 7", "Tiếng Anh"),
            ("Lớp 8", "Khoa học tự nhiên"),
            ("Lớp 9", "Lịch sử & Địa lý"),
            ("Lớp 10", "Lịch sử"),
            ("Lớp 11", "Giáo dục kinh tế và pháp luật"),
            ("Lớp 12", "Công nghệ"),
        ]
        for grade_label, subject in cells:
            with self.subTest(subject=subject, grade=grade_label):
                at = self._open(grade_label, subject)
                mode = next(r for r in at.radio if r.label == "Lựa chọn hình thức đề thi:")
                options = [str(o) for o in mode.options]
                self.assertEqual(len(options), 4)
                self.assertTrue(any("Đề Luyện Tập Chuyên Đề" in o for o in options))
                self.assertTrue(any("Làm Nguyên Đề Thi Thật" in o for o in options))
                self.assertTrue(any("Nạp & Trộn Đề Word" in o for o in options))
                self.assertTrue(any("Quét Đề Link" in o for o in options))
                self.assertTrue(any("Trộn Siêu Đề" in b.label or "Trích Xuất Đề" in b.label or "Mở đề gốc" in b.label for b in at.button))

                mode.set_value(next(o for o in options if "Nạp & Trộn Đề Word" in o)).run(timeout=90)
                self.assertEqual([e.message for e in at.exception], [])
                blob = " ".join(str(m.value) for m in at.markdown)
                self.assertIn("Nạp Đề Thi Từ File Word", blob)

                mode = next(r for r in at.radio if r.label == "Lựa chọn hình thức đề thi:")
                mode.set_value(next(o for o in mode.options if "Quét Đề Link" in str(o))).run(timeout=90)
                self.assertEqual([e.message for e in at.exception], [])
                blob = " ".join(str(m.value) for m in at.markdown)
                self.assertIn("Quét Đề Từ Link", blob)
                self.assertTrue(any("Chọn chuyên trang" in s.label for s in at.selectbox))

                mode = next(r for r in at.radio if r.label == "Lựa chọn hình thức đề thi:")
                mode.set_value(next(o for o in mode.options if "Làm Nguyên Đề Thi Thật" in str(o))).run(timeout=90)
                self.assertEqual([e.message for e in at.exception], [])
                self.assertEqual(at.session_state.get("exam_state"), "config")


if __name__ == "__main__":
    unittest.main()
