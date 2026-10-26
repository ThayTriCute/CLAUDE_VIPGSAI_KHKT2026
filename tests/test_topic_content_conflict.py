"""Regression for the live grouped-data question mislabeled as function survey."""
import copy
import unittest
from unittest.mock import patch

from services.academic_scope import AcademicScopeError, check_exam_question_scope
from services.context_recovery import repair_exam_context
from services.curriculum_policy import prepare_exam_for_delivery


class TestTopicContentConflict(unittest.TestCase):
    topic = 'Khảo sát và vẽ đồ thị hàm số'

    def question(self):
        return {'subject': 'Toán học', 'grade': 12, 'topic': self.topic,
                'q': 'Khảo sát thời gian tự học của 50 học sinh. Khoảng biến thiên của mẫu số liệu ghép nhóm bằng:',
                'mslgn_data': {'groups': ['[30;45)', '[45;60)'], 'freq': [20, 30]},
                'opt': ['A. 30', 'B. 15', 'C. 45', 'D. 60'], 'ans': 'A'}

    def test_false_survey_label_cannot_override_grouped_statistics_task(self):
        with self.assertRaises(AcademicScopeError):
            check_exam_question_scope(self.question(), 'Toán', 12, [self.topic])

    def test_final_publication_catches_the_same_mislabeled_source(self):
        with self.assertRaises(AcademicScopeError):
            prepare_exam_for_delivery({'p1': [self.question()]}, 'Toán', 12, topics=[self.topic])

    def test_actual_statistics_and_combined_function_tasks_are_preserved(self):
        q = self.question()
        q['topic'] = 'Các số đặc trưng đo mức độ phân tán - Mẫu số liệu ghép nhóm'
        self.assertEqual(check_exam_question_scope(q, 'Toán', 12, [q['topic']]), q)
        q = self.question()
        q['q'] += ' Dùng đạo hàm khảo sát hàm số mô hình.'
        self.assertEqual(check_exam_question_scope(q, 'Toán', 12, [self.topic]), q)
        self.assertEqual(check_exam_question_scope(self.question(), 'Tiếng Anh', 12, [self.topic]), self.question())

    def test_rule_does_not_leak_across_the_65_subject_grade_contexts(self):
        from services.academic_context import subjects_for_grade
        from services.academic_scope import check_topic_content_consistency
        count = 0
        for grade in range(6, 13):
            for subject in subjects_for_grade(grade):
                count += 1
                q = self.question()
                if subject == 'Toán học':
                    q['topic'] = 'Thống kê mẫu số liệu ghép nhóm'
                with self.subTest(subject=subject, grade=grade):
                    self.assertEqual(check_topic_content_consistency(q, subject), q)
        self.assertEqual(count, 65)

    def test_complete_replacement_uses_existing_recovery_without_mutating_source(self):
        q = self.question()
        original = copy.deepcopy(q)
        replacement = {'subject': 'Toán học', 'grade': 12, 'topic': self.topic,
                       'q': 'Cho hàm số $y=x^3-3x$. Tính đạo hàm tại $x=0$.',
                       'opt': ['A. -3', 'B. 0', 'C. 1', 'D. 3'], 'ans': 'A'}
        calls = []
        def generate(prompt):
            calls.append(prompt)
            return {'replacement_question': replacement}
        # Keep the visual-reading task when repairing the original grouped table.
        replacement['f'] = {'type': 'func_3', 'a': 1, 'b': 0, 'c': -3, 'd': 0}
        result = repair_exam_context({'p1': [q]}, 'Toán', 12, [self.topic], ai_generator=generate,
                                    scope_validator=lambda item: check_exam_question_scope(item, 'Toán', 12, [self.topic]))
        self.assertEqual(q, original)
        self.assertEqual(result['p1'][0]['q'], replacement['q'])
        self.assertEqual(result['p1'][0]['opt'], replacement['opt'])
        self.assertEqual(result['context_recovery']['unresolved'], 0)
        self.assertEqual(len(calls), 1)

    def test_initial_bank_selection_does_not_keep_the_corrupt_label(self):
        import real_exam_engine as engine
        with patch.object(engine, 'get_baseline_questions_pool', return_value={'p1': [self.question()], 'p2': [], 'p3': []}):
            result = engine.generate_blended_real_exam('Toán học', 12, [self.topic], (1, 0, 0))
        self.assertFalse(result and result.get('p1'))
