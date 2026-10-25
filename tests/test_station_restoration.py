import copy
import unittest

from services.academic_context import subjects_for_grade
from services.context_recovery import recover_visual
from services.curriculum_policy import lesson_prompt
from services.lesson_contract import LessonContractError, socratic_prompt, validate_socratic_question
from services.math_publication import native_radio_label, validate_math_text


class TestStationRestoration(unittest.TestCase):
    def qualitative(self):
        return {"q": r"Cho hàm số $y=f(x)=ax^3+bx^2+cx+d$ có đồ thị như hình vẽ (giả định đồ thị có dạng chữ N đi lên, cắt trục tung tại điểm có tung độ dương). Khẳng định nào về dấu của hệ số $a$ và $d$ là đúng?",
                "opt": ["A. $a>0,d>0$", "B. $a<0,d>0$", "C. $a>0,d<0$", "D. $a<0,d<0$"], "ans": "B"}

    def test_user_example_has_verified_representative_and_one_answer(self):
        source = self.qualitative(); before = copy.deepcopy(source)
        restored = recover_visual(source, "Toán", 12)
        self.assertEqual(source, before)
        self.assertEqual(restored["f"], {"type": "func_3", "a": 1, "b": 0, "c": -3, "d": 1})
        self.assertEqual(restored["ans"], "A")
        self.assertEqual(restored["visual_recovery"]["original_answer"], "B")
        self.assertEqual(restored["visual_recovery"]["unique_answer"], "A")

    def test_shuffled_options_do_not_choose_the_picture_from_the_answer_key(self):
        source = self.qualitative(); source["opt"] = ["A. $a<0,d<0$", "B. $a>0,d<0$", "C. $a>0,d>0$", "D. $a<0,d>0$"]
        restored = recover_visual(source, "Toán", 12)
        self.assertEqual(restored["ans"], "C")
        self.assertEqual(restored["f"]["a"], 1)

    def test_missing_or_ambiguous_constraints_do_not_get_a_stock_graph(self):
        cases = []
        source = self.qualitative(); source["q"] = source["q"].replace("tung độ dương", "tung độ chưa biết"); cases.append(source)
        source = self.qualitative(); source["q"] += " Tìm thêm hoành độ cực đại."; cases.append(source)
        source = self.qualitative(); source["opt"][1] = source["opt"][0]; cases.append(source)
        for source in cases:
            self.assertNotIn("f", recover_visual(source, "Toán", 12))

    def test_reconstruction_cannot_migrate_to_another_subject_or_lower_grade(self):
        self.assertNotIn("f", recover_visual(self.qualitative(), "Toán", 6))
        self.assertNotIn("f", recover_visual(self.qualitative(), "Vật lý", 12))

    def test_native_full_radio_uses_mhchem_parser_without_altering_original_option(self):
        original = r"A. $\ce{H2O}$"
        label = native_radio_label(original)
        self.assertEqual(original, r"A. $\ce{H2O}$")
        self.assertNotIn(r"\ce", label)
        self.assertIn(r"\mathrm{H}", label)
        self.assertIn("2", label)
        validate_math_text(label)

    def test_native_radio_preserves_other_subject_formulas(self):
        text = r"B. $x=A\cos(\omega t+\varphi)$"
        self.assertEqual(native_radio_label(text), text)

    def test_all_supported_contexts_keep_contract_and_specific_question_in_hint_prompt(self):
        for grade in range(6, 13):
            for subject in subjects_for_grade(grade):
                lesson = lesson_prompt(subject, grade, "CHỦ_ĐỀ_KIỂM_THỬ")
                self.assertIn("CHÍNH XÁC 3", lesson)
                self.assertIn("Bước 4: Kiểm tra và nhìn lại", lesson)
                hint = socratic_prompt("NỘI_DUNG_RIÊNG_CÂU_NÀY", subject, grade, ["A", "B", "C", "D"])
                self.assertIn(subject, hint)
                self.assertIn(f"lớp {grade}", hint)
                self.assertIn("NỘI_DUNG_RIÊNG_CÂU_NÀY", hint)

    def test_explanation_or_answer_cannot_be_rebranded_as_a_socratic_question(self):
        for value in ("Ta có x=77 nên chọn A.", "Em có thấy đáp án là B không?", "What is the answer?", "Em đã tính được $x=77$ chưa?"):
            with self.assertRaises(LessonContractError):
                validate_socratic_question(value, "Tìm nghiệm của phương trình đã cho.")

    def test_contextual_question_is_retained_instead_of_replaced_with_generic_text(self):
        hint = "Em sẽ so sánh dấu của hệ số bậc cao nhất với hướng của nhánh phải đồ thị như thế nào?"
        self.assertEqual(validate_socratic_question(hint, self.qualitative()["q"]), hint)

    def test_incomplete_visual_cannot_pass_station1_publication_just_with_a_warning(self):
        from tests.lesson_samples import complete_lesson
        from services.lesson_contract import validate_lesson_contract
        broken = complete_lesson().replace("Một nửa của 4 là bao nhiêu?", "Cho hàm số có đồ thị như hình vẽ bên. Tung độ điểm cực đại là bao nhiêu?")
        with self.assertRaises(LessonContractError):
            validate_lesson_contract(broken, "Toán", 12)
