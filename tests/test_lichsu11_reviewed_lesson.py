import unittest
from services.lesson_sources import reviewed_lesson_sources, apply_reviewed_content_corrections
from services.lab_scope import reviewed_workshop_request

TOPIC = 'Một số vấn đề chung về cách mạng tư sản — Lịch sử 11, KNTT, Bài 1'


class ReviewedHistoryLessonTests(unittest.TestCase):
    def test_source_repairs_are_idempotent_and_isolated(self):
        review = reviewed_lesson_sources('Lịch sử', 11, TOPIC)
        self.assertEqual(review['status'], 'reviewed_requirements_source')
        self.assertEqual(len(review['sources']), 4)
        for rule in review['content_corrections']:
            result = apply_reviewed_content_corrections(rule['before'], 'Lịch sử', 11, TOPIC)
            self.assertEqual(result, rule['after'])
            self.assertEqual(apply_reviewed_content_corrections(result, 'Lịch sử', 11, TOPIC), result)
            self.assertEqual(apply_reviewed_content_corrections(rule['before'], 'Lịch sử', 12, TOPIC), rule['before'])

    def test_ambiguous_force_question_gets_an_explicit_criterion(self):
        review = reviewed_lesson_sources('Lịch sử', 11, TOPIC)
        rule = next(x for x in review['content_corrections'] if x['before'].startswith('Trong các cuộc cách mạng tư sản thời cận đại, lực lượng'))
        self.assertIn('Bên cạnh giai cấp lãnh đạo', rule['after'])
        self.assertNotIn('CORRECT:', rule['after'])

    def test_level_repair_does_not_change_an_unrelated_essay(self):
        value = '**Câu 2. [Mức độ: VDC]**\nMột tình huống mới với yêu cầu khác.'
        self.assertEqual(apply_reviewed_content_corrections(value, 'Lịch sử', 11, TOPIC), value)

    def test_source_workshop_retains_evidence_limits(self):
        data = reviewed_workshop_request('Đối chiếu tư liệu theo bài học', 'Lịch sử', 11, TOPIC)
        self.assertEqual(len(data['workshop']['questions']), 3)
        self.assertIn('Không nghiệm thu toàn cuốn', data['workshop']['scope'])
        self.assertIsNone(reviewed_workshop_request('Đối chiếu tư liệu theo bài học', 'Lịch sử', 12, TOPIC))


if __name__ == '__main__':
    unittest.main()
