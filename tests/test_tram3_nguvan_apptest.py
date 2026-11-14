# -*- coding: utf-8 -*-
"""AppTest: Trạm 3 Ngữ văn — config tự luận + testing không lộ đáp án."""
from __future__ import annotations

import os
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

from streamlit.testing.v1 import AppTest


class Tram3NguVanAppTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import database
        cls._prev_baseline = os.environ.get("GSAI_LOAD_BASELINE_MASTER")
        os.environ["GSAI_LOAD_BASELINE_MASTER"] = "0"
        cls.temp = tempfile.TemporaryDirectory()
        cls.db = database.DatabaseManager(Path(cls.temp.name) / "tram3_van.db")
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

    def _open(self, grade_label="Lớp 12"):
        at = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=60)
        at.secrets["ADMIN_PASS"] = "qa-private-password"
        at.run()
        next(s for s in at.selectbox if s.label == "🎯 Chọn khối lớp:").select(grade_label).run()
        next(s for s in at.selectbox if s.label == "📚 Môn học cần hỗ trợ:").select("Ngữ văn").run()
        at.session_state["selected_station"] = "📝 Trạm 3: Luyện Tập & Khảo Thí"
        at.session_state["exam_state"] = "config"
        at.run(timeout=90)
        self.assertEqual([e.message for e in at.exception], [])
        return at

    def test_config_essay_mode_hides_mcq_counts(self):
        for grade_label in ("Lớp 6", "Lớp 9", "Lớp 12"):
            with self.subTest(grade=grade_label):
                at = self._open(grade_label)
                infos = " ".join(str(i.value) for i in at.info)
                self.assertIn("Tự luận", infos)
                mcq_labels = [n.label for n in at.number_input if "TN P.I" in n.label or "Đ/S P.II" in n.label]
                self.assertEqual(mcq_labels, [], msg="Ngữ văn không hiện số câu TN/ĐS")
                time_box = next(s for s in at.selectbox if s.label == "⏱️ Thời lượng bài thi (Phút):")
                self.assertGreater(time_box.value, 0)

    def test_testing_shows_socratic_without_answer_leak(self):
        at = self._open("Lớp 12")
        at.session_state["exam_state"] = "testing"
        at.session_state["tram3_sealed_mode"] = False
        at.session_state["exam_data"] = {
            "code": "VAN1",
            "subject": "Ngữ văn",
            "grade": 12,
            "part_doc_hieu": {
                "text": "Ngữ liệu đọc hiểu QA — không chứa đáp án.",
                "questions": [
                    {
                        "q": "Nêu nội dung chính của đoạn trích.",
                        "ans": "ĐÁP ÁN BÍ MẬT KHÔNG ĐƯỢC LỘ",
                        "explain": "Giải thích chi tiết không hiện khi đang làm.",
                    }
                ],
            },
            "part_viet": [
                {
                    "q": "Viết đoạn nghị luận về lòng yêu nước.",
                    "ans": "ĐÁP ÁN VIẾT BÍ MẬT",
                    "explain": "Explain viết không hiện khi đang làm.",
                }
            ],
            "p1": [],
            "p2": [],
            "p3": [],
        }
        at.session_state["exam_context"] = {
            "name": "QA", "grade": "Lớp 12", "subject": "Ngữ văn", "student_id": "qa-van"
        }
        at.session_state["exam_deadline"] = time.time() + 600
        at.session_state["attempt_id"] = "qa-van-1"
        at.session_state["exam_answers"] = {}
        at.run(timeout=90)
        self.assertEqual([e.message for e in at.exception], [])
        blob = " ".join(str(m.value) for m in at.markdown) + " ".join(str(e.label) for e in at.expander)
        self.assertNotIn("ĐÁP ÁN BÍ MẬT KHÔNG ĐƯỢC LỘ", blob)
        self.assertNotIn("ĐÁP ÁN VIẾT BÍ MẬT", blob)
        self.assertNotIn("Giải thích chi tiết không hiện khi đang làm.", blob)
        self.assertNotIn("Explain viết không hiện khi đang làm.", blob)
        self.assertTrue(any("Gợi mở tư duy Socratic" in str(e.label) for e in at.expander))
        self.assertTrue(any("Trả lời câu" in t.label for t in at.text_area))
        self.assertTrue(any("Bài làm viết" in t.label for t in at.text_area))


if __name__ == "__main__":
    unittest.main()
