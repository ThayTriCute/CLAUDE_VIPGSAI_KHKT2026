# -*- coding: utf-8 -*-
"""AppTest: ô link của môn không có chuyên trang không dính URL Toán."""
from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from streamlit.testing.v1 import AppTest


class Tram3LinkPortalAppTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import database
        cls._prev_baseline = os.environ.get("GSAI_LOAD_BASELINE_MASTER")
        os.environ["GSAI_LOAD_BASELINE_MASTER"] = "0"
        cls.temp = tempfile.TemporaryDirectory()
        cls.db = database.DatabaseManager(Path(cls.temp.name) / "tram3_link_portal.db")
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

    def _open(self, grade_label, subject):
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

    def _link_url(self, at, subject):
        mode = next(r for r in at.radio if r.label == "Lựa chọn hình thức đề thi:")
        mode.set_value(next(o for o in mode.options if "Quét Đề Link" in str(o))).run(timeout=90)
        self.assertEqual([e.message for e in at.exception], [])
        field = next(t for t in at.text_input if "Nhập Link bài viết" in t.label)
        return str(field.value or "")

    def test_grade8_link_stays_on_the_subject(self):
        at = self._open("Lớp 8", "Toán học")
        toan = self._link_url(at, "Toán học")
        self.assertIn("de-thi-giua-hk1-toan-8", toan)
        toan_src = next(s for s in at.selectbox if "Chọn chuyên trang" in s.label)
        self.assertTrue(any("TOANMATH" in str(o) for o in toan_src.options))
        self.assertTrue(any("MATHVN" in str(o) for o in toan_src.options))

        next(s for s in at.selectbox if s.label == "📚 Môn học cần hỗ trợ:").select("Khoa học tự nhiên").run(timeout=90)
        khtn = self._link_url(at, "Khoa học tự nhiên")
        self.assertNotIn("toanmath", khtn.lower())
        self.assertEqual(khtn, "")
        src = next(s for s in at.selectbox if "Chọn chuyên trang" in s.label)
        self.assertNotIn("TOANMATH", str(src.options[0]))

        next(s for s in at.selectbox if s.label == "📚 Môn học cần hỗ trợ:").select("Lịch sử & Địa lý").run(timeout=90)
        lsdl = self._link_url(at, "Lịch sử & Địa lý")
        self.assertNotIn("toanmath", lsdl.lower())
        self.assertEqual(lsdl, "")

        next(s for s in at.selectbox if s.label == "📚 Môn học cần hỗ trợ:").select("Tin học").run(timeout=90)
        tin = self._link_url(at, "Tin học")
        self.assertEqual(tin, "https://tinhoc2018.edu.vn")
        src = next(s for s in at.selectbox if "Chọn chuyên trang" in s.label)
        self.assertNotIn("TOANMATH", str(src.options[0]))
        self.assertTrue(any("Tin" in str(o) for o in src.options))

        next(s for s in at.selectbox if s.label == "📚 Môn học cần hỗ trợ:").select("Ngữ văn").run(timeout=90)
        van = self._link_url(at, "Ngữ văn")
        self.assertEqual(van, "https://nguvan2018.edu.vn")
        src = next(s for s in at.selectbox if "Chọn chuyên trang" in s.label)
        self.assertNotIn("TOANMATH", str(src.options[0]))
        self.assertIn("Ngữ Văn", str(src.options[0]))


if __name__ == "__main__":
    unittest.main()
