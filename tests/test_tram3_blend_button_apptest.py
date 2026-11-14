# -*- coding: utf-8 -*-
"""AppTest: nút trộn đề Trạm 3 → testing đúng môn/lớp (mock bank)."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from streamlit.testing.v1 import AppTest


def _fake_exam(subject: str, grade: int, counts=(3, 1, 0)):
    n1, n2, n3 = counts
    exam = {
        "code": f"MOCK-{grade}",
        "subject": subject,
        "grade": grade,
        "p1": [
            {
                "q": f"Câu TN {i+1} {subject} L{grade}",
                "opt": ["A.1", "B.2", "C.3", "D.4"],
                "ans": "B",
                "subject": subject,
            }
            for i in range(n1)
        ],
        "p2": [
            {
                "q": f"Câu ĐS {i+1}",
                "stmts": [
                    {"t": "a", "a": True},
                    {"t": "b", "a": False},
                    {"t": "c", "a": True},
                    {"t": "d", "a": False},
                ],
                "subject": subject,
            }
            for i in range(n2)
        ],
        "p3": [{"q": f"TLN {i+1}", "ans": "1", "subject": subject} for i in range(n3)],
        "actual_counts": (n1, n2, n3),
        "target_counts": (n1, n2, n3),
    }
    return exam


class Tram3BlendButtonAppTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import database
        cls.temp = tempfile.TemporaryDirectory()
        cls.db = database.DatabaseManager(Path(cls.temp.name) / "tram3_blend_btn.db")
        cls.db_patch = patch.object(database, "db_manager", cls.db)
        cls.db_patch.start()

    @classmethod
    def tearDownClass(cls):
        cls.db_patch.stop()
        cls.temp._ignore_cleanup_errors = True
        cls.temp.cleanup()

    def _open_tram3(self, grade_label: str, subject: str):
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

    def test_blend_button_starts_testing_for_matrix_cells(self):
        cells = [
            ("Lớp 6", "Toán học", 6, (3, 1, 0)),
            ("Lớp 8", "Khoa học tự nhiên", 8, (3, 1, 0)),
            ("Lớp 9", "Lịch sử & Địa lý", 9, (3, 1, 0)),
            ("Lớp 10", "Tin học", 10, (3, 1, 0)),
            ("Lớp 11", "Hóa học", 11, (3, 1, 0)),
            ("Lớp 12", "Vật lý", 12, (3, 1, 0)),
            ("Lớp 12", "Tiếng Anh", 12, (4, 0, 0)),
            ("Lớp 12", "Lịch sử", 12, (4, 1, 0)),
        ]
        for grade_label, subject, grade, counts in cells:
            with self.subTest(subject=subject, grade=grade):
                at = self._open_tram3(grade_label, subject)
                fake = _fake_exam(subject, grade, counts)

                def _gen(subj, g, topics, cnts, **kwargs):
                    self.assertEqual(subj, subject)
                    self.assertEqual(g, grade)
                    return fake

                with patch("real_exam_engine.generate_blended_real_exam", side_effect=_gen):
                    btn = next(
                        b
                        for b in at.button
                        if "Trộn Siêu Đề" in b.label or "Trích Xuất Đề" in b.label or "Mở đề gốc" in b.label
                    )
                    btn.click().run(timeout=90)
                self.assertEqual([e.message for e in at.exception], [])
                self.assertEqual(at.session_state.get("exam_state"), "testing")
                exam = at.session_state.get("exam_data") or {}
                self.assertEqual(exam.get("subject"), subject)
                radios = [r for r in at.radio if str(r.label).startswith("Lựa chọn câu")]
                self.assertGreaterEqual(len(radios), 1)


if __name__ == "__main__":
    unittest.main()
