"""Streamlit UI regressions without a live Gemini call or production database."""
import tempfile
import time
import unittest
import json
from types import SimpleNamespace
from pathlib import Path
from unittest.mock import patch

from streamlit.testing.v1 import AppTest


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
        next(s for s in at.selectbox if s.label == "🎯 Chọn khối lớp:").select("Lớp 8").run()
        next(s for s in at.selectbox if s.label == "📚 Môn học cần hỗ trợ:").select("Khoa học tự nhiên").run()
        preset = next(s for s in at.selectbox if s.label == "Mô phỏng có sẵn (không cần API):")
        preset.select("Thang đo pH & Axit - Bazơ (KHTN)").run()
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

    def test_equilibrium_lab_temperature_pressure_sliders(self):
        import re
        at = self.app()
        next(s for s in at.selectbox if s.label == '📚 Môn học cần hỗ trợ:').select('Hóa học').run()
        at.session_state['lab_data'] = {'type': 'chem_equilibrium', 'temp': 450, 'p': 100}
        at.run()
        def conversion():
            self.assertEqual([e.message for e in at.exception], [])
            text = next(item.value for item in at.success if 'Mức chuyển hóa' in item.value)
            return float(re.search(r'`([0-9.]+)%`', text)[1])
        baseline = conversion()
        next(s for s in at.slider if s.label == 'Áp suất P (bar):').set_value(200).run()
        higher_pressure = conversion()
        self.assertGreater(higher_pressure, baseline)
        next(s for s in at.slider if s.label == 'Nhiệt độ T (°C):').set_value(550).run()
        self.assertLess(conversion(), higher_pressure)
        self.assertTrue(any('Giữ áp suất' in item.value for item in at.info))
        self.assertTrue(any('Giữ nhiệt độ' in item.value for item in at.info))

    def test_ph_lab_three_environments_on_actual_slider(self):
        at = self.app()
        next(s for s in at.selectbox if s.label == '🎯 Chọn khối lớp:').select('Lớp 8').run()
        next(s for s in at.selectbox if s.label == '📚 Môn học cần hỗ trợ:').select('Khoa học tự nhiên').run()
        at.session_state['lab_data'] = {'type': 'chem_ph', 'log_h': -7.0}
        at.run()
        for value, expected in [(3.0, 'Môi trường axit'), (7.0, 'Trung tính'), (11.0, 'Môi trường bazơ')]:
            next(s for s in at.slider if s.label == 'Giá trị pH (thang KNTT 1–14):').set_value(value).run()
            self.assertEqual([e.message for e in at.exception], [])
            self.assertTrue(any(item.value == expected for item in at.success))

    def test_mendel_lab_identifies_phenotypes_and_assumptions(self):
        at = self.app()
        next(s for s in at.selectbox if s.label == '📚 Môn học cần hỗ trợ:').select('Sinh học').run()
        at.session_state['lab_data'] = {'type': 'bio_genetics'}
        at.run()
        self.assertEqual([e.message for e in at.exception], [])
        labels = [item.label for item in at.text_input]
        self.assertIn('Kiểu hình của AA và Aa (trội hoàn toàn):', labels)
        self.assertIn('Kiểu hình của aa:', labels)
        self.assertTrue(any('chỉ khi trội hoàn toàn' in item.value for item in at.info))

    def test_function_labs_render_exact_svg_for_valid_inputs(self):
        at = self.app()
        for payload in [
            {'type': 'func_3', 'a': 1, 'b': 0, 'c': -2, 'd': 1},
            {'type': 'func_1_1', 'a': 1, 'b': 1, 'c': 1, 'd': -1},
            {'type': 'func_2_1', 'a': 1, 'b': -2, 'c': 2, 'd': 1, 'e': -1},
        ]:
            at.session_state['lab_data'] = payload.copy()
            at.run()
            self.assertEqual([e.message for e in at.exception], [])
            self.assertGreaterEqual(sum('<svg' in item.value for item in at.markdown), 2)
            self.assertFalse(any('Điểm cực đại:' in item.value for item in at.caption))
            next(r for r in at.radio if r.label == 'Cách hiển thị đồ thị để đối chiếu:').set_value('Plotly tương tác').run()
            self.assertEqual([e.message for e in at.exception], [])
            self.assertGreaterEqual(len(at.get('plotly_chart')), 1)
            self.assertEqual(at.session_state['lab_data'], payload)

    def test_function_labs_reject_degenerate_data_without_changing_it(self):
        at = self.app()
        cases = [
            ({'type': 'func_3', 'a': 0}, 'a khác 0'),
            ({'type': 'func_1_1', 'a': 1, 'b': 1, 'c': 0, 'd': 1}, 'c khác 0'),
            ({'type': 'func_1_1', 'a': 1, 'b': 1, 'c': 1, 'd': 1}, 'suy biến'),
            ({'type': 'func_2_1', 'a': 0, 'b': 1, 'c': 1, 'd': 1, 'e': -1}, 'a khác 0'),
            ({'type': 'func_2_1', 'a': 1, 'b': 0, 'c': 1, 'd': 0, 'e': -1}, 'd khác 0'),
            ({'type': 'func_2_1', 'a': 1, 'b': 0, 'c': -1, 'd': 1, 'e': -1}, 'suy biến'),
        ]
        for payload, message in cases:
            at.session_state['lab_data'] = payload.copy()
            at.run()
            self.assertEqual([e.message for e in at.exception], [])
            self.assertTrue(any(message in item.value for item in at.error))
            self.assertEqual(at.session_state['lab_data'], payload)

    def test_exp_lab_constant_and_invalid_base_in_actual_app(self):
        at = self.app()
        at.session_state['lab_data'] = {'type': 'func_exp', 'base': 2.0, 'k': 0.0, 'c': 3.0}
        at.run()
        self.assertEqual([e.message for e in at.exception], [])
        self.assertTrue(any('Hằng số' in item.value for item in at.caption))
        next(s for s in at.slider if s.label == 'Cơ số a (a > 0, a ≠ 1):').set_value(1.0).run()
        self.assertEqual([e.message for e in at.exception], [])
        self.assertTrue(any('khác 1' in item.value for item in at.error))

    def test_log_lab_constant_and_invalid_base_in_actual_app(self):
        at = self.app()
        at.session_state['lab_data'] = {'type': 'func_log', 'base': 2.0, 'k': 0.0, 'c': 3.0}
        at.run()
        self.assertEqual([e.message for e in at.exception], [])
        captions = '\n'.join(item.value for item in at.caption)
        self.assertIn('Không có tiệm cận đứng', captions)
        self.assertIn('Hằng số', captions)
        next(s for s in at.slider if s.label == 'Cơ số a (a > 0, a ≠ 1):').set_value(1.0).run()
        self.assertEqual([e.message for e in at.exception], [])
        self.assertTrue(any('khác 1' in item.value for item in at.error))
        self.assertEqual(next(s for s in at.slider if s.label == 'Cơ số a (a > 0, a ≠ 1):').value, 1.0)

    def test_social_lab_rejects_mismatched_graph_without_inventing_lesson(self):
        at = self.app()
        next(s for s in at.selectbox if s.label == "📚 Môn học cần hỗ trợ:").select("Ngữ văn").run()
        at.session_state['lab_data'] = {'type': 'func_3', 'a': 1, 'b': 0, 'c': 0, 'd': 0}
        at.run()
        self.assertEqual([e.message for e in at.exception], [])
        self.assertTrue(any('Chưa có đủ dữ kiện để dựng sơ đồ theo bài học' in item.value for item in at.warning))
        self.assertFalse(any('Chuẩn kiến thức GDPT 2018' in item.value for item in at.markdown))
        self.assertEqual(at.session_state['lab_data']['type'], 'func_3')

    def test_station3_custom_request_does_not_cross_grade_and_restores_own_draft(self):
        at = self.app()
        at.session_state["selected_station"] = "📝 Trạm 3: Luyện Tập & Khảo Thí"
        request = "Chỉ khảo sát hàm số bậc ba lớp 12"
        at.run()
        next(t for t in at.text_area if "Yêu cầu ma trận" in t.label).set_value(request).run()
        original_key = next(t for t in at.text_area if "Yêu cầu ma trận" in t.label).key
        self.assertEqual(at.session_state["custom_matrix_prompt"], request)
        self.assertEqual(next(t for t in at.text_area if "Nhập yêu cầu cấu hình" in t.label).value, request)
        request = "Khảo sát hàm bậc ba lớp12 — chỉnh từ khu giáo viên"
        next(t for t in at.text_area if "Nhập yêu cầu cấu hình" in t.label).set_value(request).run()
        self.assertEqual(next(t for t in at.text_area if "Yêu cầu ma trận" in t.label).value, request)
        at.session_state["custom_request_text"] = request
        at.run()
        next(s for s in at.selectbox if s.label == "🎯 Chọn khối lớp:").select("Lớp 7").run()
        self.assertEqual([e.message for e in at.exception], [])
        self.assertEqual(at.session_state.get("custom_matrix_prompt", ""), "")
        self.assertEqual(next(t for t in at.text_area if "Yêu cầu ma trận" in t.label).value, "")
        self.assertNotEqual(next(t for t in at.text_area if "Yêu cầu ma trận" in t.label).key, original_key)
        self.assertFalse(any("ĐÃ XÁC NHẬN YÊU CẦU TÙY BIẾN" in m.value for m in at.markdown))
        self.assertNotIn("custom_request_text", at.session_state)
        next(s for s in at.selectbox if s.label == "🎯 Chọn khối lớp:").select("Lớp 12").run()
        self.assertEqual([e.message for e in at.exception], [])
        self.assertEqual(at.session_state["custom_matrix_prompt"], request)
        self.assertEqual(next(t for t in at.text_area if "Yêu cầu ma trận" in t.label).value, request)

    def test_station2_empty_session_has_no_fake_mastery(self):
        at = self.app()
        at.session_state["selected_station"] = "✍️ Trạm 2: Gia Sư Socratic & Nộp Bài"
        at.run()
        self.assertEqual([e.message for e in at.exception], [])
        self.assertEqual(at.session_state["tram2_count"], 0)
        self.assertFalse(any("85.4%" in m.value for m in at.markdown))

    def test_generated_lesson_export_is_bound_to_subject_and_grade(self):
        at = self.app()
        at.secrets["GEMINI_API_KEY"] = "test-only-key"
        next(s for s in at.selectbox if s.label == "🎯 Chọn khối lớp:").select("Lớp 6").run()
        next(t for t in at.text_input if "Bài học cần chiếm lĩnh" in t.label).set_value("Phân số")
        lesson = "### PHẦN 1: Phân số\nChỉ có nội dung lớp 6. Phân số $\\frac{1}{2}$."
        with patch("google.genai.Client") as client:
            client.return_value.__enter__.return_value.models.generate_content.return_value = SimpleNamespace(text=lesson, candidates=[])
            next(b for b in at.button if b.label == "🚀 Soạn bài học").click().run()
        self.assertEqual([e.message for e in at.exception], [])
        self.assertEqual(at.session_state["current_lesson_context"], ("Toán học", 6))
        self.assertIn("lớp 6", at.session_state["current_lesson"])
        next(s for s in at.selectbox if s.label == "🎯 Chọn khối lớp:").select("Lớp 7").run()
        self.assertEqual(at.session_state["current_lesson"], "")
        self.assertEqual([e.message for e in at.exception], [])

    def test_stale_unbound_lesson_is_not_exported_as_current_subject(self):
        at = self.app()
        at.session_state["current_lesson"] = "Bài Hóa học lớp 12 từ phiên cũ."
        at.session_state['current_lesson_context'] = ('Hóa học', 12)
        at.session_state['current_topic'] = 'Ester'
        at.run()
        self.assertEqual(at.session_state["current_lesson"], "")
        self.assertIn("Hóa học", at.session_state["orphaned_lesson"])
        self.assertEqual(at.session_state['orphaned_lesson_context'], ('Hóa học', 12))
        self.assertEqual(at.session_state['orphaned_lesson_topic'], 'Ester')
        self.assertTrue(any('tải nguyên văn' in item.value for item in at.warning))
        at.run()
        self.assertIn('Hóa học', at.session_state['orphaned_lesson'])
        at.session_state['current_lesson'] = 'Bài Sinh học lớp 12 thứ hai.'
        at.session_state['current_lesson_context'] = ('Sinh học', 12)
        at.session_state['current_topic'] = 'Mendel'
        at.run()
        previous = list(at.session_state['orphaned_lesson_archive'].values())
        self.assertEqual(len(previous), 1)
        self.assertEqual(previous[0]['text'], 'Bài Hóa học lớp 12 từ phiên cũ.')
        self.assertEqual(previous[0]['context'], ('Hóa học', 12))
        self.assertIn('Sinh học', at.session_state['orphaned_lesson'])
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

    def test_grade8_practice_sections_keep_controls_without_graduation_claims(self):
        at = self.app()
        next(s for s in at.selectbox if s.label == "🎯 Chọn khối lớp:").select("Lớp 8").run()
        at.session_state["selected_station"] = "📝 Trạm 3: Luyện Tập & Khảo Thí"
        at.session_state["exam_state"] = "testing"
        at.session_state["exam_data"] = {"code": "QALABEL", "p1": [],
            "p2": [{"q": "Kiểm tra các mệnh đề số học", "stmts": [
                {"t": str(i) + " là số dương", "a": True} for i in range(1, 5)]}],
            "p3": [{"q": "Tính 2 + 2", "ans": "4"}]}
        at.session_state["exam_context"] = {"name": "QA", "grade": "Lớp 8", "subject": "Toán học", "student_id": "qa-label"}
        at.session_state["exam_deadline"] = time.time() + 300
        at.session_state["attempt_id"] = "qa-label"
        at.run(timeout=90)
        self.assertEqual([e.message for e in at.exception], [])
        sections = [m.value for m in at.markdown if m.value.startswith("### PHẦN")]
        self.assertTrue(any("Thang điểm luyện tập" in v for v in sections))
        self.assertFalse(any("theo Bộ" in v or "4 ký tự" in v for v in sections))
        fields = [t for t in at.text_input if t.label == "Nhập đáp số câu 1:"]
        self.assertEqual(len(fields), 1)
        self.assertNotIn("Quy chế thi tốt nghiệp", fields[0].help or "")
        self.assertEqual(len([r for r in at.radio if r.label.startswith("Chọn Đúng/Sai")]), 4)

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
                                    SimpleNamespace(text=json.dumps({"replacement_question": replacement}), candidates=[])]
            next(b for b in at.button if b.label == "🚀 Khởi Tạo Đề Mới (AI Sáng Tạo 2026)").click().run()
        self.assertEqual([e.message for e in at.exception], [])
        self.assertEqual(at.session_state["exam_state"], "testing")
        self.assertEqual(at.session_state["exam_data"]["p1"][0]["q"], replacement["q"])
        self.assertIn("f", at.session_state["exam_data"]["p1"][0])
        self.assertEqual(at.session_state["exam_data"]["context_recovery"]["events"][0]["action"], "ai_replacement")
        self.assertFalse(at.session_state["exam_data"]["cognitive_audit"]["verified"])
        self.assertTrue(any("Đối soát nhãn mức độ" in expander.label for expander in at.expander))

    def test_english_practice_duration_and_score_do_not_certify_cefr(self):
        at = self.app()
        next(s for s in at.selectbox if s.label == "🎯 Chọn khối lớp:").select("Lớp 7").run()
        next(s for s in at.selectbox if s.label == "📚 Môn học cần hỗ trợ:").select("Tiếng Anh").run()
        at.session_state["selected_station"] = "📝 Trạm 3: Luyện Tập & Khảo Thí"
        at.session_state["exam_state"] = "testing"
        at.session_state["exam_data"] = {"code": "QA18", "p1": [{
            "q": "My brother enjoys ___ models.",
            "opt": ["A. make", "B. making", "C. makes", "D. to making"],
            "ans": "B", "hint": "Sau enjoy, em cần dạng động từ nào?",
            "explain": "Enjoy is followed by a gerund."}], "p2": [], "p3": []}
        at.session_state["exam_context"] = {"name": "QA UI", "grade": "Lớp 7", "subject": "Tiếng Anh", "student_id": "qa-ui"}
        at.session_state["exam_time_mins"] = 45
        at.session_state["exam_start_timestamp"] = time.time()
        at.session_state["exam_deadline"] = time.time() + 45 * 60
        at.session_state["attempt_id"] = "qa-english-practice-cefr"
        at.run()
        self.assertEqual([e.message for e in at.exception], [])
        heading = next(m.value for m in at.markdown if "CÂU HỎI TRẮC NGHIỆM TIẾNG ANH" in m.value)
        self.assertIn("45 phút", heading)
        self.assertNotIn("50 phút", heading)
        next(r for r in at.radio if r.label == "Lựa chọn câu 1:").set_value("B. making").run()
        next(b for b in at.button if b.label == "🏁 Nộp bài & Chấm điểm tức thì").click().run()
        self.assertEqual([e.message for e in at.exception], [])
        self.assertEqual(next(m for m in at.metric if m.label == "Tổng Điểm Khảo Thí").value, "10.00 / 10.0 đ")
        self.assertEqual(next(m for m in at.metric if m.label == "Tỉ Lệ Chính Xác").value, "100.0%")
        self.assertEqual(next(m for m in at.metric if m.label == "Khung Năng Lực CEFR").value, "Chưa đánh giá")
        self.assertFalse(any("Bậc 6" in str(m.delta) or "điểm chuẩn" in str(m.delta) for m in at.metric))

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


if __name__ == "__main__":
    unittest.main()
