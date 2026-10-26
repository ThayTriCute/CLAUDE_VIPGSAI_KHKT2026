import unittest

from services.academic_context import subjects_for_grade
from services.lesson_contract import (LessonContractError, validate_lesson_contract,
                                     validate_socratic_question)
from tests.lesson_samples import complete_lesson


class SocraticBoundaryTests(unittest.TestCase):
    def test_formula_is_not_a_numeric_answer_prefix(self):
        for formula in ('y=2x+b', 'y=2.5x+b', 'y=2 x+b', r'C=2\pi R'):
            hint = f'Trong biểu thức ${formula}$, em cần đối chiếu những đại lượng nào?'
            with self.subTest(formula=formula):
                self.assertEqual(validate_socratic_question(hint), hint)

    def test_referring_to_options_does_not_give_an_answer(self):
        hint = 'Em có thể kiểm tra các đáp án bằng cách thay vào điều kiện của đề như thế nào?'
        self.assertEqual(validate_socratic_question(hint), hint)

    def test_english_source_words_are_context(self):
        for word in ('solution', 'therefore'):
            hint = f'Trong đoạn văn, từ {word} đóng vai trò gì?'
            question = f'Read the passage containing the word {word}.'
            with self.subTest(word=word):
                self.assertEqual(validate_socratic_question(hint, question), hint)

    def test_actual_disclosures_and_new_numeric_results_remain_rejected(self):
        for hint in ('Đáp án là B, em thấy đúng không?', 'Đáp án đúng: B, em hiểu chưa?',
                     'Em hãy chọn A nhé?', 'Em thấy x=77 có đúng không?',
                     'Em thấy x=77.5 có đúng không?', 'Em thấy x=7/2 có đúng không?',
                     'Kết quả là nước, em có hiểu không?'):
            with self.subTest(hint=hint), self.assertRaises(LessonContractError):
                validate_socratic_question(hint)
        with self.assertRaises(LessonContractError):
            validate_socratic_question('Em có thấy đường thẳng y=x+3 phù hợp không?',
                                       'Tìm tiệm cận xiên.', 'A. y=x+3')

    def test_worked_theory_numbers_remain_allowed_in_all_supported_contexts(self):
        lesson = complete_lesson('Ví dụ có lời giải: $x=77$, $y=2x+1$, $1+1=2$.')
        contexts = [(s, g) for g in range(6, 13) for s in subjects_for_grade(g)]
        self.assertEqual(len(contexts), 65)
        for subject, grade in contexts:
            with self.subTest(subject=subject, grade=grade):
                self.assertEqual(validate_lesson_contract(lesson, subject, grade), lesson)


if __name__ == '__main__':
    unittest.main()
