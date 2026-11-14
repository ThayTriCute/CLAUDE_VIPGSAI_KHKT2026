# -*- coding: utf-8 -*-
"""AppTest: cấu hình Trạm 3 (số câu / thời lượng / danh mục môn) đúng môn×lớp."""
from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

from services.academic_context import subjects_for_grade
from services.curriculum_policy import assessment_profile


class Tram3ConfigAppTestMatrix(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import database
        # Máy hẹp: ma trận AppTest dài dễ OOM nếu nạp baseline master.
        cls._prev_baseline = os.environ.get("GSAI_LOAD_BASELINE_MASTER")
        os.environ["GSAI_LOAD_BASELINE_MASTER"] = "0"
        cls.temp = tempfile.TemporaryDirectory()
        cls.db = database.DatabaseManager(Path(cls.temp.name) / "tram3_cfg.db")
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

    def _app(self):
        at = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=60)
        at.secrets["ADMIN_PASS"] = "qa-private-password"
        at.run()
        self.assertEqual([e.message for e in at.exception], [])
        return at

    def _open_tram3(self, at, grade_label: str, subject: str):
        next(s for s in at.selectbox if s.label == "🎯 Chọn khối lớp:").select(grade_label).run()
        next(s for s in at.selectbox if s.label == "📚 Môn học cần hỗ trợ:").select(subject).run()
        at.session_state["selected_station"] = "📝 Trạm 3: Luyện Tập & Khảo Thí"
        at.run()
        self.assertEqual([e.message for e in at.exception], [])

    def test_config_defaults_match_assessment_profile_matrix(self):
        cells = [
            ("Lớp 6", "Toán học", 6),
            ("Lớp 6", "Ngữ văn", 6),
            ("Lớp 7", "Toán học", 7),
            ("Lớp 7", "Giáo dục công dân", 7),
            ("Lớp 8", "Khoa học tự nhiên", 8),
            ("Lớp 8", "Tiếng Anh", 8),
            ("Lớp 9", "Lịch sử & Địa lý", 9),
            ("Lớp 9", "Tin học", 9),
            ("Lớp 10", "Sinh học", 10),
            ("Lớp 10", "Tin học", 10),
            ("Lớp 11", "Hóa học", 11),
            ("Lớp 11", "Giáo dục kinh tế và pháp luật", 11),
            ("Lớp 12", "Toán học", 12),
            ("Lớp 12", "Vật lý", 12),
            ("Lớp 12", "Lịch sử", 12),
            ("Lớp 12", "Tiếng Anh", 12),
            ("Lớp 12", "Địa lý", 12),
            ("Lớp 12", "Ngữ văn", 12),
        ]
        at = self._app()
        for grade_label, subject, grade in cells:
            with self.subTest(grade=grade, subject=subject):
                self._open_tram3(at, grade_label, subject)
                profile = assessment_profile(subject, grade)
                def_p1, def_p2, def_p3 = profile["counts"]
                if subject == "Ngữ văn":
                    continue
                self.assertEqual(next(n for n in at.number_input if n.label == "Số câu TN P.I:").value, def_p1)
                self.assertEqual(next(n for n in at.number_input if n.label == "Số câu Đ/S P.II:").value, def_p2)
                self.assertEqual(next(n for n in at.number_input if n.label == "Số câu TLN P.III:").value, def_p3)
                self.assertEqual(
                    next(s for s in at.selectbox if s.label == "⏱️ Thời lượng bài thi (Phút):").value,
                    profile["minutes"],
                )
                subjects = next(s for s in at.selectbox if s.label == "📚 Môn học cần hỗ trợ:").options
                for expected in subjects_for_grade(grade):
                    self.assertIn(expected, subjects)
                if grade <= 9:
                    self.assertNotIn("Vật lý", subjects)
                if grade >= 10:
                    self.assertNotIn("Khoa học tự nhiên", subjects)

    def test_testing_shows_socratic_hints_without_locking_until_submit(self):
        """Chốt anh: lúc làm bài phải có HD Socratic (không lộ đáp án); explain sau nộp."""
        at = self._app()
        self._open_tram3(at, "Lớp 12", "Toán học")
        at.session_state["exam_state"] = "testing"
        at.session_state["tram3_sealed_mode"] = False
        at.session_state["exam_data"] = {
            "code": "SOCHD",
            "subject": "Toán học",
            "grade": 12,
            "p1": [{"q": "Cho f(x)=x^2. Tìm f(2)?", "opt": ["A.1", "B.4", "C.3", "D.2"], "ans": "B"}],
            "p2": [],
            "p3": [],
        }
        at.session_state["exam_context"] = {
            "name": "QA", "grade": "Lớp 12", "subject": "Toán học", "student_id": "qa-soc"
        }
        at.session_state["exam_deadline"] = 9e12
        at.session_state["attempt_id"] = "qa-soc-hd"
        at.run(timeout=90)
        self.assertEqual([e.message for e in at.exception], [])
        captions = " ".join(c.value for c in at.caption)
        self.assertIn("không lộ đáp án", captions.lower())
        self.assertIn("sau khi nộp bài", captions.lower())
        expander_labels = [str(e.label) for e in at.expander]
        self.assertTrue(
            any("Gợi mở tư duy Socratic câu" in lab for lab in expander_labels),
            msg=f"Missing Socratic expanders during testing: {expander_labels[:8]}",
        )


if __name__ == "__main__":
    unittest.main()
