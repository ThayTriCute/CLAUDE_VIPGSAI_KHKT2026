"""Trạm 4: chống dò mật khẩu qua nhiều phiên và chống công thức độc trong CSV."""
import unittest

import pandas as pd

from services import admin_guard as g


class GlobalLockTests(unittest.TestCase):
    def setUp(self):
        g.reset_admin_guard()

    tearDown = setUp

    def test_locks_after_threshold_regardless_of_session(self):
        for i in range(g.MAX_FAILURES - 1):
            self.assertFalse(g.record_admin_failure(now=100.0 + i))
        self.assertFalse(g.admin_globally_locked(now=120.0))
        self.assertTrue(g.record_admin_failure(now=120.0))
        self.assertTrue(g.admin_globally_locked(now=120.0 + g.LOCK_SECONDS - 1))
        self.assertFalse(g.admin_globally_locked(now=120.0 + g.LOCK_SECONDS + 1))

    def test_old_failures_expire(self):
        for i in range(g.MAX_FAILURES - 1):
            g.record_admin_failure(now=float(i))
        self.assertFalse(g.record_admin_failure(now=g.WINDOW_SECONDS + 100.0))
        self.assertFalse(g.admin_globally_locked(now=g.WINDOW_SECONDS + 100.0))


class CsvSafetyTests(unittest.TestCase):
    def test_formula_like_text_is_neutralised_numbers_untouched(self):
        frame = pd.DataFrame({"name": ["=HYPERLINK(\"http://x\")", "+84", "@a", "Nguyễn An", None],
                              "score": [-1.5, 8.0, 9.0, 10.0, 0.0]})
        safe = g.csv_safe(frame)
        self.assertEqual(list(safe["name"][:4]), ["'=HYPERLINK(\"http://x\")", "'+84", "'@a", "Nguyễn An"])
        self.assertEqual(list(safe["score"]), [-1.5, 8.0, 9.0, 10.0, 0.0])
        self.assertEqual(frame["name"][0], "=HYPERLINK(\"http://x\")")

    def test_app_uses_guard(self):
        with open("app.py", encoding="utf-8") as handle:
            source = handle.read()
        self.assertIn("csv_safe(frame).to_csv", source)
        self.assertIn("not global_locked and time.monotonic() >= locked_until and admin_password_matches", source)
        self.assertIn("record_admin_failure()", source)


if __name__ == "__main__":
    unittest.main()
