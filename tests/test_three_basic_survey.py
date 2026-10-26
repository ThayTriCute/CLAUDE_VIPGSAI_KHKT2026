import unittest

from services.academic_scope import (AcademicScopeError, academic_scope_instruction,
                                     check_lesson_scope, check_three_basic_survey_coverage)
from services.curriculum_policy import lesson_prompt, exam_prompt
from services.math_publication import generate_checked_text
from tests.lesson_samples import complete_lesson


class ThreeBasicSurveyTests(unittest.TestCase):
    topic = 'Khảo sát hàm số ba hàm cơ bản'
    examples = (r'Ví dụ bậc ba: $y=x^3-3x+1$. '
                r'Ví dụ phân thức 1/1: $y=\frac{2x-1}{x-1}$. '
                r'Ví dụ phân thức 2/1: $y=\dfrac{x^2-2x+2}{x-1}$.')

    def test_incident_listing_three_names_with_one_example_is_incomplete(self):
        theory = ('Ba dạng bậc ba, phân thức 1/1 và 2/1. '
                  r'Ví dụ minh họa: $y=\frac{2x-1}{x-1}$.')
        with self.assertRaisesRegex(AcademicScopeError, 'bậc ba.*phân thức 2/1'):
            check_lesson_scope(complete_lesson(theory), 'Toán', 12, self.topic)

    def test_three_explicit_examples_pass_without_changing_text(self):
        self.assertEqual(check_three_basic_survey_coverage(self.examples, 'Toán học', 12, self.topic), self.examples)

    def test_equivalent_function_notation_is_not_rejected(self):
        for theory in (self.examples.replace('y=', 'y=f(x)='),
                       self.examples.replace('y=', 'f(x)='),
                       self.examples.replace(r'\frac', r'\tfrac').replace('x^3-3x+1', r'\left(x^3-3x+1\right)')):
            with self.subTest(theory=theory):
                self.assertEqual(check_three_basic_survey_coverage(theory, 'Toán', 12, self.topic), theory)

    def test_other_contexts_and_single_form_requests_are_unchanged(self):
        for subject, grade, topic in [('Toán', 6, self.topic), ('Vật lý', 12, self.topic),
                                     ('Toán', 12, 'Khảo sát hàm bậc ba'),
                                     ('Toán', 12, 'Ứng dụng đạo hàm khảo sát hàm số')]:
            with self.subTest(context=(subject, grade, topic)):
                self.assertEqual(check_three_basic_survey_coverage('Bài riêng', subject, grade, topic), 'Bài riêng')

    def test_generic_formulas_and_cancelled_fractions_do_not_fake_coverage(self):
        for extra in (r'$y=ax^3+bx^2+cx+d$', r'$y=\frac{x^2-1}{x-1}$', r'$y=x^4$'):
            with self.subTest(extra=extra), self.assertRaises(AcademicScopeError):
                check_three_basic_survey_coverage(extra, 'Toán', 12, self.topic)

    def test_missing_coverage_reuses_one_repair_then_accepts_complete_draft(self):
        calls = []
        good = complete_lesson(self.examples)
        def generate(prompt):
            calls.append(prompt)
            return complete_lesson(r'$y=x^3-3x+1$.') if len(calls) == 1 else good
        result = generate_checked_text('Bài ba dạng', generate,
            lambda text: check_lesson_scope(text, 'Toán', 12, self.topic))
        self.assertEqual(result, good)
        self.assertEqual(len(calls), 2)
        self.assertIn('PHẦN 1 thiếu ví dụ', calls[1])

    def test_repair_is_bounded_and_keeps_failed_draft_for_private_diagnostics(self):
        calls = []
        def generate(prompt):
            calls.append(prompt)
            return complete_lesson('Chỉ liệt kê tên.')
        with self.assertRaises(AcademicScopeError) as caught:
            generate_checked_text('Bài ba dạng', generate,
                lambda text: check_lesson_scope(text, 'Toán', 12, self.topic))
        self.assertEqual(len(calls), 2)
        self.assertEqual(caught.exception.validation_attempts, 2)
        self.assertIn('Chỉ liệt kê tên', caught.exception.rejected_draft)

    def test_source_context_is_only_added_for_explicit_three_form_request(self):
        prompt = lesson_prompt('Toán', 12, self.topic)
        self.assertIn('truonghocsoquocgia.nxbgd.vn/book/', prompt)
        self.assertIn('CẢ BA DẠNG', prompt)
        self.assertNotIn('CẢ BA DẠNG', lesson_prompt('Toán', 12, 'Khảo sát hàm bậc ba'))
        self.assertNotIn('CẢ BA DẠNG', exam_prompt('Toán', 12, [self.topic], (1, 0, 0), '1234'))


if __name__ == '__main__':
    unittest.main()
