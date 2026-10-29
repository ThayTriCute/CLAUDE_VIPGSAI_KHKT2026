import unittest

from data.socratic_anchors import sanitize_socratic_hint
from services.academic_context import subjects_for_grade


class TestComputingContextHints(unittest.TestCase):
    def test_live_cpu_metaphor_is_replaced_without_changing_valid_hint(self):
        question = 'Phát biểu nào sau đây về CPU là ĐÚNG?'
        leaked = "Thành phần nào được ví như 'bộ não' điều phối mọi hoạt động suy nghĩ và tính toán của máy tính?"
        options = ['A. Lưu trữ lâu dài', 'B. CPU là bộ não, tính toán và điều khiển',
                   'C. Hiển thị', 'D. Thiết bị ra']
        for grade in range(6, 13):
            result = sanitize_socratic_hint(leaked, 'B', question, options,
                                            subject='Tin học', grade_num=grade)
            self.assertIn('phân biệt', result)
            self.assertNotIn('bộ não', result)
            self.assertTrue(result.endswith('?'))
        supplied = 'Em sẽ dùng tiêu chí nào để kiểm tra chức năng của từng thành phần?'
        self.assertEqual(sanitize_socratic_hint(supplied, q_text=question,
                                              subject='Tin học'), supplied)

    def test_live_storage_and_connection_fallbacks_match_task_without_solution(self):
        storage = sanitize_socratic_hint('', '4096',
            'Thẻ nhớ dung lượng 16 GB, bức ảnh 4 MB; tối đa bao nhiêu ảnh?', subject='Tin học')
        self.assertIn('cùng đơn vị', storage)
        self.assertIn('phần dư', storage)
        for value in ('4096', '1024', '16', '4 MB'):
            self.assertNotIn(value, storage)
        connection = sanitize_socratic_hint('', q_text=
            'Sự đa dạng của các thiết bị số và khả năng kết nối của chúng', subject='Tin học')
        self.assertIn('từng nhận định', connection)
        self.assertNotIn('HDMI', connection)

    def test_all_contexts_keep_unrelated_valid_hints(self):
        hint = 'Em cần đối chiếu dữ kiện nào trước khi kiểm tra phát biểu?'
        for grade in range(6, 13):
            for subject in subjects_for_grade(grade):
                self.assertEqual(sanitize_socratic_hint(hint, q_text='Nhiệm vụ học tập.',
                    subject=subject, grade_num=grade), hint)
        self.assertNotIn('CPU', sanitize_socratic_hint('', q_text='CPU', subject='Ngữ văn'))


if __name__ == '__main__':
    unittest.main()
