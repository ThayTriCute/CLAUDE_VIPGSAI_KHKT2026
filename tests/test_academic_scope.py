import copy
import unittest

from services.academic_scope import (AcademicScopeError, check_requested_scope, check_lesson_scope,
                                     check_exam_question_scope, academic_scope_instruction)
from services.context_recovery import repair_exam_context
from services.curriculum_policy import prepare_exam_for_delivery
from services.math_publication import generate_checked_text
from tests.lesson_samples import complete_lesson


class TestAcademicScope(unittest.TestCase):
    cubic = 'Khảo sát hàm bậc ba'

    def test_cubic_request_cannot_survey_quartic_function(self):
        for formula in ('$y=x^4-2x^2+1$', '$f(x)=ax^{4}+bx^{2}+c$', 'y=x⁴-2x²+1'):
            with self.subTest(formula=formula), self.assertRaises(AcademicScopeError):
                check_requested_scope(formula, 'Toán', 12, [self.cubic])

    def test_basic_survey_scope_uses_same_boundary(self):
        with self.assertRaises(AcademicScopeError):
            check_requested_scope('$y=x^4-2x^2+1$', 'Toán', 12, ['Ứng dụng đạo hàm khảo sát và vẽ đồ thị'])

    def test_integral_and_primitive_are_not_globally_banned(self):
        check_requested_scope('$y=x^4$', 'Toán', 12, ['Nguyên hàm và tích phân'])
        check_requested_scope('$F(x)=x^4/4+C$', 'Toán', 12, [self.cubic])

    def test_cubic_derivative_and_canceling_terms_are_not_false_positives(self):
        for formula in ("$y=x^3-3x+1$", "$f'(x)=3x^2-3$", "$y=x^4-x^4+x^3$"):
            check_requested_scope(formula, 'Toán', 12, [self.cubic])

    def test_scope_does_not_migrate_between_subjects(self):
        for subject in ('Vật lý', 'Tiếng Anh', 'Địa lý'):
            check_requested_scope('$y=x^4$', subject, 12, [self.cubic])

    def test_quartic_distractor_is_not_the_function_under_survey(self):
        lesson = complete_lesson().replace('A. 1\n', 'A. $y=x^4$\n', 1)
        self.assertEqual(check_lesson_scope(lesson, 'Toán', 12, self.cubic), lesson)

    def test_lesson_scope_repair_is_bounded_and_precedes_publication(self):
        bad = complete_lesson('Khảo sát $y=x^4-2x^2+1$.')
        good = complete_lesson('Khảo sát $y=x^3-3x+1$.')
        calls = []
        def generate(prompt):
            calls.append(prompt)
            return bad if len(calls) == 1 else good
        result = generate_checked_text('Toán 12, ' + self.cubic, generate,
                                       lambda text: check_lesson_scope(text, 'Toán', 12, self.cubic))
        self.assertEqual(result, good)
        self.assertEqual(len(calls), 2)

    def test_mixed_exam_uses_each_matched_topic(self):
        topics = [self.cubic, 'Nguyên hàm và tích phân']
        check_exam_question_scope({'q': '$y=x^4$', 'topic': topics[1]}, 'Toán', 12, topics)
        with self.assertRaises(AcademicScopeError):
            check_exam_question_scope({'q': '$y=x^4$', 'topic': topics[0]}, 'Toán', 12, topics)

    def test_whole_question_replacement_preserves_input_and_answer_alignment(self):
        question = {'subject': 'Toán học', 'grade': 12, 'topic': self.cubic,
                    'q': 'Khảo sát $y=x^4-2x^2+1$.', 'opt': ['A. -3', 'B. 0', 'C. 1', 'D. 3'], 'ans': 'A'}
        replacement = {**question, 'q': "Cho $y=x^3-3x+1$. Tính $y'(0)$."}
        exam = {'p1': [question], 'p2': [], 'p3': []}
        before = copy.deepcopy(exam)
        check = lambda item: check_exam_question_scope(item, 'Toán', 12, [self.cubic])
        result = repair_exam_context(exam, 'Toán', 12, [self.cubic], scope_validator=check,
                                     ai_generator=lambda prompt: {'replacement_question': replacement})
        self.assertEqual(exam, before)
        self.assertEqual(result['p1'][0]['q'], replacement['q'])
        self.assertEqual(result['p1'][0]['opt'], replacement['opt'])
        self.assertEqual(result['p1'][0]['ans'], replacement['ans'])
        self.assertEqual(result['context_recovery']['ai_calls'], 1)
        self.assertEqual(result['context_recovery']['unresolved'], 0)

    def test_final_publication_still_checks_scope_without_recovery(self):
        exam = {'p1': [{'q': '$y=x^4-2x^2+1$', 'opt': ['A. 1', 'B. 2', 'C. 3', 'D. 4'], 'ans': 'A'}]}
        with self.assertRaises(AcademicScopeError):
            prepare_exam_for_delivery(exam, 'Toán', 12, topics=[self.cubic])

    def test_sourced_instruction_is_not_inserted_into_other_subjects(self):
        self.assertIn('trang 106', academic_scope_instruction('Toán', 12, self.cubic))
        self.assertEqual(academic_scope_instruction('Vật lý', 12, self.cubic), '')
        self.assertEqual(academic_scope_instruction('Toán', 6, self.cubic), '')
