"""Exercise the actual Station 1 renderer against lost-row regressions."""
import html
import unittest
from services.curriculum_policy import correct_khtn8_lime_soil_confusion

from tests.test_expert_patch_regressions import load_function


class TeacherLessonTableTests(unittest.TestCase):
    def test_observed_polya_plan_does_not_reintroduce_touch_or_taste(self):
        source = ('Nước xà phòng, nước vắt từ quả cam, nước tinh khiết.\n'
                  'Xác định môi trường của từng mẫu dựa trên kiến thức thực tế '
                  '(Ví dụ: Cam có vị chua thì chứa chất gì? Xà phòng có cảm giác nhờn thì thuộc loại nào?).')
        fixed = correct_khtn8_lime_soil_confusion(source, 'Khoa học tự nhiên', 8)
        self.assertNotIn('cảm giác nhờn', fixed)
        self.assertIn('không nếm hoặc chạm mẫu', fixed)
        self.assertEqual(correct_khtn8_lime_soil_confusion(fixed, 'Khoa học tự nhiên', 8), fixed)
        self.assertEqual(correct_khtn8_lime_soil_confusion(source, 'Ngữ văn', 8), source)

    @classmethod
    def setUpClass(cls):
        cls.render = staticmethod(load_function('render_pedagogical_lesson_visuals', html=html,
            _parse_bbt_cells_safe=load_function('_parse_bbt_cells_safe')))

    def test_live_ph_table_keeps_all_three_samples(self):
        source = ('| Dung dịch | Giá trị pH |\n|---|---|\n'
                  '| Nước chanh | 3 |\n| Nước tinh khiết | 7 |\n| Nước xà phòng | 10 |\n')
        self.assertEqual(self.render(source, 'Khoa học tự nhiên', 8), source)

    def test_multirow_table_is_not_partially_converted_as_frequency_table(self):
        source = ('| Giá trị | 1 | 2 |\n|---|---|---|\n'
                  '| n | 3 | 4 |\n| Ghi chú | thấp | cao |\n')
        self.assertEqual(self.render(source, 'Tin học', 8), source)

    def test_two_row_frequency_table_still_renders_without_losing_values(self):
        source = '| Nhóm | [0; 5) | [5; 10) |\n|---|---|---|\n| Tần số | 3 | 7 |\n'
        for newline in ('\n', '\r\n'):
            with self.subTest(newline=repr(newline)):
                result = self.render(source.replace('\n', newline), 'Toán học', 11)
                self.assertIn('<table', result)
                for value in ('[0; 5)', '[5; 10)', '>3</td>', '>7</td>'):
                    self.assertIn(value, result)


if __name__ == '__main__':
    unittest.main()
