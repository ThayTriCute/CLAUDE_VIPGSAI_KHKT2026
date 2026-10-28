import copy
import unittest
from unittest.mock import Mock

from services.context_recovery import repair_exam_context
from services.math_conditions import math_condition_conflict
from services.neuro_symbolic_verifier import audit_ai_generated_question_sympy


POINTS = ('Cho hàm số bậc ba $y=f(x)=ax^3+bx^2+cx+d$ ($a\\ne0$) có đồ thị đi qua bốn điểm '
          '$A(0;2)$, $B(1;0)$, $C(-1;6)$ và $D(2;0)$. Phát biểu nào đúng về tính đơn điệu?')
BOUNDARY = ('Tìm giá trị của tham số $m$ để hàm số $y=x^3-3x^2+mx+1$ không có cực trị. '
            '(Nếu kết quả là một khoảng hoặc đoạn, hãy nhập giá trị biên lớn nhất của $m$ thỏa mãn điều kiện đó).')


def question(text):
    return dict(subject='Toán học', grade=12, topic='Khảo sát hàm số', level='TH',
                q=text, opt=['A. 0','B. 1','C. 2','D. 3'], ans='A')


class TestMathConditions(unittest.TestCase):
    def test_live_four_points_force_zero_leading_coefficient(self):
        q = question(POINTS)
        before = copy.deepcopy(q)
        self.assertEqual(math_condition_conflict(q), 'asserted_cubic_inconsistent_with_points')
        self.assertTrue(audit_ai_generated_question_sympy(q)['hallucination_detected'])
        self.assertEqual(q, before)

    def test_actual_cubic_and_unrelated_later_point_are_not_rejected(self):
        text = POINTS.replace('B(1;0)', 'B(1;3)').replace('C(-1;6)', 'C(-1;1)').replace('D(2;0)', 'D(2;10)')
        self.assertEqual(math_condition_conflict(question(text)), '')  # x^3+2
        self.assertEqual(math_condition_conflict(question(text + ' Xét thêm điểm M(5;7).')), '')

    def test_less_than_four_asserted_points_or_existence_question_is_unknown(self):
        for text in (POINTS.replace('bốn điểm','ba điểm'), POINTS.replace('Cho hàm số bậc ba','Có tồn tại hàm số bậc ba')):
            self.assertEqual(math_condition_conflict(question(text)), '')

    def test_no_extrema_set_has_no_largest_boundary(self):
        self.assertEqual(math_condition_conflict(question(BOUNDARY)), 'requested_parameter_boundary_does_not_exist')
        self.assertEqual(math_condition_conflict(question(BOUNDARY.replace('lớn nhất','nhỏ nhất'))), '')

    def test_opposite_half_line_has_no_smallest_boundary(self):
        text = BOUNDARY.replace('+mx','-mx').replace('lớn nhất','nhỏ nhất')
        self.assertEqual(math_condition_conflict(question(text)), 'requested_parameter_boundary_does_not_exist')
        self.assertEqual(math_condition_conflict(question(text.replace('nhỏ nhất','lớn nhất'))), '')

    def test_additional_restrictions_are_not_guessed(self):
        for text in (BOUNDARY.replace('tham số $m$', 'tham số $m\\in[0;5]$'),
                     BOUNDARY.replace('không có cực trị.', 'không có cực trị và $m<5$.'),
                     BOUNDARY.replace('không có cực trị.', 'không có cực trị trên đoạn $[0;1]$.'),
                     BOUNDARY.replace('tham số $m$', 'tham số nguyên $m$')):
            self.assertEqual(math_condition_conflict(question(text)), '', text)

    def test_recovery_replaces_whole_inconsistent_question_without_answer_rewrite(self):
        original = question(POINTS)
        before = copy.deepcopy(original)
        candidate = question('Cho hàm số $y=x^3+x$. Hàm số có bao nhiêu điểm cực trị?')
        ai = Mock()
        result = repair_exam_context({'p1':[original]}, 'Toán học', 12, topics=['Khảo sát hàm số'],
            bank_provider=lambda *_: {'p1':[candidate]}, ai_generator=ai)
        self.assertEqual(result['context_recovery']['unresolved'], 0)
        self.assertEqual(result['p1'][0]['q'], candidate['q'])
        self.assertEqual(original, before)
        ai.assert_not_called()

    def test_other_subjects_and_long_or_unparsed_input_are_not_blocked(self):
        self.assertEqual(math_condition_conflict(dict(question(POINTS), subject='Tiếng Anh')), '')
        self.assertEqual(math_condition_conflict(question('x'*10001)), '')
        self.assertEqual(math_condition_conflict(question(BOUNDARY.replace('x^3-3x^2+mx+1', 'g(x,m)'))), '')


if __name__ == '__main__':
    unittest.main()
