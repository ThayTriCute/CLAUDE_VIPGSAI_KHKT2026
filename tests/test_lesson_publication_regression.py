import unittest

from services.context_recovery import needs_visual
from services.lesson_contract import (validate_lesson_contract, validate_socratic_question,
                                      LessonContractError, student_polya)
from services.math_publication import generate_checked_text
from tests.lesson_samples import complete_lesson


class TestLessonPublicationRegression(unittest.TestCase):
    def test_table_as_requested_output_is_not_missing_input(self):
        for text in ("Cho $y=x^3-3x+1$. Lập bảng biến thiên của hàm số.",
                     "Bảng biến thiên của hàm số $y=x^3-3x+1$ được lập theo những bước nào?",
                     "Xét dấu đạo hàm rồi lập bảng xét dấu của hàm số đã cho."):
            self.assertFalse(needs_visual({'q': text}), text)

    def test_missing_input_table_and_figure_still_require_recovery(self):
        for text in ("Cho hàm số có bảng biến thiên sau đây.",
                     "Dựa vào bảng xét dấu, tìm khoảng đồng biến.",
                     "Bảng biến thiên của $y=x^3-3x+1$ như hình bên.",
                     "Cho đồ thị như hình vẽ bên."):
            self.assertTrue(needs_visual({'q': text}), text)

    def test_formula_question_about_table_can_be_published(self):
        text = complete_lesson().replace('Một nửa của 4 là bao nhiêu?',
            'Cho $y=x^3-3x+1$. Để lập bảng biến thiên, trước tiên xét đại lượng nào?')
        self.assertEqual(validate_lesson_contract(text, 'Toán', 12), text)

    def test_bold_ai_field_variants_are_normalized_without_inventing_content(self):
        for key, hint in (('**ĐÁP ÁN:** B', '**GỢI MỞ SOCRATIC:** '),
                          ('**ĐÁP ÁN: B**', '**GỢI MỞ SOCRATIC**: ')):
            text = complete_lesson().replace('ĐÁP ÁN: B', key).replace('GỢI MỞ SOCRATIC: ', hint)
            checked = validate_lesson_contract(text, 'Toán', 6)
            self.assertIn('ĐÁP ÁN: B', checked)
            self.assertNotIn('**GỢI MỞ', checked)

    def test_two_contextual_questions_are_not_a_worked_solution(self):
        hint = 'Em cần tìm đạo hàm để xét đại lượng nào? Em sẽ dùng dấu của đạo hàm để kết luận ra sao?'
        self.assertEqual(validate_socratic_question(hint), hint)
        with self.assertRaises(LessonContractError):
            validate_socratic_question('Em tính được nghiệm là 2? Em chọn A phải không?')

    def test_bold_same_line_polya_question_is_retained(self):
        text = complete_lesson()
        for n, label in enumerate(('Tìm hiểu đề', 'Lập kế hoạch', 'Thực hiện kế hoạch', 'Kiểm tra và nhìn lại'), 1):
            text = text.replace(f'Bước {n}: {label}\n', f'**Bước {n}: {label}** ')
        checked = validate_lesson_contract(text, 'Toán', 6)
        self.assertEqual(student_polya(checked, 'Toán', 6).count('Em cần tự xem xét thông tin nào ở bước này?'), 8)

    def test_markdown_separator_after_essay_does_not_become_a_solution(self):
        text = complete_lesson().replace('Câu 2. [Mức độ: VD]', '---\nCâu 2. [Mức độ: VD]') + '\n---\n'
        validate_lesson_contract(text, 'Toán', 6)
        self.assertEqual(student_polya(text, 'Toán', 6).count('Em cần tự xem xét thông tin nào ở bước này?'), 8)

    def test_structural_repair_can_replace_whole_incomplete_question(self):
        calls = []
        broken = complete_lesson().replace('Một nửa của 4 là bao nhiêu?',
                                          'Cho đồ thị như hình bên. Tung độ cực đại là bao nhiêu?')
        def generator(prompt):
            calls.append(prompt)
            return broken if len(calls) == 1 else complete_lesson()
        generate_checked_text('Toán lớp 12', generator, lambda text: validate_lesson_contract(text, 'Toán', 12))
        self.assertEqual(len(calls), 2)
        self.assertIn('TOÀN BỘ', calls[1])
        self.assertNotIn('giữ nguyên nhiệm vụ, số liệu và ý nghĩa', calls[1])

    def test_derivative_zero_is_a_method_not_a_computed_root(self):
        hint = "Em sẽ giải điều kiện $f'(x)=0$ để xác định các mốc xét dấu như thế nào?"
        self.assertEqual(validate_socratic_question(hint, 'Khảo sát hàm số đã cho.'), hint)
        with self.assertRaises(LessonContractError):
            validate_socratic_question('Em đã tính được $x=77$ chưa?', 'Tìm nghiệm của phương trình.')

    def test_repeated_given_numeric_data_does_not_include_prose_in_equation_match(self):
        hint = 'Em sẽ dùng giả thiết $a = 2$ để đối chiếu điều kiện nào?'
        self.assertEqual(validate_socratic_question(hint, 'Cho tham số $a=2$.'), hint)

    def test_inline_polya_question_does_not_repeat_step_title_in_body(self):
        text = complete_lesson()
        for n, title in enumerate(('Tìm hiểu đề', 'Lập kế hoạch', 'Thực hiện kế hoạch', 'Kiểm tra và nhìn lại'), 1):
            text = text.replace(f'Bước {n}: {title}\n', f'Bước {n}: {title}. ')
        rendered = student_polya(text, 'Toán', 6)
        for title in ('Tìm hiểu đề', 'Lập kế hoạch', 'Thực hiện kế hoạch', 'Kiểm tra và nhìn lại'):
            self.assertEqual(rendered.count(title), 2)

    def test_bold_question_number_does_not_leave_dangling_stars_in_essay(self):
        text = complete_lesson().replace('Câu 1. [Mức độ: VD]', '**Câu 1. [Mức độ: VD]**')
        self.assertNotIn('\n\n** Tự tính', student_polya(text, 'Toán', 6))

    def test_repeated_step_heading_inside_body_is_not_rendered_twice(self):
        text = complete_lesson().replace('Em cần tự xem xét thông tin nào ở bước này?',
                                         'Tìm hiểu đề\nEm cần tự xem xét thông tin nào ở bước này?')
        rendered = student_polya(text, 'Toán', 6)
        self.assertEqual(rendered.count('Tìm hiểu đề'), 2)
