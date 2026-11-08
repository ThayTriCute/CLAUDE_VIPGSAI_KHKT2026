import ast
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch


class ClosureReplayStateTests(unittest.TestCase):
    def test_both_replay_paths_tolerate_empty_state_and_complete_only_valid_plan(self):
        tree = ast.parse(Path('app.py').read_text(encoding='utf-8'))
        nodes = [n for n in ast.walk(tree) if isinstance(n, ast.If)
                 and isinstance(n.test, ast.BoolOp)
                 and 'closure_plan' in ast.dump(n.test)
                 and 'complete_verified_quote_reference' in ast.dump(n)]
        self.assertEqual(len(nodes), 2)
        for node in nodes:
            for plan in (None, {}, [], '', 0):
                message = {'content': 'Approved original'}
                with patch('services.socratic_context.complete_verified_quote_reference') as complete:
                    exec(compile(ast.Module(body=[node], type_ignores=[]), 'actual-replay', 'exec'),
                         {'closure_plan': plan, 'm': message})
                    complete.assert_not_called()
                self.assertEqual(message['content'], 'Approved original')
            message = {'content': 'Original'}
            plan = {'plan_id': 'verified-plan'}
            with patch('services.socratic_context.complete_verified_quote_reference', return_value='Completed') as complete:
                exec(compile(ast.Module(body=[node], type_ignores=[]), 'actual-replay', 'exec'),
                     {'closure_plan': plan, 'm': message})
                complete.assert_called_once_with('Original', [plan])
                self.assertEqual(message['content'], 'Completed')


if __name__ == '__main__':
    unittest.main()
