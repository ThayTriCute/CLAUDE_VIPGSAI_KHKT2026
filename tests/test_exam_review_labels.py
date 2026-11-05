import unittest
from copy import deepcopy
from qa_runtime import mcq_key_option, mcq_answer_matches
from services.exam_delivery import question_solution_text, answer_source_label
from services.official_paper import original_tin0530


class ReviewLabelsTests(unittest.TestCase):
    def test_key_option_uses_same_index_as_scoring_for_prefixed_and_plain_options(self):
        for options in [['<i>','<img>','<p>','<ol>'],['A. one','B. two','C. three','D. four']]:
            q={'opt':options,'ans':'B'};before=deepcopy(q)
            result=mcq_key_option(q)
            self.assertNotEqual(result,'B. B')
            self.assertTrue(mcq_answer_matches(q,options[1]))
            self.assertEqual(q,before)
        self.assertEqual(mcq_key_option({'opt':['one','two'],'ans':'B'}),'B. two')

    def test_missing_key_or_option_is_not_invented(self):
        self.assertEqual(mcq_key_option({'opt':['one'],'ans':''}),'Chưa xác định')
        self.assertIn('chưa có nội dung',mcq_key_option({'ans':'B'}))

    def test_missing_explanation_is_explicit_and_short_real_explanation_is_retained(self):
        self.assertIn('Chưa có lời giải độc lập',question_solution_text({}))
        self.assertEqual(question_solution_text({'explain':'x=2'}),'x=2')
        self.assertEqual(question_solution_text({'expl':'Theo dữ kiện gốc'}),'Theo dữ kiện gốc')

    def test_ministry_key_attribution_requires_reviewed_original_source_context(self):
        self.assertNotIn('Bộ',answer_source_label({'is_ai_generated':True}))
        exam=original_tin0530('ICT')
        self.assertIn('Khóa Bộ',answer_source_label(exam))
        exam['original_source_archive_sha256']='wrong'
        self.assertNotIn('Bộ',answer_source_label(exam))
