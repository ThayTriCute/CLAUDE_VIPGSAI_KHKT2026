import unittest
from services.curriculum_policy import correct_reviewed_reaction_rate as repair


class ReviewedReactionRateTests(unittest.TestCase):
    topic = 'Tốc độ phản ứng — Hóa học 10, KNTT, Bài 19'

    def test_rate_formula_repair_preserves_signs_coefficients(self):
        raw = (r'$aA + bB \rightarrow cC + dD$v_{tb} = -$\frac{1}{a}$ \cdot '
               r'$\frac{\Delta C_A}{\Delta t}$ = -$\frac{1}{b}$ \cdot '
               r'$\frac{\Delta C_B}{\Delta t}$ = $\frac{1}{c}$ \cdot '
               r'$\frac{\Delta C_C}{\Delta t}$ = $\frac{1}{d}$ \cdot $\frac{\Delta C_D}{\Delta t}$')
        result = repair(raw, 'Hóa học', 10, self.topic)
        self.assertIn(r'$$v_{tb}=-\frac{1}{a}', result)
        self.assertIn(r'=\frac{1}{d}\frac{\Delta C_D}{\Delta t}$$', result)
        self.assertEqual(repair(result, 'Hóa học', 10, self.topic), result)
        self.assertEqual(repair(raw, 'Hóa học', 11, self.topic), raw)
        self.assertEqual(repair(raw, 'Vật lý', 10, self.topic), raw)
        self.assertEqual(repair('```text\n'+raw+'\n```', 'Hóa học', 10, self.topic), '```text\n'+raw+'\n```')

    def test_source_assumptions_added_once_without_changing_key(self):
        raw = ('**b. Các yếu tố ảnh hưởng đến tốc độ phản ứng**\n'
               '**3. Ví dụ có lời giải**\nCORRECT: C\n'
               'Dữ liệu thực nghiệm cho thấy tại một thời điểm, nồng độ là 0,500 M.')
        result = repair(raw, 'Hóa học', 10, self.topic)
        self.assertIn('biểu thức tốc độ được xác định từ thực nghiệm', result)
        self.assertIn('dữ liệu giả định', result)
        self.assertIn('CORRECT: C', result)
        self.assertEqual(repair(result, 'Hóa học', 10, self.topic), result)
