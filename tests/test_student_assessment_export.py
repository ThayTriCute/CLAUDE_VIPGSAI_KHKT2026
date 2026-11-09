import hashlib
import json
import unittest
from services.lesson_export import build_lesson_html, lesson_body_html, handwritten_prompt, faithful_infographic_data


class StudentAssessmentExportTests(unittest.TestCase):
    source = ('### PHẦN 2: TRẮC NGHIỆM KHÁCH QUAN SOCRATIC\n\n'
              '**Câu 1. [Mức độ: TH]**\nĐọc và chọn phương án.\n'
              'A. $x=1$\nB. $x=2$\nC. $x=3$\nD. $x=4$\n'
              'OUTCOME: INTERNAL_OUTCOME\nCORRECT: C\nHINT: PRIVATE_HINT\nEXPLAIN: PRIVATE_EXPLANATION\n\n'
              '### PHẦN 3: BÀI TẬP TỰ LUẬN\nCâu 2. Bước 1: Giữ lời giải và rubric tự luận.')

    def test_all_styles_and_contexts_separate_answers_from_student_questions(self):
        for subject, grade in [('Toán học', 10), ('Vật lý', 11), ('Lịch sử', 12), ('Tiếng Anh', 11)]:
            for style in ('handwritten', 'color', 'monochrome'):
                with self.subTest(subject=subject, grade=grade, style=style):
                    page = build_lesson_html(subject, grade, 'Bài kiểm bố cục', self.source, style)
                    student, teacher = page.split('<details class="answer-key">', 1)
                    for value in ('PRIVATE_', 'CORRECT:', 'HINT:', 'EXPLAIN:', 'SOCRATIC'):
                        self.assertNotIn(value, student)
                    self.assertIn('PRIVATE_HINT', teacher)
                    self.assertIn('Đáp án:', teacher)
                    self.assertIn('.answer-key:not([open]){display:none}', page)
                    self.assertEqual(student.count('class="mc-option"'), 4)
                    self.assertIn('data-tex="x=3"', student)
                    self.assertIn('rubric tự luận', student)
                    self.assertIn('getBoundingClientRect', page)
                    self.assertIn('ResizeObserver', page)

    def test_image_inputs_exclude_answers_but_keep_raw_source_digest(self):
        prompt = json.loads(handwritten_prompt('Toán học', 10, 'Bài kiểm bố cục', self.source))
        data = faithful_infographic_data('Toán học', 10, 'Bài kiểm bố cục', self.source)
        for value in (prompt['content'], json.dumps(data)):
            self.assertNotIn('PRIVATE_', value)
            self.assertNotIn('CORRECT:', value)
            self.assertNotIn('SOCRATIC', value)
        self.assertEqual(data['source_sha256'], hashlib.sha256(self.source.encode()).hexdigest())
        self.assertIn('CORRECT: C', self.source)

    def test_inline_fields_and_incomplete_options_do_not_leak(self):
        for source in ('Câu 1. Chọn. A. Một B. Hai C. Ba D. Bốn CORRECT: B HINT: SECRET EXPLAIN: SECRET2',
                       'Câu 1. Chọn.\nA. Một\nB. Hai\nCORRECT: B\nEXPLAIN: SECRET'):
            body = lesson_body_html(source)
            self.assertNotIn('SECRET', body)
            self.assertNotIn('CORRECT', body)
            self.assertIn('Một', body)

    def test_code_and_authentic_foreign_language_are_preserved(self):
        source = ('```text\nCâu 1. Example\nA. A\nB. B\nC. C\nD. D\nCORRECT: literal\n```\n'
                  'Câu 2. Which sentence is correct?\nA. I am ready.\nB. I is ready.\n'
                  'C. I are ready.\nD. I be ready.\nCORRECT: A\nEXPLAIN: PRIVATE')
        body = lesson_body_html(source)
        self.assertIn('CORRECT: literal', body)
        self.assertIn('Which sentence is correct?', body)
        self.assertIn('I am ready.', body)
        self.assertNotIn('PRIVATE', body)
        self.assertEqual(body.count('class="mc-option"'), 4)


if __name__ == '__main__':
    unittest.main()
