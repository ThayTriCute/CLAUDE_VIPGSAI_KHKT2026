import unittest
from services.socratic_context import complete_verified_quote_reference
from services.philosophy_rotation import MODERN


class QuoteReferenceCompletionTests(unittest.TestCase):
    def test_existing_book_url_still_needs_exact_quote_locator(self):
        ref=next(x for x in MODERN if x['author']=='John Stuart Mill')
        original='John Stuart Mill: "'+ref['quote']+'". '+ref['source_url']
        fixed=complete_verified_quote_reference(original,[ref])
        self.assertTrue(fixed.startswith(original))
        self.assertIn(ref['source_locator'],fixed)
        self.assertEqual(fixed,complete_verified_quote_reference(fixed,[ref]))

    def test_internal_guidance_marker_removed_but_code_and_math_preserved(self):
        from services.philosophy_rotation import GUIDANCE
        marker=GUIDANCE.splitlines()[0]
        text='Bài giảng giữ nguyên $x^2$.\n\n'+marker+'\n\nKết thúc.\n`'+marker+'`'
        fixed=complete_verified_quote_reference(text,[])
        self.assertIn('Bài giảng giữ nguyên $x^2$.',fixed)
        self.assertNotIn('\n'+marker+'\n',fixed)
        self.assertIn('`'+marker+'`',fixed)

    def test_real_mill_missing_url_and_note_are_completed_without_rewriting(self):
        ref=next(x for x in MODERN if x['author']=='John Stuart Mill')
        original='John Stuart Mill: "'+ref['quote']+'". Bài học lắng nghe.'
        fixed=complete_verified_quote_reference(original,[ref])
        self.assertTrue(fixed.startswith(original))
        self.assertIn(ref['source_url'],fixed)
        self.assertIn(ref['source_locator'],fixed)
        self.assertIn(ref['translation_note'],fixed)
        self.assertEqual(fixed,complete_verified_quote_reference(fixed,[ref]))

    def test_no_attribution_for_unverified_partial_or_code_only_matches(self):
        ref=MODERN[0]
        for text,reference in [
            ('Tagore: '+ref['quote'],dict(ref,source_verified=False)),
            ('Rabindranath Tagore nói về việc học.',ref),
            ('Một người nói: '+ref['quote'],ref),
            ('```\nRabindranath Tagore: '+ref['quote']+'\n```',ref)]:
            self.assertEqual(text,complete_verified_quote_reference(text,[reference]))


if __name__=='__main__':
    unittest.main()
