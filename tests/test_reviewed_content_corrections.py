import unittest
from unittest.mock import patch
from services.lesson_sources import apply_reviewed_content_corrections, reviewed_lesson_sources

TOPIC = 'Trao đổi chất qua màng tế bào — Sinh học 10, KNTT, Bài 10'


class ReviewedContentCorrectionTests(unittest.TestCase):
    def test_exact_stem_level_revision_stays_a_proposal_and_keeps_keys(self):
        from services.lesson_sources import apply_reviewed_quiz_proposal
        from services.cognitive_levels import level_caption
        review=reviewed_lesson_sources('Sinh học',10,TOPIC)
        stem=next(r['before'] for r in review['content_corrections'] if r['before'].startswith('Sự vận chuyển glucose'))
        original=dict(question=stem,level='VD',correct='B',options=['a','b','c','d'])
        fixed=apply_reviewed_quiz_proposal(original,'Sinh học',10,TOPIC)
        self.assertEqual(fixed['level'],'TH')
        self.assertEqual(fixed['level_claimed'],'VD')
        self.assertEqual(original['level'],'VD')
        self.assertEqual(fixed['correct'],original['correct'])
        self.assertEqual(fixed['options'],original['options'])
        self.assertIn('chưa duyệt',level_caption(fixed))
        self.assertEqual(fixed,apply_reviewed_quiz_proposal(fixed,'Sinh học',10,TOPIC))
        for subject,grade,topic in [('Sinh học',11,TOPIC),('Hóa học',10,TOPIC),('Sinh học',10,'Khác')]:
            self.assertEqual(original,apply_reviewed_quiz_proposal(original,subject,grade,topic))

    def test_actual_glucose_counterexample_has_required_conditions(self):
        review = reviewed_lesson_sources('Sinh học', 10, TOPIC)
        rule = next(x for x in review['content_corrections'] if x['before'].startswith('Sự vận chuyển glucose'))
        original = rule['before'] + '\nA. Đơn giản\nB. Tăng cường\nCORRECT: B'
        fixed = apply_reviewed_content_corrections(original, 'Sinh học', 10, TOPIC)
        self.assertIn('không ghép với gradient ion', fixed)
        self.assertIn('CORRECT: B', fixed)
        self.assertEqual(fixed, apply_reviewed_content_corrections(fixed, 'Sinh học', 10, TOPIC))
        for subject, grade, topic in [('Sinh học', 11, TOPIC), ('Hóa học', 10, TOPIC),
                                      ('Sinh học', 10, 'Bài khác')]:
            self.assertEqual(original, apply_reviewed_content_corrections(original, subject, grade, topic))

    def test_history_source_repairs_keep_quiz_keys_and_exact_topic_scope(self):
        import re
        topic = 'Hiện thực lịch sử và lịch sử được con người nhận thức — Lịch sử 10, KNTT, Bài 1'
        review = reviewed_lesson_sources('Lịch sử', 10, topic)
        rules = review['content_corrections']
        original = '\n'.join(r['before'] for r in rules) + '\nCORRECT: C\nCORRECT: B\nCORRECT: C'
        fixed = apply_reviewed_content_corrections(original, 'Lịch sử', 10, topic)
        self.assertEqual(re.findall(r'CORRECT: ([A-D])', fixed), ['C', 'B', 'C'])
        self.assertIn('**Sử học:**', fixed)
        self.assertIn('**Chức năng của Sử học:**', fixed)
        self.assertIn('**Nhiệm vụ của Sử học:**', fixed)
        self.assertNotIn('một bên coi Ma-gien-lăng là người có công truyền bá văn minh', fixed)
        self.assertNotIn('tấm bia phía Tây Ban Nha', fixed)
        self.assertNotIn('bãi cọc Cao Quỳ', fixed)
        self.assertEqual(fixed, apply_reviewed_content_corrections(fixed, 'Lịch sử', 10, topic))
        for subject, grade, other_topic in [('Lịch sử', 11, topic), ('Ngữ văn', 10, topic),
                                            ('Lịch sử', 10, 'Bài khác')]:
            self.assertEqual(original, apply_reviewed_content_corrections(original, subject, grade, other_topic))

    def test_explicit_corrections_preserve_code_and_require_review(self):
        review = dict(status='reviewed_requirements_source', content_corrections=[
            dict(before='Sai điều kiện', after='Đủ điều kiện', reason='Source-backed')])
        value = 'Sai điều kiện `Sai điều kiện`\n```python\nSai điều kiện\n```\n<svg>Sai điều kiện</svg>'
        with patch('services.lesson_sources.reviewed_lesson_sources', return_value=review):
            fixed = apply_reviewed_content_corrections(value, 'Toán học', 12, 'Fixture')
        self.assertTrue(fixed.startswith('Đủ điều kiện `Sai điều kiện`'))
        self.assertIn('```python\nSai điều kiện\n```', fixed)
        self.assertIn('<svg>Sai điều kiện</svg>', fixed)
        with patch('services.lesson_sources.reviewed_lesson_sources', return_value=dict(status='missing_lesson_review')):
            self.assertEqual(value, apply_reviewed_content_corrections(value, 'Toán học', 12, 'Fixture'))


if __name__ == '__main__':
    unittest.main()
