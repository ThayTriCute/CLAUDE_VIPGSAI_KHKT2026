"""Cloud giữ module services cũ sau khi app.py cập nhật (sự cố 09/11/2026: ImportError
normalize_bbt_discontinuity ở Trạm 1). CI luôn nạp module mới nên phải mô phỏng worker cũ."""
import ast
import re
import unittest
from pathlib import Path
from unittest.mock import patch

from services import bbt_display_contract, lesson_export

APP = Path(__file__).resolve().parents[1] / 'app.py'


def _app_functions(*names):
    tree = ast.parse(APP.read_text(encoding='utf-8'))
    scope = {'re': re}
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name in names:
            exec(compile(ast.Module(body=[node], type_ignores=[]), 'app-stale', 'exec'), scope)
    return scope


class StaleContractModuleTests(unittest.TestCase):
    def _make_stale(self):
        del bbt_display_contract.normalize_bbt_discontinuity
        del bbt_display_contract.is_bbt_markdown

    def tearDown(self):
        if not hasattr(bbt_display_contract, 'normalize_bbt_discontinuity'):
            from importlib import reload
            reload(bbt_display_contract)

    def test_app_normalizer_reloads_stale_contract_instead_of_import_error(self):
        normalize = _app_functions('_normalize_bbt_discontinuity')['_normalize_bbt_discontinuity']
        self._make_stale()
        self.assertEqual(normalize('| $y\'$ | $\\|\\|$ |'), "| $y'$ | $||$ |")
        self.assertTrue(hasattr(bbt_display_contract, 'normalize_bbt_discontinuity'))

    def test_export_reloads_stale_contract(self):
        self._make_stale()
        out = lesson_export.lesson_body_html("| $x$ | $-\\infty$ | $-1$ | $+\\infty$ |\n|---|---|---|---|\n"
                                            "| $y'$ | $+$ | $\\|\\|$ | $+$ |\n| $y$ | $2$ | $+\\infty \\|\\| -\\infty$ | $2$ |")
        self.assertIn('data-tex="||"', out)

    def test_precision_engine_reloads_stale_contract(self):
        try:
            import precision_visual_engine as pve
        except Exception as error:  # heavy optional deps in minimal envs
            self.skipTest(str(error))
        self._make_stale()
        pve.heal_bbt_mathematics("x | -inf | -1 | +inf\ny' | + | \\|\\| | +\ny | 2 | +inf \\|\\| -inf | 2")
        self.assertTrue(hasattr(bbt_display_contract, 'normalize_bbt_discontinuity'))

    def test_refresh_reloads_contract_before_its_dependants(self):
        refresh = _app_functions('_refresh_t1_context_services')['_refresh_t1_context_services']
        with patch.object(bbt_display_contract, 'T1_CONTEXT_REVISION', 0), patch.object(lesson_export, 'T1_CONTEXT_REVISION', 0):
            with patch('importlib.reload', wraps=__import__('importlib').reload) as reload_call:
                refresh()
                self.assertEqual([c.args[0] for c in reload_call.call_args_list], [bbt_display_contract, lesson_export])
        self.assertEqual(bbt_display_contract.T1_CONTEXT_REVISION, 2026110911)
        self.assertEqual(lesson_export.T1_CONTEXT_REVISION, 2026110911)


if __name__ == '__main__':
    unittest.main()
