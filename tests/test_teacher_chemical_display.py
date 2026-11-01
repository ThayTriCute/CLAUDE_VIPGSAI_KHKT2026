import unittest

from services.text_boundaries import chemical_display_markdown, wrap_naked_chemistry
from services.lesson_export import build_lesson_html


class TeacherChemicalDisplayTests(unittest.TestCase):
    def test_reviewed_base_lesson_completes_missing_properties_only_in_knowledge_section(self):
        from services.curriculum_policy import correct_khtn8_lime_soil_confusion
        source = ('### PHẦN 1: BÀI HỌC\n#### 2. Hình thành kiến thức\n'
                  'Khái niệm base và thang pH.\n\n#### 3. Ví dụ có lời giải\nVí dụ phân loại.\n'
                  '### PHẦN 3: BÀI TẬP TỰ LUẬN\nCâu 1. Hãy tự giải thích.\n')
        fixed = correct_khtn8_lime_soil_confusion(source, 'Khoa học tự nhiên', 8, 'Base. Thang pH')
        self.assertIn('phenolphthalein', fixed)
        self.assertIn(r'\ce{NaOH + HCl -> NaCl + H2O}', fixed)
        self.assertEqual(fixed.split('### PHẦN 3:')[1], source.split('### PHẦN 3:')[1])
        self.assertEqual(correct_khtn8_lime_soil_confusion(fixed, 'Khoa học tự nhiên', 8, 'Base. Thang pH'), fixed)
        for subject, grade, topic in [('Khoa học tự nhiên', 7, 'Base. Thang pH'),
                                      ('Ngữ văn', 8, 'Base. Thang pH'), ('Khoa học tự nhiên', 8, 'Áp suất')]:
            self.assertEqual(correct_khtn8_lime_soil_confusion(source, subject, grade, topic), source)

    def test_native_display_keeps_coefficients_subscripts_charges_and_direction(self):
        value = chemical_display_markdown(r'$\ce{2H2 + O2 -> 2H2O}$ và $\ce{SO4^{2-}(aq)}$.')
        self.assertIn(r'2\mathrm{H}_{2}', value)
        self.assertIn(r'\rightarrow', value)
        self.assertIn(r'\mathrm{SO}_{4}^{2-}(\mathrm{aq})', value)
        self.assertNotIn(r'\ce', value)
        self.assertIn(r'\mathrm{OH}^{-}', chemical_display_markdown(r'$\ce{OH-}$'))

    def test_bare_reactions_are_wrapped_but_code_and_existing_math_are_preserved(self):
        source = r'Phản ứng: \ce{Cu(OH)2 + H2SO4 -> CuSO4 + 2H2O}' + '\n`\\ce{literal}`\n$x^2$'
        wrapped = wrap_naked_chemistry(source)
        self.assertIn(r'$\ce{Cu(OH)2 + H2SO4 -> CuSO4 + 2H2O}$', wrapped)
        self.assertIn(r'$$\ce{Cu(OH)2 + H2SO4 -> CuSO4 + 2H2O}$$', wrapped)
        self.assertIn('`\\ce{literal}`', wrapped)
        self.assertIn('$x^2$', wrapped)
        self.assertEqual(wrap_naked_chemistry(wrapped), wrapped)
        display = chemical_display_markdown(source)
        self.assertIn(r'\mathrm{Cu}(\mathrm{OH})_{2}', display)
        self.assertIn('`\\ce{literal}`', display)

    def test_export_uses_full_mhchem_without_false_missing_delimiter_error(self):
        lesson = r'Phản ứng: \ce{NaOH + HCl -> NaCl + H2O}'
        for style in ('handwritten', 'color', 'monochrome'):
            page = build_lesson_html('Khoa học tự nhiên', 8, 'Base. Thang pH', lesson, style)
            self.assertNotIn('data-source-issue="math-delimiter"', page)
            self.assertIn(r'\ce{NaOH + HCl -&gt; NaCl + H2O}', page)
        self.assertEqual(lesson, r'Phản ứng: \ce{NaOH + HCl -> NaCl + H2O}')

    def test_unsupported_chemistry_is_explicit_instead_of_silently_rewritten(self):
        self.assertIn('Công thức cần đối chiếu', chemical_display_markdown(r'$\ce{A ->[heat] B}$'))


if __name__ == '__main__':
    unittest.main()
