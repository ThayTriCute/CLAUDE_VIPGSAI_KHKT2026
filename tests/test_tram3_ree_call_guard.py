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

    def test_link_scan_sources_helper_and_mismatch_flag(self):
        import app
        import real_exam_engine as ree

        self.assertTrue(app._REE_PORTAL_HELPERS_OK)
        self.assertTrue(hasattr(ree, "PORTAL_LINK_HELPERS_VERSION"))
        toan_sources = app._tram3_link_scan_sources("Toán học")
        self.assertTrue(any("TOANMATH" in s for s in toan_sources))
        self.assertFalse(app._tram3_link_helpers_mismatch("Toán học", toan_sources))

        with patch.object(app, "_REE_PORTAL_HELPERS_OK", False):
            self.assertTrue(app._tram3_link_helpers_mismatch("Toán học", ["🔗 Link tùy chỉnh"]))

    def test_app_fallback_keeps_toan_and_tin_portals_when_engine_helpers_missing(self):
        import app

        with patch.object(app, "ree", types.SimpleNamespace()):
            with patch.object(app, "_REE_PORTAL_HELPERS_OK", False):
                toan_sources = app._tram3_link_scan_sources("Toán học")
                self.assertTrue(any("TOANMATH" in s for s in toan_sources))
                self.assertEqual(
                    app._tram3_link_scan_default_url("Toán học", 8, toan_sources[0]),
                    "https://toanmath.com/de-thi-giua-hk1-toan-8",
                )
                self.assertIn("TOANMATH", app._portal_display_name_safe("Toán học", "link tùy chỉnh"))

                tin_sources = app._tram3_link_scan_sources("Tin học")
                self.assertTrue(any("Tin" in s for s in tin_sources))
                self.assertEqual(
                    app._tram3_link_scan_default_url("Tin học", 8, tin_sources[0]),
                    "https://tinhoc2018.edu.vn",
                )

                khtn_sources = app._tram3_link_scan_sources("Khoa học tự nhiên")
                self.assertTrue(any("tùy chỉnh" in s for s in khtn_sources))
                self.assertNotIn("TOANMATH", " ".join(khtn_sources))
                self.assertEqual(
                    app._tram3_link_scan_default_url("Khoa học tự nhiên", 8, khtn_sources[0]),
                    "",
                )


if __name__ == "__main__":
    unittest.main()
