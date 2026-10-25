"""Speech stays on demand and does not claim an unverified regional accent."""
import ast
from pathlib import Path
import shutil
import subprocess
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from services.speech_service import speech_button, speech_controls, speech_script, speech_bootstrap
from services.speech_audio import valid_request, free_speech_audio


class TestSpeechService(unittest.TestCase):
    def test_button_escapes_lesson_and_subject_instead_of_executing_them(self):
        button = speech_button('</button><script>alert(1)</script> "x"', '" onclick="alert(2)', "one")
        self.assertNotIn("<script>", button)
        self.assertIn("&lt;script&gt;", button)
        self.assertIn("&quot;", button)
        self.assertEqual(speech_button("", "Toán", "empty"), "")

    def test_controls_have_voice_names_language_override_and_stop(self):
        markup = speech_controls("Tiếng Anh", 6, "Trạm 3")
        for value in ('gsai-voice-vi', 'gsai-voice-en', 'gsai-speech-language', 'data-gsai-stop'):
            self.assertIn(value, markup)
        self.assertIn("không tự chứng minh giọng Nam Bộ", markup)
        self.assertNotIn("translate.googleapis.com", markup)
        self.assertNotIn("fetch(", speech_script())

    def test_untrusted_context_cannot_close_script(self):
        markup = speech_bootstrap('</script><script>alert(1)', 6, "Trạm 1")
        self.assertNotIn('</script><script>alert(1)', markup)
        self.assertIn('\\u003c/script>', markup)

    def test_rendering_tts_wrapper_has_no_audio_fetch_or_character_cutoff(self):
        tree = ast.parse(Path(__file__).resolve().parents[1].joinpath("app.py").read_text(encoding="utf-8"))
        fn = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "create_pedagogical_tts_component")
        calls = [ast.unparse(node.func) for node in ast.walk(fn) if isinstance(node, ast.Call)]
        self.assertEqual(calls, ["speech_button", "st.html"])
        self.assertFalse(any(isinstance(node, ast.Subscript) for node in ast.walk(fn)))

    @unittest.skipUnless(shutil.which("node"), "Node only needed for JS development tests, not production speech")
    def test_actual_javascript_speech_planner(self):
        result = subprocess.run([shutil.which("node"), "--test", "tests/speech_engine.test.cjs"],
                                cwd=Path(__file__).resolve().parents[1], capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_online_audio_requires_opt_in_matching_context_and_bounded_text(self):
        value = {"consent": True, "context": "Toán|6|1", "lang": "vi", "text": "Xin chào", "id": "test_1"}
        self.assertTrue(valid_request(value, "Toán|6|1"))
        for field, other in (("consent", False), ("context", "other"), ("lang", "xx"), ("text", "x"*501), ("id", "../bad")):
            self.assertFalse(valid_request({**value, field: other}, "Toán|6|1"))

    def test_fallback_language_is_explicit_and_network_runs_only_on_request(self):
        free_speech_audio.clear()
        response = SimpleNamespace(headers={"Content-Type": "audio/mpeg"}, content=b"a"*200, raise_for_status=lambda: None)
        with patch("services.speech_audio.requests.get", return_value=response) as get:
            self.assertEqual(free_speech_audio("Xin chào", "vi"), b"a"*200)
            self.assertEqual(free_speech_audio("Xin chào", "vi"), b"a"*200)
            self.assertEqual(get.call_count, 1)
            self.assertEqual(get.call_args.kwargs["params"]["tl"], "vi")
            self.assertEqual(get.call_args.kwargs["timeout"], (3, 5))
        free_speech_audio.clear()

    def test_fallback_rejects_partial_audio_and_html_error_pages(self):
        free_speech_audio.clear()
        good = SimpleNamespace(headers={"Content-Type": "audio/mpeg"}, content=b"a"*200, raise_for_status=lambda: None)
        bad = SimpleNamespace(headers={"Content-Type": "text/html"}, content=b"a"*200, raise_for_status=lambda: None)
        with patch("services.speech_audio.requests.get", side_effect=[good, bad]):
            with self.assertRaises(ValueError):
                free_speech_audio("nội dung "*30, "vi")
        free_speech_audio.clear()
