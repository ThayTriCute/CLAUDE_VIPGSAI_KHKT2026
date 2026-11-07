import ast
from pathlib import Path
import random
import os
import sqlite3
import tempfile
from contextlib import closing
from unittest.mock import patch
from concurrent.futures import ThreadPoolExecutor
from types import SimpleNamespace
import unittest


class PhilosophyRotationTests(unittest.TestCase):
    def test_closure_history_survives_lesson_change_without_student_content(self):
        tree = ast.parse(Path('app.py').read_text(encoding='utf-8'))
        fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef)
                  and n.name == 'register_station_closure')
        class State(dict):
            __getattr__ = dict.__getitem__
            __setattr__ = dict.__setitem__
        state = State(current_topic='Bài Toán', subject='Toán học')
        env = {'st': SimpleNamespace(session_state=state)}
        exec(compile(ast.Module(body=[fn], type_ignores=[]), 'actual-register', 'exec'), env)
        quote = {'quote': 'Câu đã kiểm', 'author': 'Tác giả', 'lesson': 'Giữ lời hứa', 'student': 'PRIVATE'}
        env[fn.name](1, quote)
        state.update(current_topic='Bài Văn', subject='Ngữ văn')
        env[fn.name](1, quote)
        self.assertEqual(len(state['philosophical_teaching_history']), 1)
        self.assertNotIn('student', state['philosophical_teaching_history'][0])
        self.assertIn('Câu đã kiểm', state['used_philosophical_quotes'])

    def test_shared_rotation_survives_new_session_and_uses_only_verified_sources(self):
        tree = ast.parse(Path('app.py').read_text(encoding='utf-8'))
        bank = next(n for n in tree.body if isinstance(n, ast.Assign)
                    and any(isinstance(t, ast.Name) and t.id == 'CROSS_STATION_PHILOSOPHY_BANK' for t in n.targets))
        fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef)
                  and n.name == 'get_unique_philosophical_lesson')
        used = []
        env = {'st': SimpleNamespace(session_state={'used_philosophical_quotes': used}), 'random': random}
        exec(compile(ast.Module(body=[bank, fn], type_ignores=[]), 'actual-controller', 'exec'), env)
        with tempfile.TemporaryDirectory() as folder, patch.dict(os.environ,
                GSAI_PHILOSOPHY_LEDGER_PATH=str(Path(folder)/'rotation.sqlite3')):
            results=[]
            for i in range(12):
                # New app session does not reset the public runtime ledger.
                env['st']=SimpleNamespace(session_state={})
                result=env[fn.name](i % 3+1, 'Ngữ văn' if i % 2 else 'Toán học', 'PRIVATE_CONTEXT')
                self.assertTrue(result['source_verified'])
                self.assertTrue(result['source_locator'])
                self.assertNotIn(result['angle'],[r['angle'] for r in results[-8:]])
                results.append(result)
            self.assertEqual(len({r['plan_id'] for r in results}),12)
            self.assertEqual({r['era'] for r in results},{'ancient','modern'})
            self.assertTrue(any('Tagore' in r['author'] for r in results))
            self.assertTrue(any('Mill' in r['author'] for r in results))
            with closing(sqlite3.connect(results[0]['ledger_path'])) as db:
                self.assertNotIn('PRIVATE_CONTEXT',str(db.execute('SELECT * FROM plans').fetchall()))
                self.assertEqual(db.execute('SELECT SUM(delivered) FROM plans').fetchone()[0],0)

    def test_concurrent_reservations_and_delivery_are_distinct(self):
        from services.philosophy_rotation import reserve_plan, mark_delivered, closure_instruction
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'rotation.sqlite3'
            with ThreadPoolExecutor(max_workers=4) as pool:
                plans=list(pool.map(lambda station: reserve_plan({},station,ledger_path=path),[1,2,3,1,2,3]))
            self.assertEqual(len({p['plan_id'] for p in plans}),6)
            mark_delivered(plans[0]);mark_delivered(plans[0])
            with closing(sqlite3.connect(path)) as db:
                self.assertEqual(db.execute('SELECT SUM(delivered) FROM plans').fetchone()[0],1)
            prompt=closure_instruction(plans[0],1,'Bài học dữ liệu')
            self.assertIn('Bài học dữ liệu',prompt)
            self.assertNotIn(str(path),prompt)

    def test_existing_public_session_history_is_not_lost_on_new_ledger(self):
        from services.philosophy_rotation import reserve_plan
        bank={1:[dict(author='A',origin='Phương Đông',quote='Seen',lesson='Old',
                      source_verified=True,source_url='https://example.com/a',source_locator='1'),
                 dict(author='B',origin='Phương Đông',quote='Fresh',lesson='New',
                      source_verified=True,source_url='https://example.com/b',source_locator='2')]}
        with tempfile.TemporaryDirectory() as folder:
            plan=reserve_plan(bank,1,ledger_path=Path(folder)/'new.sqlite3',
                              prior=[dict(author='A',quote='Seen')])
            self.assertEqual(plan['quote'],'Fresh')

    def test_all_stations_pass_plan_before_api_and_record_after_response(self):
        source=Path('app.py').read_text(encoding='utf-8')
        for station,var in [(1,'t1'),(2,'t2'),(3,'t3')]:
            self.assertIn(f'closure_instruction({var}_quote_data, {station},',source)
        for station,content in [(2,'clean_rep'),(3,'t3_rep')]:
            pos=source.index(f'register_station_closure({station},')
            self.assertGreater(pos,source.rfind('"role": "assistant", "content": '+content,0,pos))
