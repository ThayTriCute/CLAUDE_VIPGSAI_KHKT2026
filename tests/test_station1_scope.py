"""Trạm 1 đúng môn/lớp (09/11/2026): minh họa mẫu, ngữ cảnh tên bài, chủ đề gợi ý.

Ca lỗi thật trước bản vá: bài KHTN 7 "Nguyên tử" (có cụm "hạt nhân") bị chèn đồ thị
phóng xạ Vật lí 12; KHTN 7 "Từ trường" bị chèn quy tắc bàn tay trái; KHTN 8 "chu trình
tuần hoàn" bị chèn chu trình p–V; Sinh 10 "thông tin di truyền" bị chèn phả hệ; Toán 12
"Vectơ trong không gian" bị chèn tứ diện tọa độ tự đặt A(2;0;0)... vì renderer hạ chữ
thường làm mất tên điểm. Chủ đề gợi ý Lịch sử 11 có "Chiến tranh thế giới I & II"
(thuộc LS&ĐL 8–9), Tin học 12 có CSDL/SQL (thuộc Tin học 11 KNTT)...
"""
import html
import re
import unittest

from services.academic_context import subjects_for_grade
from services.station1_scope import (GENERIC_NOTE, lesson_illustrations, lesson_part_spans, lesson_parts,
                                     topic_context_conflict, topic_context_mentions)
from tests.test_expert_patch_regressions import load_function

KEYWORD_RICH = ('hạt nhân, phóng xạ, chu kì bán rã, từ trường, lực từ, bàn tay trái, cảm ứng từ, '
                'đẳng nhiệt, khí lí tưởng, chu trình, di truyền, phả hệ, gen trội, hệ sinh thái, '
                'chuỗi thức ăn, lưới thức ăn, Daniell, vectơ trong không gian, mặt cầu, đường bay')
ALLOWED = {('Vật lý', 12): {'pv', 'magnetic', 'nuclear'}, ('Hóa học', 12): {'daniell'},
           ('Sinh học', 12): {'pedigree', 'food_web'}, ('Khoa học tự nhiên', 8): {'food_web'}}


def renderer():
    scope = {'html': html, 'sanitize_svg_for_markdown': lambda text: text}
    for name in ('_render_math_html_token', '_parse_bbt_cells_safe', '_normalize_moet_bbt_grid',
                 '_build_svg_bbt_from_rows', 'render_pedagogical_lesson_visuals'):
        scope[name] = load_function(name, **scope)
    return scope['render_pedagogical_lesson_visuals']


class IllustrationScopeTests(unittest.TestCase):
    def test_every_subject_grade_gets_only_its_own_curriculum_illustrations(self):
        for grade in range(6, 13):
            for subject in subjects_for_grade(grade):
                with self.subTest(subject=subject, grade=grade):
                    keys = set(lesson_illustrations(KEYWORD_RICH, subject, grade))
                    self.assertLessEqual(keys, ALLOWED.get((subject, grade), set()))

    def test_reproduced_wrong_grade_insertions_are_gone(self):
        cases = [('Khoa học tự nhiên', 7, 'Nguyên tử gồm hạt nhân mang điện dương và vỏ electron.'),
                 ('Khoa học tự nhiên', 7, 'Từ trường: xung quanh nam châm có từ trường.'),
                 ('Khoa học tự nhiên', 8, 'Chu trình tuần hoàn máu gồm vòng tuần hoàn lớn và nhỏ.'),
                 ('Vật lý', 10, 'Năng lượng hạt nhân là một dạng năng lượng.'),
                 ('Sinh học', 10, 'DNA mang thông tin di truyền của tế bào.'),
                 ('Toán học', 12, 'Bài 6. Vectơ trong không gian: tổng, hiệu hai vectơ.'),
                 ('Toán học', 12, 'Thiết bị bay theo một đường bay thẳng.')]
        for subject, grade, text in cases:
            with self.subTest(subject=subject, grade=grade):
                self.assertEqual(lesson_illustrations(text, subject, grade), [])

    def test_correct_lessons_keep_their_illustrations(self):
        self.assertEqual(lesson_illustrations('Phóng xạ và chu kì bán rã', 'Vật lý', 12), ['nuclear'])
        self.assertEqual(lesson_illustrations('Quy tắc bàn tay trái cho lực từ', 'Vật lý', 12), ['magnetic'])
        self.assertEqual(lesson_illustrations('Quá trình đẳng nhiệt của khí lí tưởng', 'Vật lý', 12), ['pv'])
        self.assertEqual(lesson_illustrations('Phân tích phả hệ', 'Sinh học', 12), ['pedigree'])
        self.assertEqual(lesson_illustrations('Chuỗi thức ăn và lưới thức ăn', 'Khoa học tự nhiên', 8), ['food_web'])
        self.assertEqual(lesson_illustrations('Pin Daniell', 'Hóa học', 12), ['daniell'])
        self.assertEqual(lesson_illustrations('Điều chế C2H4, đun nóng, thu khí bằng đẩy nước', 'Hóa học', 11), ['gas_c2h4'])

    def test_oxyz_figures_only_from_written_coordinates(self):
        axial = 'Trong hệ trục Oxyz cho A(3;0;0), B(0;6;0), C(0;0;2). Viết phương trình mặt cầu.'
        self.assertEqual(lesson_illustrations(axial, 'Toán học', 12), ['oxyz_tetra'])
        self.assertEqual(lesson_illustrations(axial, 'Toán học', 11), [])
        general = 'Trong hệ trục Oxyz cho A(1;2;3), B(0;4;1), C(2;0;5). Tính diện tích tam giác.'
        self.assertEqual(lesson_illustrations(general, 'Toán học', 12), [])  # engine chỉ vẽ O.ABC trên trục
        flight = 'Thiết bị bay theo đường bay từ M(1;3;4) đến N(5;7;12).'
        self.assertEqual(lesson_illustrations(flight, 'Toán học', 12), ['oxyz_flight'])

    def test_renderer_uses_lesson_coordinates_and_honest_note(self):
        try:
            import precision_visual_engine as pve
        except Exception as error:  # môi trường thiếu thư viện tùy chọn
            self.skipTest(str(error))
        render = renderer()
        axial = 'Trong hệ trục Oxyz cho A(3;0;0), B(0;6;0), C(0;0;2). Viết phương trình mặt cầu.'
        out = render(axial, 'Toán học', 12)
        self.assertIn(pve.build_oxyz_tetrahedron_model(axial)['svg'], out)
        self.assertNotIn(pve.build_oxyz_tetrahedron_model('')['svg'], out)
        decay = render('Phóng xạ: số hạt nhân giảm theo chu kì bán rã.', 'Vật lý', 12)
        self.assertIn(html.escape(GENERIC_NOTE), decay)
        self.assertNotIn('<svg', render('Nguyên tử gồm hạt nhân và vỏ.', 'Khoa học tự nhiên', 7))
        self.assertNotIn('<svg', render('Phóng xạ và chu kì bán rã.', 'Vật lý', 12, illustrations=False))


class TopicContextTests(unittest.TestCase):
    def test_owner_request_on_wrong_grade_is_blocked(self):
        topic = 'Khảo sát ba hàm số cơ bản trong sách toán 12 KNTT'
        self.assertEqual(topic_context_conflict(topic, 'Toán học', 11)['grade'], 12)
        self.assertEqual(topic_context_conflict(topic, 'Toán học', 12), {'grade': None, 'other_book': None})

    def test_other_subject_book_is_notice_not_grade_block(self):
        result = topic_context_conflict('Ứng dụng tích phân trong Vật lí 12', 'Toán học', 11)
        self.assertEqual(result, {'grade': None, 'other_book': ('Vật lý', 12)})

    def test_lop_khoi_mentions_keep_existing_rule(self):
        self.assertEqual(topic_context_conflict('Ôn tập lớp12A1', 'Toán học', 11)['grade'], 12)
        self.assertIsNone(topic_context_conflict('So sánh lớp 10 và lớp 11', 'Toán học', 11)['grade'])

    def test_grade_band_book_names_and_false_positives(self):
        self.assertEqual(topic_context_mentions('Lịch sử 8: Cách mạng tư sản Anh'), [('Lịch sử & Địa lý', 8)])
        self.assertEqual(topic_context_mentions('Vật lí 7 âm thanh'), [('Khoa học tự nhiên', 7)])
        self.assertEqual(topic_context_mentions('GDCD 10'), [('Giáo dục kinh tế và pháp luật', 10)])
        for text in ('Học sinh 12 tuổi', 'Đề toán 10 điểm', 'Toán 9 câu', 'KHTN 11'):
            with self.subTest(text=text):
                self.assertEqual(topic_context_mentions(text), [])
        self.assertEqual(topic_context_mentions('toán 10 dạng bài'), [('Toán học', 10)])


class CurriculumSuggestionTests(unittest.TestCase):
    def setUp(self):
        from data.curriculum_data import BIGDATA_CURRICULUM
        self.data = BIGDATA_CURRICULUM

    def test_every_offered_subject_grade_has_suggestions(self):
        for grade in range(6, 13):
            for subject in subjects_for_grade(grade):
                with self.subTest(subject=subject, grade=grade):
                    topics = self.data[subject][grade]
                    self.assertGreaterEqual(len(topics), 3)
                    self.assertTrue(all(re.match(r'Chuyên đề \d+: \S', t) for t in topics))

    def test_topics_misplaced_in_another_grade_are_corrected(self):
        joined = lambda subject, grade: ' | '.join(self.data[subject][grade])
        self.assertNotIn('Chiến tranh thế giới', joined('Lịch sử', 11))
        self.assertIn('Biển Đông', joined('Lịch sử', 11))
        self.assertNotIn('Biển Đông', joined('Lịch sử', 12))
        self.assertIn('Hồ Chí Minh', joined('Lịch sử', 12))
        self.assertNotRegex(joined('Tin học', 12), r'CSDL|SQL|JavaScript')
        self.assertIn('CSDL', joined('Tin học', 11))
        self.assertNotIn('tín dụng', joined('Giáo dục kinh tế và pháp luật', 12))
        self.assertNotIn('Quần thể', joined('Khoa học tự nhiên', 9))
        self.assertNotIn('Phân bào', joined('Sinh học', 12))
        self.assertIn('Thổ nhưỡng', joined('Lịch sử & Địa lý', 8))
        self.assertNotIn('tệ nạn', joined('Giáo dục công dân', 8))
        self.assertIn('Life on Other Planets', joined('Tiếng Anh', 8))
        self.assertIn('World Englishes', joined('Tiếng Anh', 9))
        self.assertIn('Life Stories We Admire', joined('Tiếng Anh', 12))

    def test_retained_worker_refreshes_new_scope_and_data(self):
        import ast
        from pathlib import Path
        from data import curriculum_data
        from services import station1_scope
        source = (Path(__file__).resolve().parents[1] / 'app.py').read_text(encoding='utf-8')
        refresh = next(n for n in ast.parse(source).body
                       if isinstance(n, ast.FunctionDef) and n.name == '_refresh_t1_context_services')
        body = ast.get_source_segment(source, refresh)
        self.assertIn(f'(station1_scope, {station1_scope.T1_CONTEXT_REVISION})', body)
        self.assertIn(f'(curriculum_data, {curriculum_data.T1_CONTEXT_REVISION})', body)


QUIZ = """Câu 1. [Mức độ: NB] Câu hỏi một?
A. Một
B. Hai
C. Ba
D. Bốn
CORRECT: B
HINT: Em nhớ lại?
Câu 2. [Mức độ: TH] Phần 2 nói về điều gì?
A. Cảnh
B. Nỗi nhớ
C. Lao động
D. Học tập
CORRECT: B
HINT: Đọc lại khổ 2–3?
"""
ESSAY = "Câu 1. [Mức độ: VD] Phân tích phần 3 của văn bản.\nBước 1: Tìm hiểu đề — đọc lại phần 3.\n"
OUTLINE = ("Bố cục: 3 phần\nPhần 1 (khổ 1): hình ảnh quê hương.\n"
           "Phần 2 (khổ 2–3): nỗi nhớ.\nPhần 3 (khổ cuối): tình yêu quê hương.\n")


def lesson(outline=OUTLINE, h2='### PHẦN 2: TRẮC NGHIỆM KHÁCH QUAN SOCRATIC', h3='### PHẦN 3: BÀI TẬP TỰ LUẬN'):
    return ("### PHẦN 1: BÀI HỌC\n**Khởi động:** ...\n**Hình thành kiến thức**\n" + outline
            + "**Luyện tập:** Tóm tắt.\n**Vận dụng:** Viết đoạn văn.\n" + h2 + "\n" + QUIZ + h3 + "\n" + ESSAY)


def old_parse_window(text):
    """Cách tách cũ của parse_quiz_questions (trước 09/11/2026) để so sánh."""
    part3 = re.search(r'(?im)^\s*(?:#{1,6}\s*)?PHẦN\s*3(?!\d)', text)
    window = text[:part3.start()] if part3 else text
    part2 = re.search(r'(?im)^\s*(?:#{1,6}\s*)?PHẦN\s*2(?!\d)', window)
    return window[part2.end():] if part2 else window


class LessonPartTests(unittest.TestCase):
    def parse(self, text):
        from unittest.mock import patch
        fn = load_function('parse_quiz_questions', sanitize_katex_latex=lambda s: s,
                           format_pedagogical_math=None, annotate_question=lambda q: q)
        with patch('random.shuffle', side_effect=lambda items: None):
            return fn(text)

    def test_outline_lines_do_not_cut_lesson_or_drop_quiz(self):
        text = lesson()
        part1, part2, part3 = lesson_parts(text)
        self.assertIn('Phần 3 (khổ cuối)', part1)
        self.assertIn('**Vận dụng:**', part1)
        self.assertTrue(part2.lstrip().startswith('Câu 1.'))
        self.assertTrue(part3.lstrip().startswith('Câu 1. [Mức độ: VD]'))
        self.assertEqual([q['question'] for q in self.parse(text)],
                         ['Câu hỏi một?', 'Phần 2 nói về điều gì?'])

    def test_standard_lessons_keep_previous_quiz_window(self):
        variants = [lesson(outline=''), lesson(outline='', h2='### PHẦN 2', h3='### PHẦN 3'),
                    lesson(outline='', h2='PHẦN 2: TRẮC NGHIỆM', h3='PHẦN 3: TỰ LUẬN'),
                    'Câu 1: Nội dung\nA. Một\nB. Hai\nC. Ba\nD. Bốn\nCORRECT: A\n']
        for text in variants:
            with self.subTest(text=text[:40]):
                spans = lesson_part_spans(text)
                new = text[:spans[3][0]] if 3 in spans else text
                new = new[spans[2][1]:] if 2 in spans else new
                self.assertEqual(new.split('Câu 1', 1)[-1], old_parse_window(text).split('Câu 1', 1)[-1])

    def test_bold_and_plain_heading_forms(self):
        text = lesson(h2='**PHẦN 2: TRẮC NGHIỆM**', h3='**PHẦN 3: BÀI TẬP TỰ LUẬN**')
        self.assertEqual(len(self.parse(text)), 2)
        self.assertIn('Phần 2 (khổ 2–3)', lesson_parts(text)[0])
        no_titles = lesson(h2='### PHẦN 2', h3='### PHẦN 3')
        self.assertEqual(len(self.parse(no_titles)), 2)
        self.assertTrue(lesson_parts(no_titles)[2].lstrip().startswith('Câu 1. [Mức độ: VD]'))


class GradeScopedPromptTests(unittest.TestCase):
    def test_three_form_survey_rules_only_for_grade12_math(self):
        from services.curriculum_policy import lesson_prompt
        for grade in range(6, 13):
            with self.subTest(grade=grade):
                prompt = lesson_prompt('Toán học', grade, 'Bài đang học')
                self.assertEqual('ad−bc≠0' in prompt, grade == 12)
                self.assertIn('Bảng biến thiên: chỉ khi', prompt)  # hướng dẫn bảng/đồ thị chung vẫn giữ

    def test_cubic_closing_reminder_is_bound_to_cubic_lessons(self):
        from pathlib import Path
        source = (Path(__file__).resolve().parents[1] / 'app.py').read_text(encoding='utf-8')
        start = source.index('science_closure = (')
        block = source[start:source.index('if subject == "Tin học"', start)]
        self.assertIn("'bậc ba' in", block)


if __name__ == '__main__':
    unittest.main()
