import ast
from pathlib import Path
import unittest

from services.academic_context import subjects_for_grade
from services.curriculum_policy import lesson_generation_request, exam_generation_request
from services.text_boundaries import TEACHING_STEP_LAYOUT_GUIDANCE, with_teaching_step_layout


class StepGenerationContractTests(unittest.TestCase):
    def test_rule_is_attached_once_for_all_supported_generation_contexts(self):
        checked = 0
        for grade in range(6, 13):
            for subject in subjects_for_grade(grade):
                for system, user in (
                        lesson_generation_request(subject, grade, 'Chủ đề dữ liệu'),
                        exam_generation_request(subject, grade, ['Chủ đề dữ liệu'], (3, 1, 1), 'QA')):
                    prepared = with_teaching_step_layout(system)
                    self.assertEqual(prepared.count(TEACHING_STEP_LAYOUT_GUIDANCE), 1)
                    self.assertEqual(with_teaching_step_layout(prepared), prepared)
                    self.assertIn('\\n\\n', prepared)
                    self.assertNotIn('Chủ đề dữ liệu', prepared)
                    self.assertIn('Chủ đề dữ liệu', user)
                    checked += 1
        self.assertEqual(checked, 130)

    def test_both_real_transports_attach_before_fallback_loops(self):
        tree = ast.parse(Path('app.py').read_text(encoding='utf-8'))
        for name in ('call_gemini_with_fallback', 'stream_gemini_with_fallback'):
            node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name)
            assignments = [n for n in ast.walk(node) if isinstance(n, ast.Assign)
                           and isinstance(n.value, ast.Call)
                           and isinstance(n.value.func, ast.Name)
                           and n.value.func.id == 'with_teaching_step_layout']
            self.assertEqual(len(assignments), 1, name)
            self.assertEqual(assignments[0].targets[0].id, 'effective_si')
            self.assertLess(assignments[0].lineno, min(n.lineno for n in ast.walk(node) if isinstance(n, ast.For)))
            configs = [n for n in ast.walk(node) if isinstance(n, ast.Call)
                       and isinstance(n.func, ast.Attribute) and n.func.attr == 'GenerateContentConfig']
            self.assertTrue(configs)
            for config in configs:
                self.assertTrue(any(k.arg == 'system_instruction'
                                    and isinstance(k.value, ast.Name) and k.value.id == 'effective_si'
                                    for k in config.keywords))

    def test_json_mode_keeps_schema_instruction_and_does_not_change_user_data(self):
        instruction = 'Return ONLY valid JSON with the existing schema.'
        prepared = with_teaching_step_layout(instruction)
        self.assertTrue(prepared.startswith(instruction))
        self.assertIn('bên trong giá trị chuỗi', prepared)
        self.assertIn('không chèn Markdown hoặc văn bản bên ngoài JSON', prepared)
