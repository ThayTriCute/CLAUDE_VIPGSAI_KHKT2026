"""Reproduce Cloud retaining an older imported HTML builder after app update."""
import ast
import re
import unittest
from pathlib import Path


class Station1ExportReloadTests(unittest.TestCase):
    topic = 'Hàm 2/1 y=(x^2-2x+2)/(x-1).'
    old_page = '<html><style>.paper{color:black}</style><body class="monochrome"><article id="lesson"><p>KEEP SOURCE</p><table><tr><td>x</td></tr><tr><td>y′</td></tr><tr><td>y</td></tr></table></article></body></html>'

    def namespace(self):
        tree = ast.parse((Path(__file__).resolve().parents[1] / 'app.py').read_text(encoding='utf-8'))
        scope = {'re': re}
        for node in tree.body:
            if isinstance(node, ast.FunctionDef) and node.name == '_sync_t1_function_export':
                exec(compile(ast.Module(body=[node], type_ignores=[]), 'app-export-helper', 'exec'), scope)
        return tree, scope

    def test_actual_app_export_assignments_repair_a_cached_old_builder(self):
        tree, scope = self.namespace()
        scope.update(build_lesson_html=lambda *args: self.old_page, subject='Toán học', grade_num=12,
                     current_topic_name=self.topic, cleaned_p1='KEEP SOURCE', export_style='monochrome')
        assignments = [node for node in ast.walk(tree) if isinstance(node, ast.Assign) and
                       any(isinstance(target, ast.Name) and target.id == 'export_html' for target in node.targets)]
        for node in sorted(assignments, key=lambda item: item.lineno):
            exec(compile(ast.Module(body=[node], type_ignores=[]), 'actual-app-export', 'exec'), scope)
        self.assertEqual(scope['export_html'].count('<section class="verified-function-visuals"'), 1)
        self.assertIn('aria-label="Đồ thị y=', scope['export_html'])
        self.assertIn('KEEP SOURCE', scope['export_html'])

    def test_repair_is_idempotent_and_preserves_monochrome(self):
        _, scope = self.namespace()
        repair = scope['_sync_t1_function_export']
        first = repair(self.old_page, 'Toán học', self.topic, 'KEEP SOURCE')
        self.assertEqual(repair(first, 'Toán học', self.topic, 'KEEP SOURCE'), first)
        self.assertIn('.monochrome .verified-function-visuals polyline{stroke:#111}', first)

    def test_other_subjects_and_ambiguous_functions_are_unchanged(self):
        _, scope = self.namespace()
        repair = scope['_sync_t1_function_export']
        self.assertEqual(repair(self.old_page, 'Tin học', self.topic, 'KEEP SOURCE'), self.old_page)
        self.assertEqual(repair(self.old_page, 'Toán học', 'Nhiều hàm', ''), self.old_page)
        self.assertEqual(repair('<p>Missing article</p>', 'Toán học', self.topic, ''), '<p>Missing article</p>')


if __name__ == '__main__':
    unittest.main()
