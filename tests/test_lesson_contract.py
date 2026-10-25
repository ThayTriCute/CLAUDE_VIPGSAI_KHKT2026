import unittest

from services.academic_context import subjects_for_grade
from services.lesson_contract import (LessonContractError, POLYA_LABELS, lesson_sections,
                                     polya_questions, student_polya, validate_lesson_contract)
from services.math_publication import generate_checked_text
from tests.lesson_samples import complete_lesson


class TestLessonContract(unittest.TestCase):
    def test_complete_three_quiz_two_essay_contract(self):
        lesson = complete_lesson()
        self.assertEqual(validate_lesson_contract(lesson, "Toán", 6), lesson)
        self.assertEqual(len(lesson_sections(lesson)), 3)

    def test_missing_or_extra_mcq_is_not_published(self):
        lesson = complete_lesson()
        for broken in (lesson.replace("Câu 3.", "Mục 3.", 1), lesson.replace("Câu 3.", "Câu 4.", 1)):
            with self.assertRaises(LessonContractError):
                validate_lesson_contract(broken, "Toán", 6)

    def test_absent_answer_key_is_not_defaulted_to_a(self):
        with self.assertRaises(LessonContractError):
            validate_lesson_contract(complete_lesson().replace("ĐÁP ÁN: B", "", 1), "Toán", 6)

    def test_missing_polya_step_and_missing_essay_are_rejected(self):
        lesson = complete_lesson()
        for broken in (lesson.replace("Bước 4:", "Giai đoạn 4:", 1), lesson.rsplit("Câu 2.", 1)[0]):
            with self.assertRaises(LessonContractError):
                validate_lesson_contract(broken, "Toán", 6)

    def test_ai_solution_and_english_guidance_never_enter_student_polya(self):
        lesson = complete_lesson().replace("Em cần tự xem xét thông tin nào ở bước này?", "Understand the problem. THE_ANSWER_IS_77. Solve x=77.")
        rendered = student_polya(lesson, "Toán", 6)
        for secret in ("THE_ANSWER", "Understand", "Solve", "PRIVATE_REASONING", "OUTCOME", "COGNITIVE_STEPS", "x=77"):
            self.assertNotIn(secret, rendered)
        for number, title in enumerate(POLYA_LABELS, 1):
            self.assertEqual(rendered.count(f"Bước {number}: {title}"), 2)

    def test_all_supported_subject_grade_pairs_use_four_vietnamese_questions(self):
        for grade in range(6, 13):
            for subject in subjects_for_grade(grade):
                with self.subTest(subject=subject, grade=grade):
                    hints = polya_questions(subject, grade)
                    self.assertEqual(len(hints), 4)
                    self.assertTrue(all(hint.endswith("?") and hint.count("?") == 1 for hint in hints))
                    self.assertFalse(any("Step" in hint or "Answer" in hint or "Solution" in hint for hint in hints))

    def test_theory_worked_example_is_separate_from_self_study_exercise(self):
        lesson = complete_lesson("Ví dụ có lời giải: $1+1=2$. Nội dung lớp 6.")
        validate_lesson_contract(lesson, "Toán", 6)
        self.assertIn("$1+1=2$", lesson_sections(lesson)[0])
        self.assertNotIn("$1+1=2$", student_polya(lesson, "Toán", 6))

    def test_structure_repair_is_bounded_to_one_extra_ai_call(self):
        calls = []
        def generate(prompt):
            calls.append(prompt)
            return "Bài thiếu phần trắc nghiệm" if len(calls) == 1 else complete_lesson()
        result = generate_checked_text("Toán lớp 6", generate, lambda text: validate_lesson_contract(text, "Toán", 6))
        self.assertEqual(len(calls), 2)
        self.assertEqual(result, complete_lesson())

    def test_answer_in_essay_stem_is_rejected(self):
        lesson = complete_lesson().replace("Bước 1:", "Đáp số: 77\nBước 1:", 1)
        with self.assertRaises(LessonContractError):
            validate_lesson_contract(lesson, "Toán", 6)
