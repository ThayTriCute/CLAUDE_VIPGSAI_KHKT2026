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

    def test_time_words_do_not_substitute_for_explicit_example_context(self):
        source = (
            "Today, my mother (not/go) __________ to work; she (stay) __________ at home to celebrate my sister's birthday.\n"
            'I (take) __________ out the rubbish every night, but tonight my brother (do) __________ it for me.\n'
            '**Dấu hiệu nhận biết**'
        )
        result = repair(source, 'Tiếng Anh', 10, 'Unit 1 Family life')
        self.assertIn('My mother usually goes to work in the morning. Right now', result)
        self.assertIn('every night. Right now, my brother', result)
        self.assertNotIn('**Dấu hiệu nhận biết**', result)
        self.assertEqual(source, repair(source, 'Tiếng Anh', 11, 'Family life'))
        self.assertEqual(result, repair(result, 'Tiếng Anh', 10, 'Family life'))

    def test_quoted_code_and_other_contexts_stay_unchanged(self):
        source = '```text\nMy sister is cleaning her room every Sunday morning.\n```'
        self.assertEqual(source, repair(source, 'Tiếng Anh', 10, 'Family life'))
        for subject, grade, topic in [('Tiếng Anh', 11, 'Family life'),
                                      ('Ngữ văn', 10, 'Family life'),
                                      ('Tiếng Anh', 10, 'Ecotourism')]:
            prose = 'My sister is cleaning her room every Sunday morning.'
            self.assertEqual(prose, repair(prose, subject, grade, topic))


class ParsedEnglishFamilyTests(unittest.TestCase):
    def test_existing_parsed_quiz_is_repaired_without_mutating_key_or_source(self):
        from copy import deepcopy
        from services.curriculum_policy import repair_reviewed_english_family_question
        original = {'question': 'Which sentence describes a household routine?',
                    'options': ['A. My sister clean her room.',
                                'B. My sister is cleaning her room every Sunday morning.',
                                'C. My sister are cleaning her room.',
                                'D. My sister cleans her room every Sunday morning.'],
                    'correct': 'D', 'level': 'VD', 'cognitive_evidence': {'review': 'pending'}}
        before = deepcopy(original)
        fixed = repair_reviewed_english_family_question(original, 'Tiếng Anh', 10, 'Family life')
        self.assertEqual(original, before)
        self.assertEqual(fixed['options'][1], 'B. My sister is clean her room every Sunday morning.')
        self.assertEqual(fixed['correct'], 'D')
        self.assertEqual(fixed['level'], 'VD')  # Never self-certify cognitive level.
        self.assertEqual(fixed['cognitive_evidence'], original['cognitive_evidence'])
        self.assertEqual(fixed, repair_reviewed_english_family_question(fixed, 'Tiếng Anh', 10, 'Family life'))
        self.assertEqual(original, repair_reviewed_english_family_question(original, 'Ngữ văn', 10, 'Family life'))


if __name__ == '__main__':
    unittest.main()
