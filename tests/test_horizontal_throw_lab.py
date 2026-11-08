import math
import unittest
from services.lab_scope import horizontal_throw_request, horizontal_throw_state as state


class HorizontalThrowLabTests(unittest.TestCase):
    def test_explicit_request_and_missing_or_wrong_context(self):
        command = 'Ném ngang H=20 m, v0=15 m/s, g=10 m/s²'
        self.assertEqual(horizontal_throw_request(command, 'Vật lý')['height'], 20)
        self.assertIsNone(horizontal_throw_request(command, 'Hóa học'))
        self.assertIsNone(horizontal_throw_request('Ném ngang bài này', 'Vật lý'))
        self.assertIsNone(horizontal_throw_request(command + ', H=40 m', 'Vật lý'))

    def test_launch_midpoint_and_impact(self):
        self.assertEqual(state(20, 15, 10, 0)['z'], 20)
        middle = state(20, 15, 10, .5)
        self.assertEqual((middle['t'], middle['x'], middle['z'], middle['vz']), (1, 15, 15, -10))
        end = state(20, 15, 10, 1)
        self.assertEqual((end['T'], end['L'], end['z']), (2, 30, 0))

    def test_independent_components_scaling_and_domain(self):
        base = state(20, 15, 10, 1)
        faster = state(20, 30, 10, 1)
        higher = state(80, 15, 10, 1)
        self.assertEqual(faster['T'], base['T'])
        self.assertEqual(faster['L'], 2 * base['L'])
        self.assertEqual(higher['T'], 2 * base['T'])
        self.assertEqual(higher['L'], 2 * base['L'])
        for args in ((0, 15, 10, 0), (20, 15, 0, 0), (20, 15, 10, 1.1), (20, math.inf, 10, 0)):
            with self.assertRaises(ValueError):
                state(*args)
