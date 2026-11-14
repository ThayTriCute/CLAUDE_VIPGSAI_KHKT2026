# -*- coding: utf-8 -*-
"""AppTest: nút trộn đề Trạm 3 → testing đúng môn/lớp (mock bank)."""
from __future__ import annotations

import os
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
        cls._prev_baseline = os.environ.get("GSAI_LOAD_BASELINE_MASTER")
        os.environ["GSAI_LOAD_BASELINE_MASTER"] = "0"
        cls.temp = tempfile.TemporaryDirectory()
        cls.db = database.DatabaseManager(Path(cls.temp.name) / "tram3_blend_btn.db")
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
        from services.academic_context import subjects_for_grade

        cells = []
        # Quét cứng: mọi môn hợp lệ mốc 6/8/9/10/12 (mock). Văn → test_tram3_nguvan_apptest.
        for grade in (6, 8, 9, 10, 12):
            for subject in subjects_for_grade(grade):
                if subject == "Ngữ văn":
                    continue
                counts = (4, 0, 0) if subject == "Tiếng Anh" else (3, 1, 0)
                cells.append((f"Lớp {grade}", subject, grade, counts))
        self.assertGreaterEqual(len(cells), 20)
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

    def test_blend_button_grades_7_and_11(self):
        """Bổ sung mốc 7/11 (các mốc khác đã cover ở test trên)."""
        from services.academic_context import subjects_for_grade

        cells = []
        for grade in (7, 11):
            for subject in subjects_for_grade(grade):
                if subject == "Ngữ văn":
                    continue
                counts = (4, 0, 0) if subject == "Tiếng Anh" else (3, 1, 0)
                cells.append((f"Lớp {grade}", subject, grade, counts))
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
                self.assertEqual((at.session_state.get("exam_data") or {}).get("subject"), subject)


if __name__ == "__main__":
    unittest.main()
