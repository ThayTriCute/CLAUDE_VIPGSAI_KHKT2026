import unittest
from unittest.mock import Mock
from xml.etree import ElementTree
from services.lab_scope import classify_closed_band, soil_ph_lab_request


class SoilPhLabTests(unittest.TestCase):
    def test_actual_renderer_exports_valid_standalone_svg(self):
        from tests.test_expert_patch_regressions import load_function
        for ph in (6.59, 6.6, 7.5, 7.51):
            st = Mock()
            st.session_state = {}
            st.slider.return_value = ph
            render = load_function('render_smart_lab', st=st)
            render({'type': 'soil_ph_band', 'low': 6.6, 'high': 7.5}, 'Công nghệ')
            downloaded = st.download_button.call_args.args[1]
            root = ElementTree.fromstring(downloaded)
            labels = [node.text for node in root.iter('{http://www.w3.org/2000/svg}text')]
            self.assertIn('pH < 6.6', labels)
            self.assertIn('pH > 7.5', labels)
            self.assertEqual(len(root.findall('{http://www.w3.org/2000/svg}rect')), 3)

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
