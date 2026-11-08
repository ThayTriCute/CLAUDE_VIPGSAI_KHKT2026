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

    def test_civic_review_repairs_rule_characteristic_confusion_without_changing_keys(self):
        topic='Khái niệm, đặc điểm và vai trò của pháp luật — GDKT&PL 10, KNTT, Bài 11'
        review=reviewed_lesson_sources('Giáo dục kinh tế và pháp luật',10,topic)
        rule=next(r for r in review['content_corrections'] if r['before'].startswith('*Tình huống:* Anh A'))
        value=rule['before']+'\nCORRECT: D\nCORRECT: B\nCORRECT: C'
        fixed=apply_reviewed_content_corrections(value,'Giáo dục kinh tế và pháp luật',10,topic)
        self.assertIn('không phải “vi phạm một đặc điểm”',fixed)
        self.assertTrue(fixed.endswith('CORRECT: D\nCORRECT: B\nCORRECT: C'))
        self.assertEqual(fixed,apply_reviewed_content_corrections(fixed,'Giáo dục kinh tế và pháp luật',10,topic))
        for subject,grade in [('Lịch sử',10),('Giáo dục kinh tế và pháp luật',11)]:
            self.assertEqual(value,apply_reviewed_content_corrections(value,subject,grade,topic))

    def test_geography_repairs_scope_clock_data_and_keep_shuffled_key(self):
        from services.lesson_sources import apply_reviewed_quiz_proposal
        topic='Hệ quả địa lí các chuyển động của Trái Đất — Địa lí 10, KNTT, Bài 5'
        review=reviewed_lesson_sources('Địa lý',10,topic)
        option=next(r for r in review['content_corrections'] if r['before'].startswith('C. Do độ nghiêng'))
        q=dict(question='Why?',options=['A. Other','B. '+option['before'][3:],'C. Other','D. Other'],correct='B')
        fixed=apply_reviewed_quiz_proposal(q,'Địa lý',10,topic)
        self.assertEqual(fixed['correct'],'B');self.assertEqual(fixed['options'][1],'B. '+option['after'][3:])
        self.assertEqual(q['options'][1],'B. '+option['before'][3:])
        for rule in review['content_corrections']:
            if 'Tân Sơn Nhất' in rule['before'] and 'Hà Nội' in rule['before']:
                value=apply_reviewed_content_corrections(rule['before'],'Địa lý',10,topic)
                self.assertIn('TP.Hồ Chí Minh',value)
                self.assertEqual(value,apply_reviewed_content_corrections(value,'Địa lý',10,topic))
                self.assertEqual(rule['before'],apply_reviewed_content_corrections(rule['before'],'Địa lý',11,topic))
        stem=review['assessment_proposals'][0]['question']
        q=dict(question=stem,correct='B',options=['A','B','C','D'],level='TH')
        result=apply_reviewed_quiz_proposal(q,'Địa lý',10,topic)
        self.assertEqual(result['level'],'NB');self.assertEqual(result['level_claimed'],'TH')
        self.assertEqual(result['options'],q['options']);self.assertEqual(result['correct'],'B')

    def test_reviewed_tutor_keeps_distinct_event_locations_and_live_replay_share_rule(self):
        import ast
        from pathlib import Path
        topic='Hiện thực lịch sử và lịch sử được con người nhận thức — Lịch sử 10, KNTT, Bài 1'
        before='(như sự kiện năm $1521$ và $1522$ tại đảo Mác-tan)'
        fixed=apply_reviewed_content_corrections(before,'Lịch sử',10,topic)
        self.assertIn('Ê-ca-nô trở về Tây Ban Nha năm $1522$',fixed)
        self.assertEqual(fixed,apply_reviewed_content_corrections(fixed,'Lịch sử',10,topic))
        self.assertEqual(before,apply_reviewed_content_corrections(before,'Lịch sử',11,topic))
        self.assertEqual('`'+before+'`',apply_reviewed_content_corrections('`'+before+'`','Lịch sử',10,topic))
        tree=ast.parse(Path('app.py').read_text(encoding='utf-8'))
        targets={n.targets[0].id for n in ast.walk(tree) if isinstance(n,ast.Assign)
                 and isinstance(n.targets[0],ast.Name) and isinstance(n.value,ast.Call)
                 and isinstance(n.value.func,ast.Name) and n.value.func.id=='apply_reviewed_content_corrections'}
        self.assertTrue({'chat_display','t1_ans_clean'} <= targets)

    def test_reviewed_option_repair_preserves_shuffled_position_key_and_original(self):
        from services.lesson_sources import apply_reviewed_quiz_proposal
        topic='Hiện thực lịch sử và lịch sử được con người nhận thức — Lịch sử 10, KNTT, Bài 1'
        original=dict(question='Điểm khác biệt?',correct='A',options=[
            'A. Nhận thức lịch sử có thể thay đổi, hiện thực lịch sử tồn tại độc lập.',
            'B. Unchanged', 'C. Chỉ có nhận thức lịch sử mới cần đến nguồn tư liệu để chứng minh.', 'D. Unchanged'])
        fixed=apply_reviewed_quiz_proposal(original,'Lịch sử',10,topic)
        self.assertEqual(fixed['correct'],'A')
        self.assertEqual(fixed['options'][2],'C. Nhận thức lịch sử không cần đối chiếu với bất kỳ nguồn tư liệu nào.')
        self.assertEqual(fixed['options'][0],original['options'][0])
        self.assertIn('Chỉ có',original['options'][2])
        self.assertEqual(fixed,apply_reviewed_quiz_proposal(fixed,'Lịch sử',10,topic))
        self.assertEqual(original,apply_reviewed_quiz_proposal(original,'Lịch sử',11,topic))

    def test_display_gate_reads_changed_review_in_same_lesson_session(self):
        import ast
        from pathlib import Path
        import real_exam_engine as ree
        from services.academic_context import academic_context
        from services.curriculum_policy import correct_khtn8_lime_soil_confusion, validate_lesson_policy, T1_CONTEXT_REVISION
        from tests.test_expert_patch_regressions import load_function
        tree=ast.parse(Path('app.py').read_text(encoding='utf-8'))
        node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='station1_master_sovereign_brain_gate')
        self.assertFalse(node.decorator_list, 'Registry changes must not be hidden by a lesson-text cache')
        legacy=load_function('_legacy_sanitize_katex_latex')
        sanitize=load_function('sanitize_katex_latex',_legacy_sanitize_katex_latex=legacy)
        gate=load_function('station1_master_sovereign_brain_gate',ree=ree,academic_context=academic_context,
            validate_lesson_policy=validate_lesson_policy,sanitize_katex_latex=sanitize,
            CURRICULUM_POLICY_REVISION=T1_CONTEXT_REVISION,correct_khtn8_lime_soil_confusion=correct_khtn8_lime_soil_confusion)
        original='A source claim'
        with patch('services.lesson_sources.apply_reviewed_content_corrections',side_effect=[original,'A corrected source claim']):
            self.assertEqual(gate(original,'Lịch sử',10,'Unchanged topic'),original)
            self.assertEqual(gate(original,'Lịch sử',10,'Unchanged topic'),'A corrected source claim')

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
