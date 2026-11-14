# -*- coding: utf-8 -*-
"""AppTest: làm bài kín tắt Socratic; sau nộp mới có Explain; nút tùy biến + radio Tin 12."""
from __future__ import annotations

import os
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

from streamlit.testing.v1 import AppTest


class Tram3SealedGradedAppTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import database
        cls._prev_baseline = os.environ.get("GSAI_LOAD_BASELINE_MASTER")
        os.environ["GSAI_LOAD_BASELINE_MASTER"] = "0"
        cls.temp = tempfile.TemporaryDirectory()
        cls.db = database.DatabaseManager(Path(cls.temp.name) / "tram3_sealed.db")
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

    def _app(self, grade_label="Lớp 12", subject="Toán học"):
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

    def _seed_testing(self, at, sealed: bool):
        at.session_state["exam_state"] = "testing"
        at.session_state["tram3_sealed_mode"] = sealed
        at.session_state["exam_data"] = {
            "code": "SEAL1",
            "subject": "Toán học",
            "grade": 12,
            "p1": [{
                "q": "1+1 bằng bao nhiêu?",
                "opt": ["A. 1", "B. 2", "C. 3", "D. 4"],
                "ans": "B",
                "explain": "EXPLAIN_CHI_SAU_NOP_QA",
            }],
            "p2": [],
            "p3": [],
        }
        at.session_state["exam_context"] = {
            "name": "QA", "grade": "Lớp 12", "subject": "Toán học", "student_id": "qa-seal"
        }
        at.session_state["exam_deadline"] = time.time() + 600
        at.session_state["attempt_id"] = "qa-seal-1"
        at.session_state["exam_answers"] = {}
        at.run(timeout=90)
        self.assertEqual([e.message for e in at.exception], [])
        return at

    def test_sealed_hides_socratic_practice_shows_it(self):
        sealed = self._seed_testing(self._app(), sealed=True)
        labels = [str(e.label) for e in sealed.expander]
        self.assertFalse(any("Gợi mở tư duy Socratic" in lab for lab in labels))
        blob = " ".join(str(getattr(w, "value", "")) for w in list(sealed.markdown) + list(sealed.info) + list(sealed.success))
        self.assertNotIn("EXPLAIN_CHI_SAU_NOP_QA", blob)

        open_mode = self._seed_testing(self._app(), sealed=False)
        labels = [str(e.label) for e in open_mode.expander]
        self.assertTrue(any("Gợi mở tư duy Socratic" in lab for lab in labels))
        blob = " ".join(str(getattr(w, "value", "")) for w in list(open_mode.markdown) + list(open_mode.info) + list(open_mode.success))
        self.assertNotIn("EXPLAIN_CHI_SAU_NOP_QA", blob)

    def test_graded_shows_socratic_and_explain(self):
        at = self._seed_testing(self._app(), sealed=False)
        next(b for b in at.button if "Nộp bài" in b.label).click().run(timeout=90)
        self.assertEqual([e.message for e in at.exception], [])
        self.assertEqual(at.session_state.get("exam_state"), "graded")
        infos = " ".join(str(i.value) for i in at.info)
        oks = " ".join(str(s.value) for s in at.success)
        self.assertIn("EXPLAIN_CHI_SAU_NOP_QA", infos)
        self.assertIn("HD Socratic", oks)
        self.assertIn("Explain", infos)

    def test_custom_prompt_relabels_blend_and_tin12_bank_radio(self):
        at = self._app("Lớp 12", "Toán học")
        area = next(t for t in at.text_area if "Yêu cầu ma trận" in t.label)
        area.set_value("Ưu tiên đồ thị, không lộ đáp án").run()
        labels = [b.label for b in at.button]
        self.assertTrue(any("Trích Xuất Đề Tùy Biến" in lab for lab in labels))
        self.assertTrue(any("AI Tạo Đề Theo Tùy Biến" in lab for lab in labels))

        tin = self._app("Lớp 12", "Tin học")
        radios = [r.label for r in tin.radio]
        self.assertTrue(any("Cách dùng kho đề Tin học" in lab for lab in radios))


if __name__ == "__main__":
    unittest.main()
