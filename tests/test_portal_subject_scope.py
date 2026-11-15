# -*- coding: utf-8 -*-
"""Môn chưa có chuyên trang không được kế thừa cổng Toán."""
from __future__ import annotations

import unittest

import real_exam_engine as ree
from services.academic_context import subjects_for_grade


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

    def test_every_subject_grade_keeps_its_own_link_source(self):
        for grade in range(6, 13):
            for subject in subjects_for_grade(grade):
                with self.subTest(subject=subject, grade=grade):
                    url = ree.default_subject_scan_url(subject, grade)
                    own = str(ree.portal_for_subject(subject).get("url") or "")
                    sources = ree.link_scan_sources(subject)
                    self.assertTrue(sources)
                    if subject == "Toán học":
                        self.assertIn(f"toan-{grade}", url)
                        self.assertIn("TOANMATH", sources[0])
                        self.assertIn("MATHVN", sources[1])
                    else:
                        self.assertEqual(url, own)
                        self.assertNotIn("toanmath", url.lower())
                        self.assertNotIn("TOANMATH", sources[0])
                        self.assertNotIn("MATHVN", sources[0])
                    mathvn = ree.link_scan_default_url(subject, grade, "📐 MATHVN.com")
                    if not (subject == "Toán học" and grade == 12):
                        self.assertNotIn("toan-12", mathvn)
                    custom = ree.link_scan_default_url(subject, grade, sources[-2])
                    self.assertEqual(custom, "")


if __name__ == "__main__":
    unittest.main()
