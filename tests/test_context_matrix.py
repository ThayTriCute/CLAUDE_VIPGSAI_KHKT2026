"""All supported contexts; these tests do not certify subject knowledge."""
import json
import html
import unittest
from urllib.parse import unquote_plus, urlparse

from services.academic_context import subjects_for_grade, academic_context, validate_exam_context
from services.curriculum_policy import lesson_prompt, exam_prompt, validate_exam_structure
from services.lesson_sources import books_for, lesson_references
from data.socratic_anchors import safe_json_loads


CONTEXTS = [(subject, grade) for grade in range(6, 13) for subject in subjects_for_grade(grade)]


class TestContextMatrix(unittest.TestCase):
    def test_supported_matrix_has_65_distinct_contexts(self):
        self.assertEqual(len(CONTEXTS), 65)
        self.assertEqual(len(set(CONTEXTS)), 65)

    def test_prompts_and_schema_keep_each_context(self):
        for subject, grade in CONTEXTS:
            with self.subTest(subject=subject, grade=grade):
                lesson = lesson_prompt(subject, grade, 'CHỦ_ĐỀ_KIỂM_THỬ')
                self.assertIn(f'môn {subject}; lớp {grade};', lesson)
                prompt = exam_prompt(subject, grade, ['CHỦ_ĐỀ_KIỂM_THỬ'], (1, 0, 0), 'QA')
                schema = json.loads(prompt[prompt.rfind('\n{') + 1:])
                self.assertEqual((schema['subject'], schema['grade']), (subject, grade))
                self.assertIn('CHỦ_ĐỀ_KIỂM_THỬ', prompt)

    def test_reference_navigation_keeps_subject_and_grade(self):
        for subject, grade in CONTEXTS:
            with self.subTest(subject=subject, grade=grade):
                references = lesson_references(subject, grade, 'CHỦ_ĐỀ_KIỂM_THỬ', {}, lambda url: '')
                query = unquote_plus(references['yt_deep_url'])
                self.assertIn(f'{subject} lớp {grade}', query)
                self.assertIn(f'{subject} · Lớp {grade}', html.unescape(references['badge_html']))
                for book in books_for(subject, grade):
                    self.assertTrue(book['title'])
                    self.assertIn(urlparse(book['url']).scheme, ('http', 'https'))
                    self.assertTrue(urlparse(book['url']).hostname)

    def test_structural_json_roundtrip_preserves_all_subjects(self):
        for subject, grade in CONTEXTS:
            with self.subTest(subject=subject, grade=grade):
                question = {'q': 'Ngữ liệu mô phỏng chỉ kiểm tra cấu trúc, không phải câu đánh giá kiến thức.',
                            'opt': ['A. lựa chọn một', 'B. lựa chọn hai', 'C. lựa chọn ba', 'D. lựa chọn bốn'], 'ans': 'B'}
                exam = {'subject': subject, 'grade': grade, 'p1': [question]}
                if subject == 'Ngữ văn':
                    exam = {'subject': subject, 'grade': grade,
                            'part_doc_hieu': {'text': 'Đoạn văn mô phỏng kiểm thử.', 'questions': [{'q': 'Câu mô phỏng.'}]},
                            'part_viet': [{'q': 'Đề viết mô phỏng.'}]}
                restored = safe_json_loads('```json\n' + json.dumps(exam, ensure_ascii=False))
                self.assertEqual(restored, exam)
                self.assertEqual(validate_exam_context(restored, subject, grade), (subject, grade))
                validate_exam_structure(restored, subject)

    def test_wrong_grade_and_subject_are_rejected_for_every_context(self):
        for subject, grade in CONTEXTS:
            with self.subTest(subject=subject, grade=grade):
                wrong_grade = 11 if grade == 12 else grade + 1
                with self.assertRaises(ValueError):
                    validate_exam_context({'subject': subject, 'grade': wrong_grade}, subject, grade)
                other = next(value for value in subjects_for_grade(grade) if value != subject)
                with self.assertRaises(ValueError):
                    validate_exam_context({'p1': [{'q': 'Dữ liệu', 'subject': other}]}, subject, grade)

    def test_middle_school_integrated_subjects_do_not_become_standalone_physics(self):
        for grade in range(6, 10):
            with self.assertRaises(ValueError):
                academic_context('Vật lý', grade)
            self.assertEqual(academic_context('KHTN', grade), ('Khoa học tự nhiên', grade))
