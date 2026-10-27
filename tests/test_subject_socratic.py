import unittest

from data.socratic_anchors import sanitize_socratic_hint
from services.academic_context import subjects_for_grade


class TestSubjectSocratic(unittest.TestCase):
    def test_non_math_fallback_does_not_instruct_every_subject_to_solve_equations(self):
        for grade in range(6, 13):
            for subject in subjects_for_grade(grade):
                if subject == 'Toán học':
                    continue
                with self.subTest(subject=subject, grade=grade):
                    hint = sanitize_socratic_hint('', 'B', 'Nhiệm vụ học tập theo ngữ liệu.',
                        ['A. Một', 'B. Hai', 'C. Ba', 'D. Bốn'], subject=subject, grade_num=grade)
                    self.assertNotIn('Thiết lập phương trình', hint)
                    self.assertNotIn('thế số liệu', hint)
                    self.assertTrue(hint.endswith('?'))

    def test_separate_contextual_question_is_preserved(self):
        hint = 'Chi tiết nào trong đoạn trích giúp em nhận diện cảm xúc của người kể?'
        self.assertEqual(sanitize_socratic_hint(hint, 'B', 'Đọc hiểu đoạn trích.',
            ['A. Một', 'B. Hai', 'C. Ba', 'D. Bốn'], subject='Ngữ văn', grade_num=8), hint)

    def test_explicit_answers_are_not_forwarded_as_hints(self):
        for value in ('Chọn B?', 'The answer is B?', 'B là đúng?', 'Đáp án: B?'):
            with self.subTest(value=value):
                self.assertNotEqual(sanitize_socratic_hint(value, 'B', 'Đọc câu hỏi.',
                    ['A. Alpha', 'B. Beta', 'C. Gamma', 'D. Delta'], subject='Anh', grade_num=7), value)

    def test_math_guiding_question_can_reference_given_data_without_solving(self):
        hint = 'Với điều kiện $x > 0$ trong đề, em cần kiểm tra miền xác định trước hay sau khi biến đổi?'
        self.assertEqual(sanitize_socratic_hint(hint, 'B', 'Xét biểu thức theo điều kiện.',
            ['A. Alpha', 'B. Beta', 'C. Gamma', 'D. Delta'], subject='Toán', grade_num=9), hint)
