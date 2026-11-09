import unittest
from services.lesson_sources import reviewed_lesson_sources, apply_reviewed_content_corrections
from services.lab_scope import reviewed_workshop_request

TOPIC = 'Sự khác biệt về trình độ phát triển kinh tế – xã hội của các nhóm nước — Địa lí 11, KNTT, Bài 1'


class ReviewedGeographyLessonTests(unittest.TestCase):
    def test_repairs_match_source_scope_and_leave_other_grades_alone(self):
        review = reviewed_lesson_sources('Địa lý', 11, TOPIC)
        self.assertEqual(review['status'], 'reviewed_requirements_source')
        for rule in review['content_corrections']:
            result = apply_reviewed_content_corrections(rule['before'], 'Địa lý', 11, TOPIC)
            self.assertEqual(result, rule['after'])
            self.assertEqual(apply_reviewed_content_corrections(result, 'Địa lý', 11, TOPIC), result)
            self.assertEqual(apply_reviewed_content_corrections(rule['before'], 'Địa lý', 12, TOPIC), rule['before'])

    def test_service_share_claim_uses_reviewed_data_not_invented_threshold(self):
        review = reviewed_lesson_sources('Địa lý', 11, TOPIC)
        rule = next(x for x in review['content_corrections'] if 'thường trên' in x['before'])
        self.assertIn('63.3%', rule['after'])
        self.assertIn('69.5%', rule['after'])
        self.assertNotIn('CORRECT:', rule['after'])

    def test_hdi_classification_is_not_the_country_group_rule(self):
        review = reviewed_lesson_sources('Địa lý', 11, TOPIC)
        rule = next(x for x in review['content_corrections'] if x['before'].startswith('Dựa vào kiến thức đã học, em hãy xác định mỗi quốc gia'))
        self.assertIn('không đồng nhất', rule['after'])

    def test_source_workshop_keeps_units_and_answer_order(self):
        data = reviewed_workshop_request('Đối chiếu tư liệu theo bài học', 'Địa lý', 11, TOPIC)
        self.assertEqual([x['correct'] for x in data['workshop']['questions']], [0, 1, 2])
        self.assertIsNone(reviewed_workshop_request('Đối chiếu tư liệu theo bài học', 'Địa lý', 12, TOPIC))


if __name__ == '__main__':
    unittest.main()
