# -*- coding: utf-8 -*-
"""Tùy biến Trạm 3 không được mang sang môn hoặc khối khác."""
from __future__ import annotations

import unittest

from services.academic_context import subjects_for_grade
from services.widget_state import switch_exam_request_context


class Tram3CustomPromptContextTests(unittest.TestCase):
    def test_prompt_stays_with_its_subject_and_grade(self):
        cells = [(grade, subject) for grade in range(6, 13) for subject in subjects_for_grade(grade)]
        self.assertGreaterEqual(len(cells), 60)
        state = {}
        grade, subject = cells[0]
        key = f"{grade}_{subject}"
        marker = f"ONLY {subject} L{grade}"
        state["custom_matrix_prompt"] = marker
        state[f"area_custom_prompt_main_{key}"] = marker
        state[f"cb_t3_12_0"] = True

        for next_grade, next_subject in cells[1:]:
            nxt = f"{next_grade}_{next_subject}"
            switch_exam_request_context(state, key, nxt)
            current = str(state.get("custom_matrix_prompt") or "")
            self.assertNotIn(marker, current, msg=f"{marker} lọt sang {nxt}")
            self.assertNotIn(f"area_custom_prompt_main_{key}", state)
            self.assertNotIn("cb_t3_12_0", state)
            state["custom_matrix_prompt"] = f"ONLY {next_subject} L{next_grade}"
            key = nxt

        switch_exam_request_context(state, key, f"{grade}_{subject}")
        self.assertEqual(state.get("custom_matrix_prompt"), marker)


if __name__ == "__main__":
    unittest.main()
