import unittest

from services.curriculum_policy import correct_reviewed_english_family_guidance as repair


class ReviewedEnglishFamilyTests(unittest.TestCase):
    def test_reviewed_item_context_preserves_internal_key(self):
        source = (
            'In my family, my father usually __________ the heavy lifting, but today he __________ a rest.\n'
            'A. does / is taking\nD. does / takes\nCORRECT: A\n'
            'go to the market / visit her grandmother'
        )
        result = repair(source, 'Tiếng Anh', 10, 'Unit 1 Family life')
        self.assertIn('Right now', result)
        self.assertIn('visit her own mother', result)
        self.assertIn('A. does / is taking\nD. does / takes\nCORRECT: A', result)
        self.assertEqual(result, repair(result, 'Tiếng Anh', 10, 'Unit 1 Family life'))

    def test_quoted_code_and_other_contexts_stay_unchanged(self):
        source = '```text\nMy sister is cleaning her room every Sunday morning.\n```'
        self.assertEqual(source, repair(source, 'Tiếng Anh', 10, 'Family life'))
        for subject, grade, topic in [('Tiếng Anh', 11, 'Family life'),
                                      ('Ngữ văn', 10, 'Family life'),
                                      ('Tiếng Anh', 10, 'Ecotourism')]:
            prose = 'My sister is cleaning her room every Sunday morning.'
            self.assertEqual(prose, repair(prose, subject, grade, topic))


if __name__ == '__main__':
    unittest.main()
