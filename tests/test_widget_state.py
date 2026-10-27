import unittest

from services.widget_state import valid_option_index


class TestCachedExamSelection(unittest.TestCase):
    def test_preserves_valid_selection(self):
        self.assertEqual(valid_option_index(2, 4), 2)

    def test_resets_stale_labels_types_and_catalogue_bounds(self):
        for value in ('old exam label', '2', None, True, 1.5, [], {}, -1, 4):
            with self.subTest(value=value):
                self.assertEqual(valid_option_index(value, 4), 0)

    def test_catalogue_shrink_and_empty_catalogue(self):
        self.assertEqual(valid_option_index(3, 2), 0)
        self.assertEqual(valid_option_index(0, 0), 0)
