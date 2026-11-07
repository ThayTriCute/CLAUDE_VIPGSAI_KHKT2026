import unittest
from services.widget_state import retained_subject_index


class RetainedSubjectTests(unittest.TestCase):
    def test_failed_run_recovers_subject_without_other_state(self):
        options = ['Toán học', 'Vật lý', 'Ngữ văn']
        self.assertEqual(retained_subject_index('Lớp 10_Vật lý', options), 1)
        self.assertEqual(retained_subject_index('Lớp 11_Ngữ văn', options), 2)
        self.assertEqual(retained_subject_index(None, options), 0)

    def test_grade_change_does_not_force_unavailable_subject(self):
        self.assertEqual(retained_subject_index('Lớp 9_Khoa học tự nhiên', ['Toán học', 'Vật lý']), 0)
