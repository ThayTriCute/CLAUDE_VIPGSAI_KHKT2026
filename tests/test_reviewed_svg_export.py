from html.parser import HTMLParser
import re
import unittest

from services.lesson_export import build_lesson_html, lesson_body_html
from services.lesson_sources import reviewed_lesson_sources


class Tags(HTMLParser):
    def __init__(self):
        super().__init__()
        self.svg_count = 0

    def handle_starttag(self, tag, attrs):
        if tag == 'svg':
            self.svg_count += 1


class ReviewedSvgExportTests(unittest.TestCase):
    topic = 'Dao động điều hòa — Vật lí 11, KNTT, Bài 1'

    def svg(self):
        review = reviewed_lesson_sources('Vật lý', 11, self.topic)
        return next(m[0] for rule in review['content_corrections']
                    for m in re.finditer(r'<svg\b[^>]*>[\s\S]*?</svg>', rule['after']))

    def count(self, body):
        parser = Tags()
        parser.feed(body)
        return parser.svg_count

    def test_exact_reviewed_figure_is_an_element_in_all_export_styles(self):
        svg = self.svg()
        for style in ('handwritten', 'color', 'monochrome'):
            body = build_lesson_html('Vật lý', 11, self.topic, 'Hình mô hình\n\n' + svg, style)
            self.assertEqual(self.count(body), 1)
            self.assertIn('(2; −40)', body)
            self.assertIn('background:transparent', body)

    def test_wrong_topic_and_unreviewed_raw_html_remain_escaped(self):
        self.assertEqual(self.count(build_lesson_html('Vật lý', 11, 'Other lesson', self.svg())), 0)
        body = lesson_body_html('<svg onload="alert(1)"><script>alert(1)</script></svg>')
        self.assertEqual(self.count(body), 0)
        self.assertNotIn('<script>', body)

    def test_matching_svg_in_code_is_not_promoted_to_an_illustration(self):
        svg = self.svg()
        for code in ('`' + svg + '`', '```html\n' + svg + '\n```'):
            self.assertEqual(self.count(lesson_body_html(code, trusted_svgs=[svg])), 0)


if __name__ == '__main__':
    unittest.main()
