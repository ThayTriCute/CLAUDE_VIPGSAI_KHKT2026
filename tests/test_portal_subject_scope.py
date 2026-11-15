# -*- coding: utf-8 -*-
"""Môn chưa có chuyên trang không được kế thừa cổng Toán."""
from __future__ import annotations

import unittest

import real_exam_engine as ree


class PortalSubjectScopeTests(unittest.TestCase):
    def test_integrated_subjects_do_not_inherit_math_portal(self):
        for subject in ("Khoa học tự nhiên", "Lịch sử & Địa lý"):
            self.assertEqual(ree.portal_for_subject(subject), {})
            self.assertNotIn("toanmath", ree.default_subject_scan_url(subject, 8).lower())
            self.assertNotIn("TOANMATH", ree.portal_display_name(subject))
            self.assertEqual(ree.default_subject_scan_url(subject, 8), "")

    def test_catalog_subjects_keep_their_own_url(self):
        self.assertEqual(
            ree.default_subject_scan_url("Toán học", 12),
            "https://toanmath.com/de-thi-giua-hk1-toan-12",
        )
        self.assertEqual(ree.default_subject_scan_url("Vật lý", 12), "https://thuvienvatly.com")
        self.assertEqual(ree.default_subject_scan_url("Ngữ văn", 8), "https://nguvan2018.edu.vn")
        self.assertEqual(ree.default_subject_scan_url("Tin học", 12), "https://tinhoc2018.edu.vn")
        self.assertEqual(ree.portal_display_name("Toán học"), "TOANMATH.com")


if __name__ == "__main__":
    unittest.main()
