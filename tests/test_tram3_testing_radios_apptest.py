# -*- coding: utf-8 -*-
"""AppTest: radio / Đ-S / nộp bài Trạm 3 hoạt động khi đang làm bài."""
from __future__ import annotations

import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

from streamlit.testing.v1 import AppTest


class Tram3TestingRadiosAppTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import database
        cls.temp = tempfile.TemporaryDirectory()
        cls.db = database.DatabaseManager(Path(cls.temp.name) / "tram3_radio.db")
        cls.db_patch = patch.object(database, "db_manager", cls.db)
        cls.db_patch.start()

    @classmethod
    def tearDownClass(cls):
        cls.db_patch.stop()
        cls.temp._ignore_cleanup_errors = True
        cls.temp.cleanup()

    def _app_testing(self, subject="Toán học", grade_label="Lớp 12", exam=None):
        at = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=60)
        at.secrets["ADMIN_PASS"] = "qa-private-password"
        at.run()
        next(s for s in at.selectbox if s.label == "🎯 Chọn khối lớp:").select(grade_label).run()
        next(s for s in at.selectbox if s.label == "📚 Môn học cần hỗ trợ:").select(subject).run()
        at.session_state["selected_station"] = "📝 Trạm 3: Luyện Tập & Khảo Thí"
        at.session_state["exam_state"] = "testing"
        at.session_state["tram3_sealed_mode"] = False
        at.session_state["exam_data"] = exam or {
            "code": "RADIO1",
            "subject": subject,
            "grade": 12,
            "p1": [
                {
                    "q": "1+1=?",
                    "opt": ["A. 1", "B. 2", "C. 3", "D. 4"],
                    "ans": "B",
                }
            ],
            "p2": [
                {
                    "q": "Xét các mệnh đề",
                    "stmts": [
                        {"t": "2 là số chẵn", "a": True},
                        {"t": "3 là số chẵn", "a": False},
                        {"t": "4 chia hết 2", "a": True},
                        {"t": "5 chia hết 2", "a": False},
                    ],
                }
            ],
            "p3": [{"q": "Tính 2+2", "ans": "4"}],
        }
        at.session_state["exam_context"] = {
            "name": "QA",
            "grade": grade_label,
            "subject": subject,
            "student_id": "qa-radio",
        }
        at.session_state["exam_deadline"] = time.time() + 600
        at.session_state["attempt_id"] = "qa-radio-1"
        at.session_state["exam_answers"] = {}
        at.run(timeout=90)
        self.assertEqual([e.message for e in at.exception], [])
        return at

    def test_p1_radio_p2_tf_and_submit_button(self):
        at = self._app_testing()
        p1 = next(r for r in at.radio if r.label == "Lựa chọn câu 1:")
        p1.set_value("B. 2").run()
        self.assertEqual(at.session_state.exam_answers.get("p1_0"), "B. 2")

        tf_radios = [r for r in at.radio if str(r.label).startswith("Chọn Đúng/Sai")]
        self.assertEqual(len(tf_radios), 4)
        tf_radios[0].set_value("Đúng").run()
        self.assertEqual(at.session_state.exam_answers.get("p2_0_0"), "Đúng")

        submit = next(b for b in at.button if "Nộp bài" in b.label)
        submit.click().run(timeout=90)
        self.assertEqual([e.message for e in at.exception], [])
        self.assertEqual(at.session_state.get("exam_state"), "graded")

    def test_khtn_grade8_testing_radios_and_socratic(self):
        at = self._app_testing(
            subject="Khoa học tự nhiên",
            grade_label="Lớp 8",
            exam={
                "code": "RADIO8",
                "subject": "Khoa học tự nhiên",
                "grade": 8,
                "p1": [{"q": "Nước có công thức?", "opt": ["A. H2O", "B. CO2", "C. O2", "D. N2"], "ans": "A"}],
                "p2": [],
                "p3": [],
            },
        )
        p1 = next(r for r in at.radio if r.label == "Lựa chọn câu 1:")
        p1.set_value("A. H2O").run()
        self.assertEqual(at.session_state.exam_answers.get("p1_0"), "A. H2O")
        labels = [str(e.label) for e in at.expander]
        self.assertTrue(any("Gợi mở tư duy Socratic câu" in lab for lab in labels))


if __name__ == "__main__":
    unittest.main()
