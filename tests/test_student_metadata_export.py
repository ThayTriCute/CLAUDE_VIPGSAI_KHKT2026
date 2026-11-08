import hashlib
import json
import unittest

from services.lesson_export import build_lesson_html, faithful_infographic_data, handwritten_prompt
from services.text_boundaries import chemical_display_markdown, student_essay_text


class StudentMetadataExportTests(unittest.TestCase):
    source = ('Câu 1. Nội dung học sinh cần đọc.\n'
              '* **OUTCOME:** PRIVATE_OUTCOME $x$\n'
              '* **COGNITIVE_REASON:** PRIVATE_REASON\n'
              '* **COGNITIVE_STEPS:** [\n "PRIVATE_STEP",\n "PRIVATE_OTHER"\n]\n'
              'Bước 1: Tìm hiểu đề\nDữ kiện $x=3$.\n'
              'Đáp án và rubric giữ nguyên.\nCâu 2. Nhiệm vụ tiếp theo.')

    def test_student_exports_for_multiple_subjects_and_grades_hide_author_fields(self):
        for subject, grade in [('Toán học', 10), ('Vật lý', 11),
                               ('Lịch sử', 12), ('Tiếng Anh', 11)]:
            for style in ('handwritten', 'color', 'monochrome'):
                with self.subTest(subject=subject, grade=grade, style=style):
                    body = build_lesson_html(subject, grade, 'Bài kiểm bố cục', self.source, style)
                    self.assertNotIn('PRIVATE_', body)
                    self.assertNotIn('COGNITIVE_REASON', body)
                    self.assertIn('Nhiệm vụ tiếp theo', body)
                    self.assertIn('rubric giữ nguyên', body)
                    self.assertIn('data-tex="x=3"', body)
        self.assertIn('PRIVATE_OUTCOME', self.source)

    def test_image_prompt_and_infographic_excerpt_use_the_same_student_boundary(self):
        prompt = json.loads(handwritten_prompt('Vật lý', 11, 'Bài kiểm bố cục', self.source))
        self.assertNotIn('PRIVATE_', prompt['content'])
        excerpt = faithful_infographic_data('Vật lý', 11, 'Bài kiểm bố cục', self.source)
        self.assertNotIn('PRIVATE_', json.dumps(excerpt))
        self.assertEqual(excerpt['source_sha256'], hashlib.sha256(self.source.encode()).hexdigest())

    def test_code_examples_remain_intact_but_real_metadata_is_hidden(self):
        code = '```text\nOUTCOME: code example\nCOGNITIVE_STEPS: ["literal"]\n```'
        value = student_essay_text('OUTCOME: PRIVATE\n' + code + '\nCâu 2. Giữ lại.')
        self.assertNotIn('PRIVATE', value)
        self.assertIn(code, value)
        self.assertIn('Câu 2.', value)

    def test_shared_live_display_hides_metadata_without_forcing_option_layout(self):
        for separate_steps in (True, False):
            value = chemical_display_markdown(self.source, separate_steps=separate_steps)
            self.assertNotIn('PRIVATE_', value)
            self.assertIn('Câu 2.', value)
            self.assertIn('$x=3$', value)
        self.assertEqual(chemical_display_markdown('Bước 1: Lựa chọn', separate_steps=False),
                         'Bước 1: Lựa chọn')


if __name__ == '__main__':
    unittest.main()
