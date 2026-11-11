"""Lab ảo: dữ liệu AI ngoài phạm vi không được làm sập giao diện."""
import unittest

from services.lab_safe import clamp_slider_value, sanitize_lab_data, to_number


class LabSafeTests(unittest.TestCase):
    def test_to_number(self):
        self.assertEqual(to_number("2,5"), 2.5)
        self.assertEqual(to_number("1/2"), 0.5)
        self.assertEqual(to_number(-3), -3)
        for bad in ("abc", "1/0", None, True, float("nan"), float("inf"), "2*x+1", [1]):
            with self.subTest(bad=bad):
                self.assertIsNone(to_number(bad))

    def test_sanitize_rejects_non_lab_payloads(self):
        for bad in (None, [], "func_3", {"a": 1}, {"type": ""}, {"type": 3}):
            with self.subTest(bad=bad):
                self.assertIsNone(sanitize_lab_data(bad))

    def test_sanitize_keeps_text_fields_and_fixes_numbers(self):
        data = {"type": " func_3 ", "a": "2,5", "b": None, "c": float("nan"), "d": 2,
                "func": "2*x + 1", "code": "graph LR", "title": "1/2", "note": "abc"}
        clean = sanitize_lab_data(data)
        self.assertEqual(clean, {"type": "func_3", "a": 2.5, "d": 2, "func": "2*x + 1",
                                 "code": "graph LR", "title": "1/2", "note": "abc"})
        self.assertEqual(data["a"], "2,5")

    def test_clamp_out_of_range_and_type(self):
        self.assertEqual(clamp_slider_value(-4.0, 4.0, 7), (4.0, True))
        self.assertEqual(clamp_slider_value(-4.0, 4.0, -9.5), (-4.0, True))
        self.assertEqual(clamp_slider_value(-4.0, 4.0, 1), (1.0, False))
        self.assertIsInstance(clamp_slider_value(-4.0, 4.0, 1)[0], float)
        self.assertEqual(clamp_slider_value(20, 50, 35.0), (35, False))
        self.assertIsInstance(clamp_slider_value(20, 50, 35.0)[0], int)
        self.assertEqual(clamp_slider_value(20, 50, 99), (50, True))
        self.assertEqual(clamp_slider_value(0.1, 4.5, "abc"), (0.1, True))
        self.assertEqual(clamp_slider_value(-3.0, 3.0, "abc"), (0.0, True))

    def test_app_wires_guard(self):
        with open("app.py", encoding="utf-8") as handle:
            source = handle.read()
        start = source.index("def render_smart_lab(")
        end = source.index('st.markdown(\'<div class="main-header">', start)
        self.assertEqual(source[start:end].count("st.slider("), 1)  # chỉ còn trong _lab_slider
        self.assertIn("render_smart_lab(safe_lab_data, subject)", source)
        self.assertIn("sanitize_lab_data(data)", source)


if __name__ == "__main__":
    unittest.main()
