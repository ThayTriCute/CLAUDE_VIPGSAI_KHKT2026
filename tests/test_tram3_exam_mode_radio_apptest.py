# -*- coding: utf-8 -*-
"""AppTest: mỗi môn lớp 6–12 đổi đúng panel hình thức đề, và nút AI gửi đúng môn."""
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

    def _mode(self, at):
        return next(r for r in at.radio if r.label == "Lựa chọn hình thức đề thi:")

    def _practice_buttons(self, at):
        needles = ("Trộn Siêu Đề", "Trích Xuất Đề", "Mở đề gốc", "Khởi Tạo Đề", "AI Tạo Đề")
        return [b.label for b in at.button if any(n in b.label for n in needles)]

    def _set_mode(self, at, needle: str):
        mode = self._mode(at)
        mode.set_value(next(o for o in mode.options if needle in str(o))).run(timeout=90)
        self.assertEqual([e.message for e in at.exception], [])
        return at

    def test_every_subject_switches_panel_and_ai_stays_on_subject(self):
        from services.academic_context import subjects_for_grade

        for grade in range(6, 13):
            subjects = subjects_for_grade(grade)
            at = self._open(f"Lớp {grade}", subjects[0])
            for subject in subjects:
                with self.subTest(subject=subject, grade=grade):
                    if subject != subjects[0]:
                        next(s for s in at.selectbox if s.label == "📚 Môn học cần hỗ trợ:").select(subject).run(timeout=90)
                        self.assertEqual([e.message for e in at.exception], [])
                    options = [str(o) for o in self._mode(at).options]
                    self.assertEqual(len(options), 4, msg=f"{subject} L{grade}")
                    self.assertTrue(self._practice_buttons(at), msg=f"{subject} L{grade} thiếu nút luyện tập")

                    marker = f"ONLY {subject} L{grade}"
                    area = next(t for t in at.text_area if "Yêu cầu ma trận" in t.label)
                    area.set_value(marker).run(timeout=90)
                    self.assertEqual([e.message for e in at.exception], [])
                    seen = []

                    def _capture(subj, g, topics, counts, code, custom, pathway=""):
                        seen.append((subj, int(g), tuple(topics), str(custom or "")))
                        return ("qa-system", "qa-prompt")

                    with patch("services.curriculum_policy.exam_generation_request", side_effect=_capture):
                        btn = next(b for b in at.button if "Khởi Tạo Đề" in b.label or "AI Tạo Đề" in b.label)
                        btn.click().run(timeout=90)
                    self.assertEqual([e.message for e in at.exception], [])
                    self.assertEqual(at.session_state.get("exam_state"), "config")
                    self.assertTrue(seen, msg=f"{subject} L{grade} không gọi yêu cầu AI")
                    self.assertEqual(seen[-1][0], subject)
                    self.assertEqual(seen[-1][1], grade)
                    self.assertTrue(any(f"Lớp {grade}" in t for t in seen[-1][2]), msg=seen[-1][2])
                    self.assertIn(marker, seen[-1][3])
                    self.assertIn("GEMINI_API_KEY", " ".join(str(e.value) for e in at.error))

                    self._set_mode(at, "Nạp & Trộn Đề Word")
                    blob = " ".join(str(m.value) for m in at.markdown)
                    self.assertIn("Nạp Đề Thi Từ File Word", blob)
                    self.assertEqual(self._practice_buttons(at), [])

                    self._set_mode(at, "Quét Đề Link")
                    blob = " ".join(str(m.value) for m in at.markdown)
                    self.assertIn("Quét Đề Từ Link", blob)
                    self.assertTrue(any("Chọn chuyên trang" in s.label for s in at.selectbox))
                    self.assertEqual(self._practice_buttons(at), [])

                    self._set_mode(at, "Làm Nguyên Đề Thi Thật")
                    self.assertEqual(at.session_state.get("exam_state"), "config")
                    has_picker = any(str(s.label).startswith("Chọn đề") for s in at.selectbox)
                    infos = " ".join(str(i.value) for i in at.info)
                    self.assertTrue(
                        has_picker or (subject in infos and f"lớp {grade}" in infos),
                        msg=f"{subject} L{grade} không mở kho đề thật",
                    )
                    self.assertEqual(self._practice_buttons(at), [])


if __name__ == "__main__":
    unittest.main()
