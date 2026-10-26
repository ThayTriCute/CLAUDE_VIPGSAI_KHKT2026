"""Exercise publication and bounded repair in all 65 contexts, without paid AI.

Synthetic payloads check contracts, routing and rendering, not textbook accuracy.
"""
from copy import deepcopy
import hashlib
import html
import json
import unittest

from services.academic_context import subjects_for_grade, validate_exam_context
from services.curriculum_policy import (validate_lesson_policy, validate_exam_structure,
    prepare_exam_for_delivery, lesson_prompt)
from services.lesson_contract import validate_lesson_contract, student_polya
from services.lesson_export import build_lesson_html, faithful_infographic_data
from services.math_publication import generate_checked_text, math_for_web, native_radio_label
from services.context_recovery import repair_exam_context
from tests.lesson_samples import complete_lesson


CONTEXTS = [(subject, grade) for grade in range(6, 13) for subject in subjects_for_grade(grade)]


def sample_exam(subject, grade):
    """Deliberately neutral QA content; never label this academic verification."""
    common = {'subject': subject, 'grade': grade, 'topic': 'Kiểm thử phần mềm',
              'level': '', 'q': 'Trong dữ liệu kiểm thử, chọn nhãn thứ hai.',
              'opt': ['A. nhãn một', 'B. nhãn hai', 'C. nhãn ba', 'D. nhãn bốn'], 'ans': 'B'}
    exam = {'subject': subject, 'grade': grade, 'textbook': 'KNTT'}
    if subject == 'Ngữ văn':
        exam.update(part_doc_hieu={'text': 'Đoạn văn mô phỏng để kiểm thử phần mềm.',
            'questions': [{'q': 'Nêu mục đích của đoạn văn mô phỏng.', 'ans': 'Kiểm thử.'}]},
            part_viet=[{'q': 'Viết một đoạn văn mô phỏng phục vụ kiểm thử.', 'ans': 'Rubric QA.'}])
    else:
        exam.update(p1=[common], p2=[{'q': 'Xét các nhãn kiểm thử.',
            'stmts': [{'t': f'Mệnh đề kiểm thử {i}.', 'a': i % 2 == 0} for i in range(4)]}],
            p3=[{'q': 'Có bao nhiêu nhãn trong dữ liệu kiểm thử?', 'ans': '4'}])
    return exam


class TestAllContextPublication(unittest.TestCase):
    def test_lesson_input_examples_follow_each_grade_instead_of_grade12_fallback(self):
        from data.curriculum_data import BIGDATA_CURRICULUM
        from services.curriculum_policy import lesson_topic_placeholder
        for subject, grade in CONTEXTS:
            with self.subTest(subject=subject, grade=grade):
                topics = BIGDATA_CURRICULUM.get(subject, {}).get(grade, [])
                value = lesson_topic_placeholder(subject, grade, topics)
                self.assertIn(f'lớp {grade}', value)
                if topics:
                    self.assertIn(topics[0].split(':', 1)[-1].strip(), value)
                self.assertIn(subject, lesson_topic_placeholder(subject, grade, []))
        self.assertNotIn('Life stories', lesson_topic_placeholder('Anh', 6, BIGDATA_CURRICULUM['Tiếng Anh'][6]))

    def test_station1_policy_conflicts_receive_one_repair_in_every_context(self):
        for subject, grade in CONTEXTS:
            with self.subTest(subject=subject, grade=grade):
                wrong_subject = next(s for s in subjects_for_grade(grade) if s != subject)
                wrong_grade = 11 if grade == 12 else grade + 1
                good = complete_lesson(f'Môn: {subject}; lớp: {grade}\nNgữ liệu mô phỏng kiểm thử, không phải bài học được thẩm định.')
                for declaration in (f'Môn: {wrong_subject}; lớp: {grade}',
                                    f'Môn: {subject}; lớp: {wrong_grade}'):
                    bad = good.replace(f'Môn: {subject}; lớp: {grade}', declaration)
                    calls = []
                    def generator(prompt):
                        calls.append(prompt)
                        return bad if len(calls) == 1 else good
                    def validate(text):
                        return validate_lesson_contract(validate_lesson_policy(text, subject, grade), subject, grade)
                    self.assertEqual(generate_checked_text(lesson_prompt(subject, grade, 'Kiểm thử'), generator, validate), good)
                    self.assertEqual(len(calls), 2)
                    self.assertIn(declaration, bad)  # rejected input remains untouched

    def test_station1_export_retains_source_context_and_polya_for_every_context(self):
        for subject, grade in CONTEXTS:
            with self.subTest(subject=subject, grade=grade):
                theory = f'Môn: {subject}; lớp: {grade}\nQA-{grade}-{subject}: văn bản mô phỏng. Công thức thử $\\frac{{1}}{{2}}$.'
                lesson = complete_lesson(theory)
                validated = validate_lesson_contract(validate_lesson_policy(lesson, subject, grade), subject, grade)
                polya = student_polya(validated, subject, grade)
                self.assertEqual(polya.count('Bước 1: Tìm hiểu đề'), 2)
                self.assertEqual(polya.count('Bước 4: Kiểm tra và nhìn lại'), 2)
                output = build_lesson_html(subject, grade, 'Kiểm thử', theory)
                self.assertIn(html.escape(f'{subject} · Lớp {grade}'), output)
                self.assertIn(hashlib.sha256(theory.encode()).hexdigest(), output)
                self.assertNotIn('data-source-issue=', output)
                data = faithful_infographic_data(subject, grade, 'Kiểm thử', theory)
                self.assertEqual(data['source_sha256'], hashlib.sha256(theory.encode()).hexdigest())
                self.assertEqual(data['example']['visual_svg'], '')
                self.assertIn('katex', math_for_web(theory))

    def test_station3_valid_payload_and_source_preserved_for_every_context(self):
        for subject, grade in CONTEXTS:
            with self.subTest(subject=subject, grade=grade):
                source = sample_exam(subject, grade)
                before = deepcopy(source)
                result = prepare_exam_for_delivery(source, subject, grade)
                self.assertEqual(source, before)
                self.assertEqual((result['subject'], result['grade']), (subject, grade))
                self.assertFalse(result['curriculum_audit']['academic_verified'])
                for part in ('p1', 'p2', 'p3', 'part_doc_hieu', 'part_viet'):
                    if part in source:
                        # Level audit may add evidence, never change the task/key.
                        if isinstance(source[part], list):
                            for old, new in zip(source[part], result[part]):
                                for field in ('q', 'opt', 'ans', 'stmts'):
                                    if field in old:
                                        self.assertEqual(new[field], old[field])
                        else:
                            self.assertEqual(result[part]['text'], source[part]['text'])

    def test_station3_malformed_sections_rejected_for_every_context(self):
        for subject, grade in CONTEXTS:
            for part in ('p1', 'p2', 'p3', 'part_viet'):
                with self.subTest(subject=subject, grade=grade, part=part):
                    invalid = sample_exam(subject, grade)
                    invalid[part] = {'q': 'Không phải danh sách câu hỏi.'}
                    with self.assertRaises(ValueError):
                        prepare_exam_for_delivery(invalid, subject, grade)

    def test_reading_context_and_empty_reading_are_not_skipped(self):
        for grade in range(6, 13):
            with self.subTest(grade=grade):
                wrong = sample_exam('Ngữ văn', grade)
                wrong['part_doc_hieu']['grade'] = 11 if grade == 12 else grade+1
                with self.assertRaises(ValueError):
                    validate_exam_context(wrong, 'Ngữ văn', grade)
                for text, questions in (('   ', [{'q': 'Câu hỏi'}]), ('Đoạn văn', 'sai kiểu'), ('Đoạn văn', [])):
                    invalid = sample_exam('Ngữ văn', grade)
                    invalid['part_doc_hieu'].update(text=text, questions=questions)
                    with self.assertRaises(ValueError):
                        validate_exam_structure(invalid, 'Ngữ văn')

    def test_explicit_other_textbook_rejected_but_quoted_comparison_allowed(self):
        for subject, grade in CONTEXTS:
            with self.subTest(subject=subject, grade=grade):
                with self.assertRaises(ValueError):
                    validate_lesson_policy('Bộ sách: Cánh Diều\nNgữ liệu mô phỏng.', subject, grade)
                allowed = 'Tham khảo cách trình bày ở Cánh Diều để so sánh, không khai báo dùng bộ sách đó.'
                self.assertEqual(validate_lesson_policy(allowed, subject, grade), allowed)
                wrong = sample_exam(subject, grade)
                if subject == 'Ngữ văn':
                    wrong['part_doc_hieu']['textbook'] = 'Chân trời sáng tạo'
                else:
                    wrong['p1'][0]['textbook'] = 'Chân trời sáng tạo'
                with self.assertRaises(ValueError):
                    prepare_exam_for_delivery(wrong, subject, grade)

    def test_policy_repair_does_not_loop_forever_or_swallow_provider_errors(self):
        subject, grade = 'Toán học', 6
        calls = []
        def generator(prompt):
            calls.append(prompt)
            return complete_lesson('Môn: Toán học; lớp: 99')
        with self.assertRaises(ValueError):
            generate_checked_text(lesson_prompt(subject, grade, 'Kiểm thử'), generator,
                lambda text: validate_lesson_policy(text, subject, grade))
        self.assertEqual(len(calls), 2)
        with self.assertRaisesRegex(RuntimeError, 'provider unavailable'):
            generate_checked_text('QA', lambda _: (_ for _ in ()).throw(RuntimeError('provider unavailable')),
                lambda text: text)

    def test_station3_whole_question_repair_and_budget_for_all_non_literature_contexts(self):
        for subject, grade in CONTEXTS:
            if subject == 'Ngữ văn':
                continue  # Passage + rubric must be replaced atomically elsewhere.
            with self.subTest(subject=subject, grade=grade):
                good = sample_exam(subject, grade)['p1'][0]
                bad = deepcopy(good)
                bad.pop('ans')
                source = {'p1': [bad]}
                before = deepcopy(source)
                calls = []
                def generator(prompt):
                    calls.append(prompt)
                    return json.dumps({'replacement_question': good}, ensure_ascii=False)
                result = repair_exam_context(source, subject, grade, [good['topic']], ai_generator=generator)
                self.assertEqual(source, before)
                self.assertEqual(len(calls), 1)
                self.assertEqual(result['context_recovery']['unresolved'], 0)
                self.assertEqual(result['p1'][0]['ans'], good['ans'])
                self.assertFalse(result['p1'][0]['replacement_audit']['academic_verified'])
                self.assertEqual(result['p1'][0]['replacement_audit']['origin'], 'ai_replacement')
                blocked = repair_exam_context(source, subject, grade, [good['topic']],
                    ai_generator=lambda _: {'replacement_question': bad}, max_ai_questions=2)
                self.assertEqual(blocked['context_recovery']['ai_calls'], 2)
                self.assertEqual(blocked['context_recovery']['unresolved'], 1)

    def test_empty_or_duplicate_options_are_rejected_in_every_mcq_context(self):
        for subject, grade in CONTEXTS:
            if subject == 'Ngữ văn':
                continue
            for options in (['A. ', 'B. hai', 'C. ba', 'D. bốn'],
                            ['A. một', 'B. một', 'C. ba', 'D. bốn'],
                            [{'text': 'một'}, 'B. hai', 'C. ba', 'D. bốn']):
                with self.subTest(subject=subject, grade=grade, options=options):
                    exam = sample_exam(subject, grade)
                    exam['p1'][0]['opt'] = options
                    with self.assertRaises(ValueError):
                        validate_exam_structure(exam, subject)

    def test_notation_is_rendered_without_replacing_science_or_code(self):
        for text in (r'$\ce{2H2 + O2 -> 2H2O}$', r'$\omega=2\pi f$',
                     r'$\frac{a}{b}$', 'English word /ˈlɜːnɪŋ/', '`a[i] < target`',
                     r'$\pu{9.8 m s-2}$'):
            with self.subTest(text=text):
                self.assertTrue(math_for_web(text))
                self.assertTrue(native_radio_label(text))

    def test_case_sensitive_scientific_and_language_options_remain_distinct(self):
        options = [r'$\ce{CO}$', r'$\ce{Co}$', '`"A"`', '`"a"`']
        for subject, grade in CONTEXTS:
            with self.subTest(subject=subject, grade=grade):
                lesson = complete_lesson(chemistry=True)
                for old, new in zip([r'$\ce{H2O}$', r'$\ce{CO2}$', r'$\ce{O2}$', r'$\ce{N2}$'], options):
                    lesson = lesson.replace(old, new)
                validate_lesson_contract(lesson, subject, grade)
                exam = sample_exam(subject, grade)
                if subject != 'Ngữ văn':
                    exam['p1'][0]['opt'] = [f'{chr(65+i)}. {value}' for i, value in enumerate(options)]
                    validate_exam_structure(exam, subject)

    def test_other_textbook_question_is_repaired_atomically_before_delivery(self):
        for subject, grade in CONTEXTS:
            if subject == 'Ngữ văn':
                continue
            with self.subTest(subject=subject, grade=grade):
                good = sample_exam(subject, grade)['p1'][0]
                wrong = dict(good, textbook='Cánh Diều')
                result = repair_exam_context({'p1': [wrong]}, subject, grade, [good['topic']],
                    ai_generator=lambda _: {'replacement_question': good})
                self.assertEqual(result['context_recovery']['unresolved'], 0)
                self.assertEqual(result['context_recovery']['ai_calls'], 1)
                self.assertEqual(result['p1'][0]['replacement_audit']['reason'], 'conflicting_textbook_declaration')
                prepare_exam_for_delivery(result, subject, grade)
