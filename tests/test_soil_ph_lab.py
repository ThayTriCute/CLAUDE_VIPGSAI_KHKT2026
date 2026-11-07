import unittest
from services.lab_scope import classify_closed_band, soil_ph_lab_request


class SoilPhLabTests(unittest.TestCase):
    def test_explicit_band_boundaries_and_other_conventions(self):
        for value, expected in ((6.59, 'below'), (6.6, 'within'), (7, 'within'),
                                (7.5, 'within'), (7.51, 'above')):
            self.assertEqual(classify_closed_band(value, 6.6, 7.5), expected)
        self.assertEqual(classify_closed_band(6.6, 6.8, 7.2), 'below')
        with self.assertRaises(ValueError):
            classify_closed_band(float('nan'), 6.6, 7.5)

    def test_requires_soil_context_and_explicit_valid_limits(self):
        request = soil_ph_lab_request('Đất trồng pH, trung tính từ 6,6 đến 7,5', 'Công nghệ')
        self.assertEqual(request, {'type': 'soil_ph_band', 'low': 6.6, 'high': 7.5})
        for text, subject in (
                ('Đất pH trung tính', 'Công nghệ'),
                ('Dung dịch pH trung tính từ 6.6 đến 7.5', 'Hóa học'),
                ('Đất pH trung tính từ 7.5 đến 6.6', 'Công nghệ'),
                ('Đất pH trung tính từ 6.6 đến 7.5', 'Ngữ văn')):
            self.assertIsNone(soil_ph_lab_request(text, subject))
