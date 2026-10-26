from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch
import unittest

from services.math_publication import (MathPublicationError, generate_checked_text,
    math_for_web, render_formulas, segments, validate_exam_math, validate_math_text, normalize_real_aliases)
from services.curriculum_policy import prepare_exam_for_delivery, validate_lesson_policy


class TestMathPublication(unittest.TestCase):
    def test_real_katex_renders_subject_notation_instead_of_unicode_approximation(self):
        for text in (r'$\frac{\sqrt{x+1}}{x^2+1}$', r'$$\ce{2H2 + O2 -> 2H2O}$$',
                     r'$x=A\cos(\omega t+\varphi),\quad R=2\,\Omega$', r'$\vec{F}=m\vec{a}$',
                     r'$\text{Nhiệt lượng}\ Q=mc\Delta T$', r'\[\begin{cases}x+y=1\\x-y=0\end{cases}\]'):
            self.assertEqual(validate_math_text(text), text)
            rendered = math_for_web(text)
            self.assertIn('class="katex', rendered)
            self.assertNotIn('class="katex-error', rendered)

    def test_bad_commands_braces_and_delimiters_are_not_published(self):
        for text in (r'$\frac{1}{2$', r'$\notARealCommand{x}$', r'$$x+1$', r'\(x+1\]', r'\frac{1}{2}'):
            with self.subTest(text=text), self.assertRaises(MathPublicationError):
                validate_math_text(text)

    def test_trusted_html_or_macro_commands_are_rejected(self):
        for text in (r'$\href{https://example.com}{x}$', r'$\htmlClass{bad}{x}$', r'$\def\a{\a}\a$'):
            with self.assertRaises(MathPublicationError):
                validate_math_text(text)

    def test_code_and_escaped_dollar_are_not_treated_as_equations(self):
        text = 'Ví dụ `\\badCommand` và giá \\$5.\n```python\nprint("$\\badCommand$")\n```'
        self.assertEqual(validate_math_text(text), text)
        self.assertIn('<code>', math_for_web(text))
        self.assertIn(r'\badCommand', math_for_web(text))

    def test_source_html_is_escaped_before_inserting_trusted_math(self):
        value = math_for_web('<img src=x onerror=alert(1)> $x+1$')
        self.assertNotIn('<img src=x', value)
        self.assertIn('&lt;img', value)
        self.assertIn('class="katex', value)

    def test_real_alias_repair_has_delimiters_and_preserves_code(self):
        text = r'Tập xác định D = R và \R. Ví dụ `D = R; \R`.'
        result = normalize_real_aliases(text)
        self.assertIn(r'$D = \mathbb{R}$', result)
        self.assertIn(r'`D = R; \R`', result)
        self.assertEqual(validate_math_text(result), result)

    def test_export_does_not_embed_a_known_broken_formula(self):
        from services.lesson_export import build_lesson_html
        with self.assertRaises(MathPublicationError):
            build_lesson_html('Hóa', 10, 'Bài học', r'$\badmath$')

    def test_cleaner_preserves_display_and_adjacent_inline_math(self):
        from real_exam_engine import deep_clean_pua_and_artifacts
        for text in (r'$$y=3x^2-3$$', '$x$ $y$', r'```tex' + '\n$$x$$\n```'):
            self.assertEqual(deep_clean_pua_and_artifacts(text), text)
        self.assertEqual(deep_clean_pua_and_artifacts('A $$ $$ B'), 'A  B')

    def test_every_answer_option_and_explanation_is_checked(self):
        for field in ('q', 'ans', 'explain', 'opt'):
            value = r'$\brokencommand$'
            q = {'q': 'Câu hỏi', 'ans': 'A', 'explain': 'Giải thích', 'opt': ['1','2','3','4']}
            q[field] = [value,'2','3','4'] if field == 'opt' else value
            with self.assertRaises(MathPublicationError):
                validate_exam_math({'p1': [q]})

    def test_tf_statements_and_literature_passage_are_checked(self):
        for exam in ({'p2': [{'q': 'Ngữ liệu', 'stmts': [{'t': r'$\badmath$', 'a': True}]}]},
                     {'part_doc_hieu': {'text': r'$\badmath$', 'questions': []}}):
            with self.assertRaises(MathPublicationError):
                validate_exam_math(exam)

    def test_final_gates_reject_bad_math_without_mutating_the_source(self):
        text = r'## Bài học\n$\badmath$'
        with self.assertRaises(MathPublicationError):
            validate_lesson_policy(text, 'Toán', 6)
        q = {'q': 'Câu hỏi', 'opt': ['1','2','3',r'$\badmath$'], 'ans':'A'}
        with self.assertRaises(MathPublicationError):
            prepare_exam_for_delivery({'p1':[q]}, 'Toán', 6)
        self.assertEqual(q['opt'][3], r'$\badmath$')

    def test_engine_failure_never_returns_unchecked_success(self):
        with patch('services.math_publication._engine', side_effect=RuntimeError('test unavailable')):
            with self.assertRaises(MathPublicationError):
                validate_math_text('$987654321+x$')

    def test_formula_limits_are_bounded(self):
        for text in ('$' + 'x+' * 2200 + '1$', ' '.join('$x$' for _ in range(501))):
            with self.assertRaises(MathPublicationError):
                validate_math_text(text)

    def test_cache_eviction_does_not_lose_items_in_the_current_batch(self):
        items = [(f'x+{i}', False) for i in range(160)]
        render_formulas(items[:128])
        result = render_formulas(items[128:] + items[:128])
        self.assertEqual(len(result), 160)
        self.assertTrue(all('katex' in value for value in result))

    def test_parallel_readers_do_not_share_mutable_formula_macros(self):
        with ThreadPoolExecutor(max_workers=4) as executor:
            values = list(executor.map(validate_math_text, [f'$x+{i}$' for i in range(8)]))
        self.assertEqual(len(values), 8)

    def test_automatic_syntax_repair_is_bounded_to_one_extra_call(self):
        calls = []
        def generate(prompt):
            calls.append(prompt)
            return r'$\badmath$' if len(calls) == 1 else '$x+1$'
        self.assertEqual(generate_checked_text('Bài gốc', generate, validate_math_text), '$x+1$')
        self.assertEqual(len(calls), 2)

        self.assertIn('giữ nguyên', calls[1])
        calls.clear()
        def always_bad(prompt):
            calls.append(prompt)
            return r'$\badmath$'
        with self.assertRaises(MathPublicationError):
            generate_checked_text('Bài gốc', always_bad, validate_math_text)
        self.assertEqual(len(calls), 2)

    def test_failed_repair_retains_private_draft_without_leaking_it_in_message(self):
        marker = r'$\badmath$ PRIVATE_DRAFT'
        with self.assertRaises(MathPublicationError) as caught:
            generate_checked_text('QA', lambda _: marker, validate_math_text)
        self.assertEqual(caught.exception.rejected_draft, marker)
        self.assertEqual(caught.exception.validation_attempts, 2)
        self.assertNotIn('PRIVATE_DRAFT', str(caught.exception))
