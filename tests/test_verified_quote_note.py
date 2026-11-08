import unittest
from services.socratic_context import label_verified_quote_translation as label


class VerifiedQuoteNoteTests(unittest.TestCase):
    row = dict(author='Khổng Tử', quote='Học rồi bền bỉ thực hành điều đã học, chẳng phải là điều vui sao?',
               source_url='https://classics.mit.edu/Confucius/analects.1.1.html',
               source_verified=True, translation_note='Diễn nghĩa tiếng Việt, không phải nguyên văn tiếng Việt của tác giả.')

    def test_exact_evidence_attaches_note_once_without_rewriting_lesson(self):
        reply = 'Bài học. Khổng Tử: ' + self.row['quote'] + ' ' + self.row['source_url']
        result = label(reply, [self.row])
        self.assertTrue(result.startswith(reply))
        self.assertIn(self.row['translation_note'], result)
        self.assertEqual(label(result, [self.row]), result)

    def test_no_certification_from_author_alone_or_unverified_metadata(self):
        self.assertEqual(label('Khổng Tử: câu chưa xác minh.', [self.row]), 'Khổng Tử: câu chưa xác minh.')
        reply = self.row['author'] + self.row['quote'] + self.row['source_url']
        self.assertEqual(label(reply, [dict(self.row, source_verified=False)]), reply)
