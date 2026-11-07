import unittest
from services.curriculum_policy import correct_reviewed_horizontal_throw as repair


class ReviewedHorizontalThrowTests(unittest.TestCase):
    topic = 'Chuyển động ném ngang — Vật lí 10, KNTT, Bài 12 mục I'

    def test_scope_and_idempotence(self):
        raw = 'Chuyển động ném ngang là chuyển động của một vật có vận tốc ban đầu theo phương nằm ngang và sau đó chỉ chịu tác dụng của trọng lực.'
        fixed = repair(raw, 'Vật lý', 10, self.topic)
        self.assertIn('0 ≤ t ≤ T', fixed)
        self.assertEqual(repair(fixed, 'Vật lý', 10, self.topic), fixed)
        self.assertEqual(repair(raw, 'Vật lý', 11, self.topic), raw)
        self.assertEqual(repair(raw, 'Vật lý', 10, 'Bài khác'), raw)

    def test_no_answer_or_code_changes(self):
        raw = 'CORRECT: B\nEXPLAIN: $T = 2$\n```python\nprint(42)\n```'
        self.assertEqual(repair(raw, 'Vật lý', 10, self.topic), raw)
