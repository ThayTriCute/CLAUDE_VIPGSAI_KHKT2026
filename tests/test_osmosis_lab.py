import unittest
from services.lab_scope import osmosis_state, osmosis_lab_request

TOPIC = 'Trao đổi chất qua màng tế bào — Sinh học 10, KNTT, Bài 10'


class OsmosisLabTests(unittest.TestCase):
    def test_gradient_reversal_and_dynamic_balance(self):
        self.assertEqual(osmosis_state(300, 150)['direction'], 'inward')
        self.assertEqual(osmosis_state(300, 450)['direction'], 'outward')
        balanced = osmosis_state(300, 300)
        self.assertEqual(balanced['direction'], 'balanced')
        self.assertTrue(balanced['bidirectional_exchange'])
        self.assertIn('hai chiều', balanced['result'])
        for value in (-1, float('nan'), float('inf')):
            with self.assertRaises(ValueError):
                osmosis_state(value, 300)

    def test_wall_changes_outcome_without_fabricated_threshold(self):
        self.assertIn('vỡ tùy điều kiện', osmosis_state(300, 150)['result'])
        self.assertIn('áp suất', osmosis_state(300, 150, True)['result'])
        self.assertIn('không gọi là co nguyên sinh', osmosis_state(300, 450)['result'])
        self.assertIn('màng tách khỏi thành', osmosis_state(300, 450, True)['result'])

    def test_only_explicit_reviewed_lesson_is_routed(self):
        self.assertEqual(osmosis_lab_request('Mô phỏng thẩm thấu', 'Sinh học', 10, TOPIC)['type'], 'bio_osmosis')
        for command, subject, grade, topic in [
            ('Phân bào', 'Sinh học', 10, TOPIC),
            ('thẩm thấu', 'Sinh học', 11, TOPIC),
            ('thẩm thấu', 'Hóa học', 10, TOPIC),
            ('thẩm thấu', 'Sinh học', 10, 'Bài khác')]:
            self.assertIsNone(osmosis_lab_request(command, subject, grade, topic))


if __name__ == '__main__':
    unittest.main()
