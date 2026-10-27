"""Keep the existing two matrix inputs synchronized without a second app run."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import database
import streamlit as st
from streamlit.testing.v1 import AppTest


class MatrixInteractionTests(unittest.TestCase):
    def test_confirmation_and_teacher_edits_keep_the_same_request(self):
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as folder:
            isolated = database.DatabaseManager(Path(folder) / 'matrix.db')
            with patch.object(database, 'db_manager', isolated), patch('google.genai.Client') as ai:
                app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / 'app.py'), default_timeout=60)
                app.run()
                next(b for b in app.button if b.key == 'top_nav_station_2').click().run()
                for source, request in [('area_custom_prompt_main', 'Giữ đúng yêu cầu học sinh'),
                                        ('area_custom_prompt_gv', 'Giữ đúng yêu cầu giáo viên'),
                                        ('area_custom_prompt_main', '')]:
                    next(t for t in app.text_area if t.key == source).set_value(request).run()
                    with patch.object(st, 'set_page_config', wraps=st.set_page_config) as runs:
                        next(b for b in app.button if b.key == 'btn_confirm_cp_explicit').click().run()
                    self.assertEqual(runs.call_count, 1)
                    self.assertFalse(app.exception)
                    self.assertEqual(app.session_state['custom_matrix_prompt'], request)
                    for key in ('area_custom_prompt_main', 'area_custom_prompt_gv'):
                        self.assertEqual(next(t for t in app.text_area if t.key == key).value, request)
                self.assertEqual(ai.call_count, 0)


if __name__ == '__main__':
    unittest.main()
