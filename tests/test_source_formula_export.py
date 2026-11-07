import unittest
from unittest.mock import patch

from services.lesson_sources import lesson_source_review_html
from services.lesson_export import build_lesson_html


class SourceFormulaExportTests(unittest.TestCase):
    def test_shared_source_math_for_supported_subjects_grades_and_styles(self):
        from services.academic_context import subjects_for_grade
        review = dict(status='reviewed_requirements_source', reviewed_on='2026-11-07',
                      scope='Fixture, not academic approval', sources=[dict(
                          url='https://example.com', title='Source', locator='p1',
                          edition_note='Edition', criteria=[r'Điều kiện $x^2\geq 0$.',
                          r'Phương trình $\ce{2H2 + O2 -> 2H2O}$. `x**2`'])])
        for grade in range(6, 13):
            for subject in subjects_for_grade(grade):
                for style in ('handwritten', 'color', 'monochrome'):
                    with self.subTest(subject=subject, grade=grade, style=style):
                        with patch('services.lesson_sources.reviewed_lesson_sources', return_value=review):
                            page = build_lesson_html(subject, grade, 'Fixture', 'Nội dung giữ nguyên', style)
                        self.assertIn('data-tex="x^2\\geq 0"', page)
                        self.assertIn('data-tex="\\ce{2H2 + O2 -&gt; 2H2O}"', page)
                        self.assertIn('<code>x**2</code>', page)
                        self.assertIn('Nội dung giữ nguyên', page)

    def test_actual_rate_source_uses_math_tokens_and_separate_paragraphs(self):
        page = build_lesson_html('Hóa học', 10,
                                'Tốc độ phản ứng — Hóa học 10, KNTT, Bài 19',
                                'Bài đã lưu', 'monochrome')
        source = page.split('class="source-criteria"', 1)[1]
        self.assertIn('data-tex=', source)
        self.assertIn('\\frac{\\Delta C_A}', source)
        self.assertIn('\\gamma^{(T_2-T_1)/10}', source)
        self.assertNotIn('v=-ΔCA/(aΔt)', source)
        self.assertNotIn('gamma^((T2-T1)/10)', source)

    def test_source_prose_escapes_html_and_preserves_code(self):
        review = dict(status='reviewed_requirements_source', reviewed_on='2026-11-07',
                      scope='Limited', sources=[dict(url='https://example.com', title='Source',
                      locator='p1', edition_note='Edition', criteria=[
                          '<script>alert(1)</script> $x^2$ `a_b`'])])
        with patch('services.lesson_sources.reviewed_lesson_sources', return_value=review):
            value = lesson_source_review_html('Toán học', 10, 'Example')
        self.assertNotIn('<script>', value)
        self.assertIn('&lt;script&gt;', value)
        self.assertIn('<code>a_b</code>', value)
        self.assertIn('data-tex="x^2"', value)


if __name__ == '__main__':
    unittest.main()
