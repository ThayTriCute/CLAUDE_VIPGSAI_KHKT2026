# -*- coding: utf-8 -*-
"""Trạm 3 must not crash when real_exam_engine is missing a portal helper."""
from __future__ import annotations

import types
import unittest
from unittest.mock import patch


class Tram3ReeCallGuardTests(unittest.TestCase):
    def test_missing_portal_helper_returns_default(self):
        import app

        with patch.object(app, "ree", types.SimpleNamespace()):
            self.assertEqual(app._ree_call("portal_for_subject", {}, "Toán học"), {})
            self.assertEqual(app._ree_call("portal_display_name", "fallback", "Toán học", "fallback"), "fallback")
            self.assertEqual(app._ree_call("link_scan_sources", ["🔗 Link tùy chỉnh"], "Ngữ văn"), ["🔗 Link tùy chỉnh"])
            self.assertEqual(app._ree_call("link_scan_default_url", "", "Ngữ văn", 8, "x"), "")

    def test_present_portal_helper_is_used(self):
        import app

        fake = types.SimpleNamespace(portal_for_subject=lambda subject: {"portal_name": f"OK-{subject}"})
        with patch.object(app, "ree", fake):
            self.assertEqual(app._ree_call("portal_for_subject", {}, "Toán học"), {"portal_name": "OK-Toán học"})


if __name__ == "__main__":
    unittest.main()
