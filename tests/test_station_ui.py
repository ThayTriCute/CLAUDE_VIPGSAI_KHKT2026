"""Streamlit UI regressions without a live Gemini call or production database."""
import tempfile
import time
import unittest
import json
from types import SimpleNamespace
from pathlib import Path
from unittest.mock import patch

from streamlit.testing.v1 import AppTest
from tests.lesson_samples import complete_lesson


class TestStationUI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import database
        cls.temp = tempfile.TemporaryDirectory()
        cls.db = database.DatabaseManager(Path(cls.temp.name) / "ui.db")
        cls.db_patch = patch.object(database, "db_manager", cls.db)
        cls.db_patch.start()

    @classmethod
    def tearDownClass(cls):
        cls.db_patch.stop()
        # AppTest creates worker-thread-local connections. Keep test cleanup independent
        # of Windows handle lifetime; TemporaryDirectory cleanup waits for process exit.
        cls.temp._ignore_cleanup_errors = True
        cls.temp.cleanup()

    def app(self):
        at = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=45)
        at.secrets["ADMIN_PASS"] = "qa-private-password"
        at.run()
        self.assertEqual([e.message for e in at.exception], [])
        return at

    def test_station1_preset_lab_and_grade_context_reset(self):
        at = self.app()
        next(b for b in at.button if b.label == "Mở mô phỏng có sẵn").click().run()
        self.assertEqual([e.message for e in at.exception], [])
        at.session_state["t3_p3_0"] = "old-answer"
        at.session_state["tram1_chat_history"] = [{"role": "user", "content": "old context"}]
        next(s for s in at.selectbox if s.label == "🎯 Chọn khối lớp:").select("Lớp 6").run()
        self.assertEqual([e.message for e in at.exception], [])
        self.assertNotIn("t3_p3_0", at.session_state)
        self.assertEqual(at.session_state["tram1_chat_history"], [])
        subjects = next(s for s in at.selectbox if s.label == "📚 Môn học cần hỗ trợ:").options
        self.assertIn("Khoa học tự nhiên", subjects)
        self.assertNotIn("Vật lý", subjects)

    def test_station2_empty_session_has_no_fake_mastery(self):
        at = self.app()
        at.session_state["selected_station"] = "✍️ Trạm 2: Gia Sư Socratic & Nộp Bài"
        at.run()
        self.assertEqual([e.message for e in at.exception], [])
        self.assertEqual(at.session_state["tram2_count"], 0)
        self.assertFalse(any("85.4%" in m.value for m in at.markdown))

    def test_station_navigation_keeps_attempt_and_answers(self):
        at = self.app()
        at.session_state["exam_state"] = "testing"
        at.session_state["exam_data"] = {"code": "QA-NAV",
            "p1": [{"q": "Tính 2 + 1.", "opt": ["A. 1", "B. 3", "C. 4", "D. 5"], "ans": "B"}],
            "p2": [{"q": "Xét các số", "stmts": [{"t": "3 > 2", "a": True}, {"t": "2 > 1", "a": True}, {"t": "1 > 2", "a": False}, {"t": "3 = 3", "a": True}]}],
            "p3": [{"q": "Tính 2 + 1.", "ans": "3"}]}
        at.session_state["exam_context"] = {"name": "QA", "grade": "Lớp 12", "subject": "Toán học", "student_id": "qa-nav"}
        deadline = time.time() + 300
        at.session_state["exam_deadline"] = deadline
        at.session_state["attempt_id"] = "qa-nav"
        next(b for b in at.button if b.key == "top_nav_station_2").click().run()
        next(r for r in at.radio if r.key == "t3_p1_0").set_value("B. 3").run()
        next(r for r in at.radio if r.key == "t3_p2_0_0").set_value("Đúng").run()
        next(t for t in at.text_input if t.label == "Nhập đáp số câu 1:").set_value("3").run()
        for index in (1, 3, 2):
            next(b for b in at.button if b.key == f"top_nav_station_{index}").click().run()
            self.assertEqual([e.message for e in at.exception], [])
        self.assertEqual(at.session_state["attempt_id"], "qa-nav")
        self.assertEqual(at.session_state["exam_deadline"], deadline)
        self.assertEqual(at.session_state["exam_answers"]["p3_0"], "3")
        self.assertEqual(next(r for r in at.radio if r.key == "t3_p1_0").value, "B. 3")
        self.assertEqual(next(r for r in at.radio if r.key == "t3_p2_0_0").value, "Đúng")
        self.assertEqual(next(t for t in at.text_input if t.label == "Nhập đáp số câu 1:").value, "3")
        self.assertEqual(at.session_state["sb_station_radio_selector"], at.session_state["selected_station"])

    def test_generated_lesson_export_is_bound_to_subject_and_grade(self):
        at = self.app()
        at.secrets["GEMINI_API_KEY"] = "test-only-key"
        next(s for s in at.selectbox if s.label == "🎯 Chọn khối lớp:").select("Lớp 6").run()
        next(t for t in at.text_input if "Bài học cần chiếm lĩnh" in t.label).set_value("Phân số")
        lesson = complete_lesson("Chỉ có nội dung lớp 6. Phân số $\\frac{1}{2}$.")
        with patch("google.genai.Client") as client:
            client.return_value.__enter__.return_value.models.generate_content.return_value = SimpleNamespace(text=lesson, candidates=[])
            next(b for b in at.button if b.label == "🚀 Soạn bài học").click().run()
        self.assertEqual([e.message for e in at.exception], [])
        self.assertEqual(at.session_state["current_lesson_context"], ("Toán học", 6))
        self.assertEqual(at.session_state["current_topic"], "Phân số")
        self.assertIn("lớp 6", at.session_state["current_lesson"])
        next(s for s in at.selectbox if s.label == "🎯 Chọn khối lớp:").select("Lớp 7").run()
        self.assertEqual(at.session_state["current_lesson"], "")
        self.assertEqual([e.message for e in at.exception], [])

    def test_generated_lesson_repairs_missing_questions_and_hides_solution_metadata(self):
        at = self.app()
        at.secrets["GEMINI_API_KEY"] = "test-only-key"
        next(s for s in at.selectbox if s.label == "🎯 Chọn khối lớp:").select("Lớp 6").run()
        next(t for t in at.text_input if "Bài học cần chiếm lĩnh" in t.label).set_value("Phân số")
        repaired = complete_lesson()
        with patch("google.genai.Client") as client:
            generate = client.return_value.__enter__.return_value.models.generate_content
            generate.side_effect = [SimpleNamespace(text="### PHẦN 1: BÀI HỌC\nBài còn thiếu cấu trúc.", candidates=[]), SimpleNamespace(text=repaired, candidates=[])]
            next(b for b in at.button if b.label == "🚀 Soạn bài học").click().run()
            self.assertEqual(generate.call_count, 2)
        self.assertEqual([e.message for e in at.exception], [])
        self.assertEqual(len(at.session_state["parsed_quiz"]), 3)
        displayed = "\n".join(str(m.value) for m in at.markdown)
        self.assertEqual(displayed.count("Bước 1: Tìm hiểu đề"), 2)
        self.assertEqual(displayed.count("Bước 4: Kiểm tra và nhìn lại"), 2)
        for forbidden in ("PRIVATE_ANSWER_77", "PRIVATE_REASONING", "COGNITIVE_STEPS", "Understand the problem", "ĐÁP ÁN:"):
            self.assertNotIn(forbidden, displayed)

    def test_lesson_still_missing_structure_after_retry_is_not_published(self):
        at = self.app()
        at.secrets["GEMINI_API_KEY"] = "test-only-key"
        next(t for t in at.text_input if "Bài học cần chiếm lĩnh" in t.label).set_value("Hàm số")
        with patch("google.genai.Client") as client:
            generate = client.return_value.__enter__.return_value.models.generate_content
            generate.return_value = SimpleNamespace(text="### PHẦN 1: BÀI HỌC\nChỉ có lý thuyết.", candidates=[])
            next(b for b in at.button if b.label == "🚀 Soạn bài học").click().run()
            self.assertEqual(generate.call_count, 2)
        self.assertFalse(at.session_state.get("current_lesson", ""))
        self.assertEqual([e.message for e in at.exception], [])

    def test_lesson_suggestion_updates_form_input_without_calling_ai(self):
        at = self.app()
        select = next(s for s in at.selectbox if s.label == "🎯 Chọn chủ đề gợi ý theo môn/lớp:")
        value = select.options[1]
        with patch("google.genai.Client") as client:
            select.select(value).run()
            self.assertFalse(client.called)
        field = next(t for t in at.text_input if "Bài học cần chiếm lĩnh" in t.label)
        self.assertEqual(field.value, value.split(":")[-1].strip())
        self.assertEqual([e.message for e in at.exception], [])

    def test_stale_unbound_lesson_is_not_exported_as_current_subject(self):
        at = self.app()
        at.session_state["current_lesson"] = "Bài Hóa học lớp 12 từ phiên cũ."
        at.run()
        self.assertEqual(at.session_state["current_lesson"], "")
        self.assertIn("Hóa học", at.session_state["orphaned_lesson"])

    def test_station1_chemistry_options_render_and_still_grade_original_answer(self):
        at = self.app()
        at.secrets["GEMINI_API_KEY"] = "test-only-key"
        next(s for s in at.selectbox if s.label == "🎯 Chọn khối lớp:").select("Lớp 10").run()
        next(s for s in at.selectbox if s.label == "📚 Môn học cần hỗ trợ:").select("Hóa học").run()
        next(t for t in at.text_input if "Bài học cần chiếm lĩnh" in t.label).set_value("Kí hiệu hóa học")
        lesson = complete_lesson(r"Nước có công thức $\ce{H2O}$.", chemistry=True)
        with patch("google.genai.Client") as client:
            client.return_value.__enter__.return_value.models.generate_content.return_value = SimpleNamespace(text=lesson, candidates=[])
            next(b for b in at.button if b.label == "🚀 Soạn bài học").click().run()
        self.assertEqual([e.message for e in at.exception], [])
        self.assertTrue(any('class="katex' in m.value for m in at.markdown))
        radio = next(r for r in at.radio if r.label == "Chọn đáp án câu 1:")
        from services.math_publication import native_radio_label
        self.assertEqual(radio.options, [native_radio_label(value) for value in at.session_state["parsed_quiz"][0]["options"]])
        self.assertTrue(all(len(value) > 2 for value in radio.options))
        water_index = next(i for i, option in enumerate(at.session_state["parsed_quiz"][0]["options"]) if "H2O" in option)
        radio.set_value(at.session_state["parsed_quiz"][0]["options"][water_index]).run()
        next(b for b in at.button if b.label == "🔍 Kiểm tra câu 1").click().run()
        self.assertEqual(at.session_state["quiz_states"][0][0], "correct")
        self.assertEqual([e.message for e in at.exception], [])
        self.assertEqual([e.message for e in at.exception], [])

    def test_station3_grade6_uses_practice_counts_not_graduation(self):
        at = self.app()
        next(s for s in at.selectbox if s.label == "🎯 Chọn khối lớp:").select("Lớp 6").run()
        at.session_state["selected_station"] = "📝 Trạm 3: Luyện Tập & Khảo Thí"
        at.run()
        self.assertEqual([e.message for e in at.exception], [])
        self.assertEqual(next(n for n in at.number_input if n.label == "Số câu TLN P.III:").value, 2)
        self.assertEqual(next(s for s in at.selectbox if s.label == "⏱️ Thời lượng bài thi (Phút):").value, 45)
        self.assertTrue(any("Luyện tập theo lớp" in c.value for c in at.caption))

    def test_station3_geography_has_six_short_answers(self):
        at = self.app()
        next(s for s in at.selectbox if s.label == "📚 Môn học cần hỗ trợ:").select("Địa lý").run()
        at.session_state["selected_station"] = "📝 Trạm 3: Luyện Tập & Khảo Thí"
        at.run()
        self.assertEqual([e.message for e in at.exception], [])
        self.assertEqual(next(n for n in at.number_input if n.label == "Số câu TN P.I:").value, 18)
        self.assertEqual(next(n for n in at.number_input if n.label == "Số câu TLN P.III:").value, 6)

    def test_station1_blocks_explicit_different_grade_before_ai(self):
        at = self.app()
        next(s for s in at.selectbox if s.label == "🎯 Chọn khối lớp:").select("Lớp 6").run()
        next(t for t in at.text_input if "Bài học cần chiếm lĩnh" in t.label).set_value("Tích phân lớp 12")
        with patch("google.genai.Client") as client:
            next(b for b in at.button if b.label == "🚀 Soạn bài học").click().run()
            client.assert_not_called()
        self.assertEqual(at.session_state["current_lesson"], "")
        self.assertEqual([e.message for e in at.exception], [])

    def test_station3_generation_replaces_a_whole_missing_visual_question(self):
        import real_exam_engine as engine
        at = self.app()
        at.secrets["GEMINI_API_KEY"] = "test-only-key"
        at.session_state["selected_station"] = "📝 Trạm 3: Luyện Tập & Khảo Thí"
        at.run()
        for label, value in (("Số câu TN P.I:", 1), ("Số câu Đ/S P.II:", 0), ("Số câu TLN P.III:", 0)):
            next(n for n in at.number_input if n.label == label).set_value(value)
        initial = {"subject": "Toán học", "grade": 12, "p1": [{"q": "Quan sát hình vẽ bên để chọn hàm số", "topic": "Hàm số", "opt": ["A. 1", "B. 2", "C. 3", "D. 4"], "ans": "B"}], "p2": [], "p3": []}
        replacement = {"subject": "Toán học", "grade": 12, "topic": "Hàm số", "q": "Đồ thị như hình bên của $y=x^3+2$. Tung độ giao Oy bằng bao nhiêu?", "opt": ["A. 1", "B. 2", "C. 3", "D. 4"], "ans": "B"}
        with patch("google.genai.Client") as client, patch.object(engine, "get_baseline_questions_pool", return_value={"p1": [], "p2": [], "p3": []}):
            response = client.return_value.__enter__.return_value.models.generate_content
            response.side_effect = [SimpleNamespace(text=json.dumps(initial), candidates=[]),
                                    SimpleNamespace(text=json.dumps({"replacement_question": dict(replacement, q=initial["p1"][0]["q"])}), candidates=[]),
                                    SimpleNamespace(text=json.dumps({"replacement_question": replacement}), candidates=[])]
            next(b for b in at.button if b.label == "🚀 Khởi Tạo Đề Mới (AI Sáng Tạo 2026)").click().run()
        self.assertEqual([e.message for e in at.exception], [])
        self.assertEqual(at.session_state["exam_state"], "testing")
        self.assertEqual(at.session_state["exam_data"]["p1"][0]["q"], replacement["q"])
        self.assertIn("f", at.session_state["exam_data"]["p1"][0])
        self.assertEqual(response.call_count, 3)
        self.assertEqual(at.session_state["exam_data"]["context_recovery"]["ai_calls"], 2)
        self.assertEqual(at.session_state["exam_data"]["context_recovery"]["events"][0]["action"], "ai_replacement")
        self.assertFalse(at.session_state["exam_data"]["cognitive_audit"]["verified"])
        self.assertTrue(any("Đối soát nhãn mức độ" in expander.label for expander in at.expander))

    def test_station3_wrong_decimal_gets_zero_and_saves_one_event(self):
        at = self.app()
        at.session_state["selected_station"] = "📝 Trạm 3: Luyện Tập & Khảo Thí"
        at.session_state["exam_state"] = "testing"
        at.session_state["exam_data"] = {"code": "QA01", "p1": [], "p2": [], "p3": [{"q": "Tìm giá trị cực đại của $y=-x^3+3x+1$.", "ans": "3"}]}
        at.session_state["exam_context"] = {"name": "QA UI", "grade": "Lớp 12", "subject": "Toán học", "student_id": "qa-ui"}
        at.session_state["exam_deadline"] = time.time() + 90
        at.session_state["attempt_id"] = "qa-ui-decimal"
        at.run()
        next(t for t in at.text_input if t.label == "Nhập đáp số câu 1:").set_value("3.4").run()
        next(b for b in at.button if b.label == "🏁 Nộp bài & Chấm điểm tức thì").click().run()
        self.assertEqual([e.message for e in at.exception], [])
        events = [e for e in at.session_state["analytics_logs"] if e.get("event_id") == "qa-ui-decimal"]
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["score"], 0)
        self.assertFalse(events[0]["answers"]["_item_results"]["p3_0"])
        at.run()
        self.assertEqual(len([e for e in at.session_state["analytics_logs"] if e.get("event_id") == "qa-ui-decimal"]), 1)

    def test_station3_accepts_complete_json_without_closing_markdown_fence(self):
        import real_exam_engine as engine
        at = self.app()
        at.secrets["GEMINI_API_KEY"] = "test-only-key"
        at.session_state["selected_station"] = "📝 Trạm 3: Luyện Tập & Khảo Thí"
        at.run()
        for label, value in (("Số câu TN P.I:", 1), ("Số câu Đ/S P.II:", 0), ("Số câu TLN P.III:", 0)):
            next(n for n in at.number_input if n.label == label).set_value(value)
        question = {"q": "Cho $y=x^3-3x+1$. Giá trị $y'(0)$ bằng bao nhiêu?",
                    "opt": ["A. -3", "B. 0", "C. 1", "D. 3"], "ans": "A"}
        exam = {"subject": "Toán học", "grade": 12, "p1": [question], "p2": [], "p3": []}
        with patch("google.genai.Client") as client, patch.object(engine, "ingest_ai_generated_exam_to_bank", return_value=None):
            generate = client.return_value.__enter__.return_value.models.generate_content
            generate.return_value = SimpleNamespace(text='```json\n' + json.dumps(exam, ensure_ascii=False), candidates=[])
            next(b for b in at.button if b.label == "🚀 Khởi Tạo Đề Mới (AI Sáng Tạo 2026)").click().run()
            self.assertEqual(generate.call_count, 1)
        self.assertEqual([e.message for e in at.exception], [])
        self.assertEqual(at.session_state["exam_state"], "testing")
        result = at.session_state["exam_data"]["p1"][0]
        self.assertEqual(result["q"], question["q"])
        self.assertEqual(result["opt"], question["opt"])
        self.assertEqual(result["ans"], "A")

    def test_station4_auth_demo_statistics_and_monte_carlo(self):
        at = self.app()
        at.session_state["selected_station"] = "📊 Trạm 4: Dữ Liệu & Nghiên Cứu"
        at.run()
        next(t for t in at.text_input if t.label == "Mật khẩu quản trị:").set_value("GiaoVienKHKT@2026")
        next(b for b in at.button if b.label == "🔓 Mở khóa").click().run()
        self.assertFalse(at.session_state.get("tab4_authenticated", False) if hasattr(at.session_state, "get") else "tab4_authenticated" in at.session_state and at.session_state["tab4_authenticated"])
        next(t for t in at.text_input if t.label == "Mật khẩu quản trị:").set_value("qa-private-password")
        next(b for b in at.button if b.label == "🔓 Mở khóa").click().run()
        self.assertTrue(at.session_state["tab4_authenticated"])
        next(r for r in at.radio if r.label == "Nguồn dữ liệu").set_value("Mô phỏng minh họa").run()
        next(b for b in at.button if b.label == "Phân tích các cặp điểm").click().run()
        self.assertEqual([e.message for e in at.exception], [])
        self.assertTrue(at.session_state["research_result"]["demo"])
        next(b for b in at.button if "Kích hoạt Mô phỏng Monte Carlo" in b.label).click().run()
        self.assertEqual([e.message for e in at.exception], [])
        self.assertFalse(any("Gaussian" in m.value and "p < 0.001" in m.value for m in at.success))

    def test_failed_json_is_retained_for_authenticated_admin_only(self):
        at = self.app()
        at.secrets["GEMINI_API_KEY"] = "test-only-key"
        at.session_state["selected_station"] = "📝 Trạm 3: Luyện Tập & Khảo Thí"
        at.run()
        raw = '{"p1":[{"q":"Bản nháp lỗi test-only-key", "ans":'
        with patch("google.genai.Client") as client:
            generate = client.return_value.__enter__.return_value.models.generate_content
            generate.return_value = SimpleNamespace(text=raw, candidates=[])
            next(b for b in at.button if b.label == "🚀 Khởi Tạo Đề Mới (AI Sáng Tạo 2026)").click().run()
            self.assertEqual(generate.call_count, 1)
        self.assertIn('_last_exam_json_failure', at.session_state)
        self.assertNotIn('test-only-key', at.session_state['_last_exam_json_failure']['raw'])
        self.assertFalse(any(b.key == 'download_failed_exam_json' for b in at.get('download_button')))
        at.session_state['selected_station'] = '📊 Trạm 4: Dữ Liệu & Nghiên Cứu'
        at.run()
        self.assertFalse(any(b.key == 'download_failed_exam_json' for b in at.get('download_button')))
        next(t for t in at.text_input if t.label == 'Mật khẩu quản trị:').set_value('qa-private-password')
        next(b for b in at.button if b.label == '🔓 Mở khóa').click().run()
        self.assertEqual([e.message for e in at.exception], [])
        self.assertTrue(any(b.key == 'download_failed_exam_json' for b in at.get('download_button')))
        # Valid JSON can fail a later structure/content gate.
        at.session_state['selected_station'] = '📝 Trạm 3: Luyện Tập & Khảo Thí'
        at.session_state['last_context_recovery'] = {'events': ['stale prior attempt']}
        at.run()
        raw_valid = json.dumps({'subject': 'Toán học', 'grade': 12, 'p1': [], 'p2': [], 'p3': []}, ensure_ascii=False)
        with patch('google.genai.Client') as client:
            generate = client.return_value.__enter__.return_value.models.generate_content
            generate.return_value = SimpleNamespace(text=raw_valid, candidates=[])
            next(b for b in at.button if b.label == '🚀 Khởi Tạo Đề Mới (AI Sáng Tạo 2026)').click().run()
            self.assertEqual(generate.call_count, 1)
        diagnostic = at.session_state['_last_exam_json_failure']
        self.assertEqual(diagnostic['raw'], raw_valid)
        self.assertEqual(diagnostic['context_recovery'], {})
        self.assertFalse(any(b.key == 'download_failed_exam_json' for b in at.get('download_button')))


if __name__ == "__main__":
    unittest.main()
