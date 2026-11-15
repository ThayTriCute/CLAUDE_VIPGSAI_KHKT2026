# -*- coding: utf-8 -*-
"""Kho đề thật trống: báo đúng môn–lớp và không mở nút luyện tập."""
from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from streamlit.testing.v1 import AppTest


class Tram3EmptyBankAppTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import database
        cls._prev_baseline = os.environ.get("GSAI_LOAD_BASELINE_MASTER")
        os.environ["GSAI_LOAD_BASELINE_MASTER"] = "0"
        cls.temp = tempfile.TemporaryDirectory()
        cls.db = database.DatabaseManager(Path(cls.temp.name) / "tram3_empty_bank.db")
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

    def test_empty_bank_names_subject_and_hides_practice(self):
        from services.academic_context import subjects_for_grade

        needles = ("Trộn Siêu Đề", "Trích Xuất Đề", "Mở đề gốc", "Khởi Tạo Đề", "AI Tạo Đề")
        with patch("real_exam_engine.get_baseline_full_exams", return_value=[]):
            for grade in range(6, 13):
                subjects = subjects_for_grade(grade)
                at = self._open(f"Lớp {grade}", subjects[0])
                for subject in subjects:
                    with self.subTest(subject=subject, grade=grade):
                        if subject != subjects[0]:
                            next(s for s in at.selectbox if s.label == "📚 Môn học cần hỗ trợ:").select(subject).run(timeout=90)
                        mode = next(r for r in at.radio if r.label == "Lựa chọn hình thức đề thi:")
                        mode.set_value(next(o for o in mode.options if "Làm Nguyên Đề Thi Thật" in str(o))).run(timeout=90)
                        self.assertEqual([e.message for e in at.exception], [])
                        self.assertEqual(at.session_state.get("exam_state"), "config")
                        infos = " ".join(str(i.value) for i in at.info)
                        self.assertIn(subject, infos)
                        self.assertIn(f"lớp {grade}", infos)
                        self.assertIn("không mở đề luyện tập", infos)
                        practice = [b.label for b in at.button if any(n in b.label for n in needles)]
                        self.assertEqual(practice, [], msg=f"{subject} L{grade}")


if __name__ == "__main__":
    unittest.main()
