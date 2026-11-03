import unittest
from datetime import datetime
from services.cache_metadata import cached_exam_label
from services.academic_context import subjects_for_grade


class CachedExamLabelTests(unittest.TestCase):
    def test_heterogeneous_metadata_across_supported_contexts(self):
        for grade in range(6, 13):
            for subject in subjects_for_grade(grade):
                for stamp in (None, 2026, '2025-2026', '', {}, [], True, datetime(2026, 11, 3)):
                    with self.subTest(subject=subject, grade=grade, stamp=stamp):
                        label = cached_exam_label({'code': '0525', 'topic': subject, 'saved_at': stamp})
                        self.assertIn('0525', label)
                        self.assertIn(subject, label)
        self.assertIn('(2026)', cached_exam_label({'saved_at': 2026}))
        self.assertIn('(2026-11-03)', cached_exam_label({'saved_at': datetime(2026, 11, 3)}))

    def test_missing_and_malformed_fields_do_not_invent_metadata(self):
        for row in (None, {}, {'code': None, 'topic': [], 'saved_at': {'bad': 'value'}}):
            self.assertEqual(cached_exam_label(row), 'Mã đề Chưa rõ - Chuyên đề ôn tập ()')

    def test_selection_identity_changes_with_context_and_catalogue(self):
        from services.cache_metadata import cached_exam_widget_key
        baseline = cached_exam_widget_key('Tin học', 12, ['A', 'B'])
        self.assertEqual(baseline, cached_exam_widget_key('Tin học', 12, ['A', 'B']))
        for subject, grade, labels in [('Toán học', 12, ['A', 'B']),
                                      ('Tin học', 11, ['A', 'B']),
                                      ('Tin học', 12, ['B', 'A']),
                                      ('Tin học', 12, ['A', 'C'])]:
            self.assertNotEqual(baseline, cached_exam_widget_key(subject, grade, labels))
