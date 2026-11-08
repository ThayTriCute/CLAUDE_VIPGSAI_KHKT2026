import unittest
from services.threshold_control import light_controller_request, light_controller_step


class ThresholdControlTests(unittest.TestCase):
    def test_hysteresis_boundaries_and_power_recovery(self):
        state = False
        results = []
        for light, power in [(50, True), (29, True), (30, True), (35, True),
                             (40, True), (41, True), (35, True), (0, False), (35, True)]:
            state = light_controller_step(light, 30, 40, power, state)
            results.append(state)
        self.assertEqual(results, [False, True, True, True, True, False, False, False, False])

    def test_requires_explicit_valid_thresholds_and_light_context(self):
        data = light_controller_request('Đèn tự động độ sáng, ngưỡng bật 30, ngưỡng tắt 40')
        self.assertEqual((data['low'], data['high']), (30, 40))
        for text in ['Đèn theo độ sáng', 'Tưới cây ngưỡng bật30 ngưỡng tắt40',
                     'Đèn độ sáng ngưỡng bật40 ngưỡng tắt30']:
            self.assertIsNone(light_controller_request(text))

    def test_rejects_invalid_numeric_state(self):
        for light, low, high in [(float('nan'), 30, 40), (10, 40, 30), (101, 30, 40)]:
            with self.assertRaises(ValueError):
                light_controller_step(light, low, high, True, False)
