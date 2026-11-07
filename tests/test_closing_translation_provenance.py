import unittest
from services.socratic_context import repair_reviewed_station1_closing as repair


class ClosingTranslationProvenanceTests(unittest.TestCase):
    def test_checked_quote_labels_vietnamese_gloss_once_and_preserves_lesson(self):
        reply = ('Bài học trách nhiệm. Marcus Aurelius, Meditations VI: '
                 '"I seek the truth by which no man was ever injured" '
                 '(Tôi tìm kiếm sự thật, điều chưa từng làm hại ai - Nguồn: '
                 'https://classics.mit.edu/Antoninus/meditations.6.six.html). Lời chúc.')
        result = repair(reply, 'Em hiểu rồi.', 'Vật lý', 10, closing=True)
        self.assertIn('Diễn nghĩa tiếng Việt từ bản dịch tiếng Anh của George Long:', result)
        self.assertTrue(result.startswith('Bài học trách nhiệm.'))
        self.assertTrue(result.endswith('Lời chúc.'))
        self.assertEqual(repair(result, '', 'Vật lý', 10, closing=True), result)
        self.assertEqual(repair(reply, '', 'Vật lý', 10, closing=False), reply)

    def test_unknown_source_is_not_given_a_verified_translator(self):
        reply = 'Marcus Aurelius (Tôi tìm kiếm sự thật, điều chưa từng làm hại ai).'
        self.assertEqual(repair(reply, '', 'Vật lý', 10, closing=True), reply)
