"""Bank provenance across contexts and independently checked authored examples."""
import copy
import json
import re
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import real_exam_engine as engine
from services.academic_context import subjects_for_grade


class TestBankProvenance(unittest.TestCase):
    def question(self):
        return {'q': 'Giá trị của biểu thức hai cộng một bằng bao nhiêu?', 'topic': 'Hàm số',
                'opt': ['A. 1', 'B. 2', 'C. 3', 'D. 4'], 'ans': 'C'}

    def test_ai_ingestion_retains_generated_origin_without_mutating_input(self):
        source = {'code': 'QA-ORIGIN', 'school': 'Unverified model claim', 'p1': [self.question()]}
        before = copy.deepcopy(source)
        with tempfile.TemporaryDirectory() as directory, patch.object(engine, 'BASE_DIR', directory), patch.object(engine, '_SHARD_CACHE', {}):
            self.assertTrue(engine.ingest_ai_generated_exam_to_bank(source, 'Toán học', 12))
            saved = json.loads(next((Path(directory)/'data'/'exam_cache').glob('*.json')).read_text(encoding='utf-8'))['data']
        self.assertEqual(source, before)
        self.assertTrue(saved['is_ai_generated'])
        self.assertFalse(saved['is_real_bank_question'])
        self.assertFalse(saved['is_real_exam'])
        self.assertNotIn('Unverified model claim', saved['school'])
        self.assertTrue(saved['p1'][0]['is_ai_generated'])
        self.assertFalse(saved['p1'][0]['is_real_bank_question'])

    def test_old_ai_cache_is_not_promoted_to_real_exam(self):
        with tempfile.TemporaryDirectory() as directory:
            cache = Path(directory)/'data'/'exam_cache'; cache.mkdir(parents=True)
            (cache/'old.json').write_text(json.dumps({'subject': 'Toán học', 'grade': 12,
                'data': {'code': 'OLD-AI', 'is_real_exam': True, 'p1': [self.question()]}}), encoding='utf-8')
            with patch.object(engine, 'BASE_DIR', directory), patch.object(engine, 'TEACHER_EXAMS_FILE', str(Path(directory)/'none.json')), \
                 patch.object(engine, '_FAST_EXAM_LIST_CACHE', {}, create=True), \
                 patch.object(engine, 'get_shard_exams', return_value=[]), patch.object(engine, 'load_teacher_uploaded_exams', return_value=[]):
                exam = engine.get_baseline_full_exams('Toán học', 12)[0]
        self.assertTrue(exam['is_ai_harvested'])
        self.assertTrue(exam['is_ai_generated'])
        self.assertFalse(exam['is_real_exam'])

    def test_pool_keeps_ai_origin_for_all_65_contexts(self):
        with patch.object(engine, '_QUESTIONS_POOL_CACHE', {}):
            for grade in range(6, 13):
                for subject in subjects_for_grade(grade):
                    with self.subTest(subject=subject, grade=grade):
                        exam = {'subject': subject, 'grade': grade, 'is_ai_harvested': True,
                                'is_real_exam': True, 'p1': [self.question()]}
                        before = copy.deepcopy(exam)
                        with patch.object(engine, 'get_baseline_full_exams', return_value=[exam]):
                            question = engine.get_baseline_questions_pool(subject, grade)['p1'][0]
                        self.assertEqual(exam, before)
                        self.assertEqual((question['subject'], question['grade']), (subject, grade))
                        self.assertTrue(question['is_ai_generated'])
                        self.assertFalse(question['is_real_bank_question'])
                        self.assertIn('AI', question['source'])

    def test_mixed_bank_does_not_claim_whole_real_exam(self):
        question = dict(self.question(), subject='Toán học', grade=12,
                        is_ai_generated=True, is_ai_harvested=True, is_real_bank_question=False)
        with patch.object(engine, 'get_baseline_questions_pool', return_value={'p1': [question], 'p2': [], 'p3': []}):
            exam = engine.generate_blended_real_exam('Toán học', 12, ['Hàm số'], (1, 0, 0))
        self.assertFalse(exam['is_real_exam'])
        self.assertEqual(exam['exam_source_type'], 'mixed_bank')
        self.assertTrue(exam['p1'][0]['is_ai_generated'])

    def test_math_examples_do_not_leak_to_other_contexts_or_claim_school_origin(self):
        names = ('p2_f_prime_graph', 'p2_mslgn_quartiles', 'p1_rational_2_1',
                 'p1_mslgn_hologram', 'p1_rational_1_1', 'p1_cubic', 'p1_bbt_rational')
        for grade in range(6, 13):
            for subject in subjects_for_grade(grade):
                if (subject, grade) != ('Toán học', 12):
                    self.assertIsNone(engine.build_specialized_custom_question(names[0], subject, grade))
        for name in names:
            q = engine.build_specialized_custom_question(name)
            self.assertTrue(q['is_synthetic_template'])
            self.assertFalse(q['is_real_bank_question'])
            self.assertNotIn('school', q)
            self.assertNotIn('TOANMATH', q['source'])
        table = engine.build_specialized_custom_question('p1_bbt_rational')['bbt']
        self.assertEqual(len(table.splitlines()), 3)
        self.assertIn(r'\nearrow', table)

    def test_derivative_graph_keys_follow_independent_sign_and_integral_checks(self):
        import sympy as sp
        q = engine.build_specialized_custom_question('p2_f_prime_graph'); x = sp.Symbol('x', real=True)
        m = q['f']; derivative = m['a']*x**3 + m['b']*x**2 + m['c']*x + m['d']
        roots = sp.solve(derivative, x)
        primitive = sp.integrate(derivative, x)
        expected = [bool(derivative.subs(x, 2) > 0), len(roots) == 3,
                    bool(derivative.subs(x, 0) > 0 and derivative.subs(x, 2) < 0),
                    bool(primitive.subs(x, 1) <= min(primitive.subs(x, -1), primitive.subs(x, 4)))]
        self.assertEqual([statement['a'] for statement in q['stmts']], expected)

    def test_rational_example_extremum_and_unique_option_are_computed(self):
        import sympy as sp
        from services.neuro_symbolic_verifier import clean_latex_math_to_sympy_expr
        q = engine.build_specialized_custom_question('p1_rational_2_1')
        model = q['f']; x = sp.Symbol('x', real=True)
        expression = (model['a']*x*x+model['b']*x+model['c'])/(model['d']*x+model['e'])
        right = [v for v in sp.solve(sp.diff(expression, x), x) if v > 1][0]
        self.assertGreater(sp.diff(expression, x, 2).subs(x, right), 0)
        point = re.search(r'cực tiểu \((\d+); (\d+)\)', q['explain'])
        self.assertEqual((float(point[1]), float(point[2])), (float(right), float(expression.subs(x, right))))
        matching = [chr(65+i) for i, option in enumerate(q['opt'])
                    if sp.simplify(clean_latex_math_to_sympy_expr(option.split('$')[1])-expression) == 0]
        self.assertEqual(matching, [q['ans']])
