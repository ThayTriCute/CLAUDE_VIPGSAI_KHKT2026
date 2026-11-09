import unittest
from services.lesson_sources import reviewed_lesson_sources, apply_reviewed_content_corrections
from services.lab_scope import osmosis_lab_request, reviewed_workshop_request

TOPIC = 'Trao đổi nước và khoáng ở thực vật — Sinh học 11, KNTT, Bài 2'


class ReviewedPlantLessonTests(unittest.TestCase):
    def test_repairs_have_scope_and_preserve_other_grades(self):
        review = reviewed_lesson_sources('Sinh học', 11, TOPIC)
        self.assertEqual(review['status'], 'reviewed_requirements_source')
        self.assertIn('trang14', review['scope'])
        for rule in review['content_corrections']:
            repaired = apply_reviewed_content_corrections(rule['before'], 'Sinh học', 11, TOPIC)
            self.assertEqual(repaired, rule['after'])
            self.assertEqual(apply_reviewed_content_corrections(repaired, 'Sinh học', 11, TOPIC), repaired)
            self.assertEqual(apply_reviewed_content_corrections(rule['before'], 'Sinh học', 12, TOPIC), rule['before'])

    def test_water_energy_and_source_sink_misconceptions_are_repaired(self):
        review = reviewed_lesson_sources('Sinh học', 11, TOPIC)
        water = next(x for x in review['content_corrections'] if 'hút nước thụ động và chủ động' in x['before'])
        self.assertIn('không có cơ chế hút nước chủ động', water['after'])
        phloem = next(x for x in review['content_corrections'] if 'chênh lệch áp suất thẩm thấu' in x['before'])
        self.assertIn('áp suất thủy tĩnh', phloem['after'])
        self.assertIn('tùy nguồn–đích', phloem['after'])

    def test_configured_osmosis_uses_exact_sources_and_does_not_route_other_lessons(self):
        data = osmosis_lab_request('Mô phỏng thẩm thấu', 'Sinh học', 11, TOPIC)
        self.assertEqual(data['source_grade'], 11)
        self.assertIn('trang11–12', data['source_scope'])
        for subject, grade, topic in [('Sinh học', 12, TOPIC), ('Sinh học', 11, 'Bài khác'), ('Hóa học', 11, TOPIC)]:
            self.assertIsNone(osmosis_lab_request('thẩm thấu', subject, grade, topic))
        self.assertIsNone(osmosis_lab_request('Mô phỏng nitrogen', 'Sinh học', 11, TOPIC))

    def test_source_workshop_is_valid_without_api(self):
        data = reviewed_workshop_request('Đối chiếu tư liệu theo bài học', 'Sinh học', 11, TOPIC)
        self.assertEqual(len(data['workshop']['questions']), 3)
        self.assertEqual([x['correct'] for x in data['workshop']['questions']], [1, 2, 3])


if __name__ == '__main__':
    unittest.main()
