from datetime import date, time
import unittest

from services.lab_scope import fixed_offset_clock


class FixedOffsetClockTests(unittest.TestCase):
    def test_year_boundary_and_reverse_conversion_preserve_instant(self):
        result = fixed_offset_clock(date(2022, 1, 1), time(7), 420, -360)
        self.assertEqual(result['target'].isoformat(), '2021-12-31T18:00:00')
        self.assertEqual(result['day_change'], -1)
        reverse = fixed_offset_clock(result['target'].date(), result['target'].time(), -360, 420)
        self.assertEqual(reverse['target'], result['source'])

    def test_fractional_offsets_leap_day_and_two_date_boundaries(self):
        result = fixed_offset_clock(date(2024, 3, 1), time(0, 15), 345, 330)
        self.assertEqual(result['target'].isoformat(), '2024-03-01T00:00:00')
        leap = fixed_offset_clock(date(2024, 3, 1), time(0), 60, 0)
        self.assertEqual(leap['target'].isoformat(), '2024-02-29T23:00:00')
        extreme = fixed_offset_clock(date(2022, 1, 1), time(23), -720, 840)
        self.assertEqual(extreme['day_change'], 2)

    def test_bad_input_and_calendar_overflow_fail_without_fabricated_result(self):
        for source, target in [(True, 0), (420.0, 0), (-721, 0), (0, 841)]:
            with self.assertRaises(ValueError):
                fixed_offset_clock(date(2022, 1, 1), time(7), source, target)
        with self.assertRaises(ValueError):
            fixed_offset_clock(date.min, time(0), 840, 0)


if __name__ == '__main__':
    unittest.main()
