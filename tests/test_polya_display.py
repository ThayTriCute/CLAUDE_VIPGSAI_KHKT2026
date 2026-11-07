import unittest

from services.lesson_export import lesson_body_html
from services.text_boundaries import chemical_display_markdown, polya_display_markdown, student_essay_text


class PolyaDisplayTests(unittest.TestCase):
    def test_plain_example_steps_are_separate_in_live_and_export(self):
        source = ('Ví dụ: Đối chiếu số đo.\nHướng dẫn:\n'
                  '- Bước 1: So sánh $pH=5,5$ với ngưỡng.\n'
                  '- Bước 2: Xét điều kiện trước khi kết luận.')
        for render in (polya_display_markdown, chemical_display_markdown):
            result = render(source)
            self.assertIn('\n\n**Bước 1:** So sánh $pH=5,5$', result)
            self.assertIn('\n\n**Bước 2:** Xét điều kiện', result)
            self.assertEqual(render(result), result)
            self.assertNotIn('Tìm hiểu đề', result)
        page = lesson_body_html(source)
        self.assertIn('<p><strong>Bước 1:</strong>', page)
        self.assertIn('<p><strong>Bước 2:</strong>', page)

    def test_arbitrary_step_count_inline_english_and_protected_content(self):
        source = ('Quy trình: Step 1: Read the data. Step 5: Check the result.\n'
                  'Bước 6: Viết báo cáo.\n'
                  '`Bước 1: literal`\n$\\text{Step 2: keep}$\n'
                  '<svg><text>Bước 3: Nhãn hình</text></svg>')
        result = chemical_display_markdown(source)
        for label in ('Step 1', 'Step 5', 'Bước 6'):
            self.assertIn('\n\n**' + label + ':**', result)
        for protected in ('`Bước 1: literal`', '$\\text{Step 2: keep}$',
                          '<svg><text>Bước 3: Nhãn hình</text></svg>'):
            self.assertIn(protected, result)
        option = 'A. Bước 1: So sánh rồi kết luận.'
        self.assertEqual(chemical_display_markdown(option, separate_steps=False), option)

    def test_exam_answer_html_and_tex_reuse_step_layout_without_editing_code(self):
        from services.exam_code_text import teaching_text_html, teaching_text_latex
        source = ('Bước 1: Xét $x<2$. Bước 2: Kết luận.\n\n'
                  '```text\n**Bước 9:** literal\n```\n'
                  '$\\text{Bước 8: keep}$')
        page = teaching_text_html(source)
        self.assertIn('<strong>Bước 1:</strong>', page)
        self.assertIn('<br><br><strong>Bước 2:</strong>', page)
        self.assertIn('**Bước 9:** literal', page)
        self.assertNotIn('<strong>Bước 9:', page)
        tex = teaching_text_latex(source, lambda value: value)
        self.assertIn(r'\par\smallskip Bước 2:', tex)
        self.assertIn('**Bước 9:** literal', tex)
        self.assertIn('$\\text{Bước 8: keep}$', tex)
        self.assertIn('$x<2$', tex)

    source = ('Câu 1. Em hãy kể một trải nghiệm.\n\n'
              'Bước 1: Tìm hiểu đề: Em kể điều gì? Bước 2: Lập kế hoạch: Chọn trình tự. '
              'Bước 3: Thực hiện kế hoạch: Tự viết bài. Bước 4: Kiểm tra và nhìn lại: Tự sửa.')

    def test_collapsed_real_world_layout_becomes_four_separate_paragraphs(self):
        result = student_essay_text(self.source)
        for n in range(1, 5):
            self.assertIn(f'\n\n**Bước {n}:', result)
        self.assertIn('Em kể điều gì?', result)
        self.assertIn('Tự viết bài.', result)
        self.assertEqual(student_essay_text(result), result)
        page = lesson_body_html(self.source)
        for n in range(1, 5):
            self.assertIn(f'<p><strong>Bước {n}:', page)

    def test_bold_list_layout_stays_readable_without_duplicate_markers(self):
        text = ('**Bước 1: Tìm hiểu đề:** Đọc đề.\n'
                '- **Bước 2: Lập kế hoạch:** Tự chọn.\n'
                '- **Bước 3: Thực hiện kế hoạch:** Tự làm.\n'
                '- **Bước 4: Kiểm tra và nhìn lại:** Đối chiếu.')
        result = polya_display_markdown(text)
        self.assertEqual(result.count('**Bước '), 4)
        self.assertNotIn('- **Bước', result)
        self.assertEqual(polya_display_markdown(result), result)

    def test_observed_bold_period_heading_leaves_no_markdown_debris(self):
        text = '*   **Bước 1: Tìm hiểu đề.** Đọc đúng ngữ cảnh.\n*   **Bước 2: Lập kế hoạch.** Giữ nội dung.'
        result = polya_display_markdown(text)
        self.assertNotIn('.**', result)
        self.assertIn('**Bước 1: Tìm hiểu đề:** Đọc đúng ngữ cảnh.', result)
        self.assertIn('\n\n**Bước 2: Lập kế hoạch:** Giữ nội dung.', result)
        self.assertEqual(polya_display_markdown(result), result)
        rendered = lesson_body_html(result)
        self.assertNotIn('.**', rendered)
        self.assertIn('Đọc đúng ngữ cảnh.', rendered)

    def test_code_math_and_mentions_are_not_rewritten(self):
        protected = ('```text\nBước 1: Tìm hiểu đề: sample\n```\n'
                     '`Bước 2: Lập kế hoạch: sample`\n$ x=1 $\n'
                     'Em đối chiếu Bước 3 trong quy trình đã học.')
        self.assertEqual(polya_display_markdown(protected), protected)
