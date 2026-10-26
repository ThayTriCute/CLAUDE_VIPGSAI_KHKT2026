import copy
import json
import unittest

from services.context_recovery import repair_exam_context
from services.curriculum_policy import exam_prompt
from services.monotonicity_check import audit_monotonic_options
from services.neuro_symbolic_verifier import audit_ai_generated_question_sympy
from services.web_question_contract import replacement_schema


class TestStation3GenerationContract(unittest.TestCase):
    def question(self):
        return {'q': 'Hàm số đã cho đồng biến trên khoảng nào dưới đây?',
                'f': {'type': 'func_3', 'a': 1, 'b': 0, 'c': -3, 'd': 1},
                'opt': ['A. $(-1;1)$', 'B. $(1;3)$', 'C. $(-\\infty;-1)$', 'D. $(-1;3)$'], 'ans': 'C'}

    def test_subinterval_is_also_correct_and_two_answers_are_rejected(self):
        q = self.question(); before = copy.deepcopy(q)
        report = audit_ai_generated_question_sympy(q)
        self.assertTrue(report['hallucination_detected'])
        self.assertEqual(report['valid_options'], ['B', 'C'])
        self.assertEqual(q, before)

    def test_single_valid_answer_and_wrong_key(self):
        q = self.question(); q['opt'][1] = 'B. $(-2;0)$'
        self.assertTrue(audit_monotonic_options(q)['verified'])
        q['ans'] = 'A'
        self.assertTrue(audit_monotonic_options(q)['hallucination_detected'])

    def test_stationary_point_does_not_break_strict_monotonicity(self):
        q = self.question(); q['f']['c'] = 0
        # x^3 increases on every open interval, not only the full real line.
        self.assertEqual(audit_monotonic_options(q)['valid_options'], list('ABCD'))

    def test_formula_and_model_conflict_is_rejected_without_rewriting_either(self):
        q = self.question(); q['q'] = 'Cho $y=x^3$. Hàm số đồng biến trên khoảng nào?'
        self.assertTrue(audit_monotonic_options(q)['hallucination_detected'])

    def test_derivative_graph_task_is_not_misread_as_graph_of_function(self):
        q = self.question(); q['q'] = "Cho đồ thị đạo hàm $y=f'(x)$. Hàm số đồng biến trên khoảng nào?"
        self.assertEqual(audit_monotonic_options(q), {'verified': False, 'hallucination_detected': False})

    def test_unsupported_options_negations_and_rational_models_are_unverified(self):
        for change in ({'opt': ['A. nhận định', 'B. một', 'C. hai', 'D. ba']},
                       {'q': 'Hàm số không đồng biến trên khoảng nào?'},
                       {'f': {'type': 'func_1_1', 'a': 1, 'b': 1, 'c': 1, 'd': 0}}):
            with self.subTest(change=change):
                self.assertEqual(audit_monotonic_options(dict(self.question(), **change)),
                                 {'verified': False, 'hallucination_detected': False})

    def test_full_schema_has_correct_part_not_a_literal_object_placeholder(self):
        for part in ('p1', 'p2', 'p3'):
            q = replacement_schema(part, 'Tiếng Anh', 6, ['My school'])['replacement_question']
            self.assertEqual((q['subject'], q['grade'], q['topic']), ('Tiếng Anh', 6, 'My school'))
            self.assertEqual(len(q['stmts']) if part == 'p2' else len(q['opt']) if part == 'p1' else 1,
                             4 if part in ('p1', 'p2') else 1)

    def test_generation_and_repair_share_web_representation_contract(self):
        prompt = exam_prompt('Toán', 12, ['Khảo sát hàm số'], (1, 0, 0), '1234')
        self.assertIn('tkzTab', prompt)
        self.assertIn('khoảng con', prompt)
        calls = []
        broken = {'q': 'Cho bảng biến thiên như sau: \\begin{tikzpicture}x\\end{tikzpicture}',
                  'topic': 'Khảo sát hàm số', 'opt': ['A. 1', 'B. 2', 'C. 3', 'D. 4'], 'ans': 'A'}
        repair_exam_context({'p1': [broken]}, 'Toán', 12, ai_generator=lambda p: calls.append(p) or {}, max_ai_questions=1)
        self.assertEqual(len(calls), 1)
        self.assertIn('tkzTab', calls[0])
        self.assertIn('"replacement_question": {', calls[0])
        self.assertNotIn('"replacement_question": "object"', calls[0])

    def test_live_failure_replay_replaces_tikz_and_rejects_nonunique_intervals(self):
        topic = 'Khảo sát hàm số'
        broken = dict(self.question(), subject='Toán học', grade=12, topic=topic, level='NB')
        broken.pop('f')
        broken['q'] = ("Cho hàm số $y=f(x)$ có bảng biến thiên như sau:\n"
                       r'\begin{tikzpicture}\tkzTabInit{$x$/1,$y$/2}{$-\infty$,$-1$,$1$,$+\infty$}\end{tikzpicture}'
                       '\nHàm số đã cho đồng biến trên khoảng nào dưới đây?')
        candidate = dict(self.question(), subject='Toán học', grade=12, topic=topic, level='NB')
        corrected = copy.deepcopy(candidate); corrected['opt'][1] = 'B. $(-2;0)$'
        sequence = iter([candidate, corrected]); prompts = []
        def generate(prompt):
            prompts.append(prompt)
            return {'replacement_question': next(sequence)}
        source = {'p1': [broken]}; original = copy.deepcopy(source)
        result = repair_exam_context(source, 'Toán', 12, [topic], ai_generator=generate)
        self.assertEqual(source, original)
        self.assertEqual(result['context_recovery']['unresolved'], 0)
        self.assertEqual(result['context_recovery']['ai_calls'], 2)
        self.assertEqual(result['context_recovery']['attempts'][0]['reason'], 'independently_detected_answer_mismatch')
        self.assertIn('independently_detected_answer_mismatch', prompts[1])
        self.assertEqual(result['p1'][0]['opt'], corrected['opt'])
        self.assertEqual(result['p1'][0]['ans'], corrected['ans'])


if __name__ == '__main__':
    unittest.main()
