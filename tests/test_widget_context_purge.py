# -*- coding: utf-8 -*-
import unittest

from services.widget_state import purge_context_bound_widget_keys, switch_exam_request_context


class WidgetContextPurgeTests(unittest.TestCase):
    def test_purge_drops_topic_checkboxes(self):
        state = {
            "cb_t3_12_0": True,
            "cb_t3_11_0": False,
            "kntt_lesson_sel": "cũ",
            "topic_input_main": "bài cũ",
            "student_name": "An",
            "area_custom_prompt_main_Lớp 10_Toán học": "cũ",
            "$$ID-dead-kntt_lesson_sel_Lớp 12_Toán học": "keep",
        }
        n = purge_context_bound_widget_keys(state, previous="Lớp 10_Toán học")
        self.assertGreaterEqual(n, 4)
        self.assertNotIn("cb_t3_12_0", state)
        self.assertNotIn("kntt_lesson_sel", state)
        self.assertNotIn("area_custom_prompt_main_Lớp 10_Toán học", state)
        self.assertIn("$$ID-dead-kntt_lesson_sel_Lớp 12_Toán học", state)
        self.assertEqual(state["student_name"], "An")

    def test_switch_keeps_drafts_and_purges_cb(self):
        state = {
            "custom_matrix_prompt": "yêu cầu A",
            "cb_t3_12_0": True,
            "exam_request_drafts": {},
        }
        switch_exam_request_context(state, "Lớp 12_Vật lý", "Lớp 11_Hóa học")
        self.assertNotIn("cb_t3_12_0", state)
        self.assertNotIn("custom_matrix_prompt", state)
        self.assertEqual(state["exam_request_drafts"]["Lớp 12_Vật lý"]["custom_matrix_prompt"], "yêu cầu A")


if __name__ == "__main__":
    unittest.main()
