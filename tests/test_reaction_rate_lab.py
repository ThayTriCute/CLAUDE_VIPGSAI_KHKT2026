import math
import unittest
from services.lab_scope import average_reactant_rate, experimental_rate_ratio, temperature_rate_ratio, reaction_rate_table_request


class ReactionRateLabTests(unittest.TestCase):
    def test_table_rate_and_equation_scaling(self):
        t, c = [0, 3, 6, 9, 12], [1, .707, .500, .354, .250]
        a = average_reactant_rate(t, c, 0, 1, 1)
        b = average_reactant_rate(t, c, 0, 1, 2)
        self.assertAlmostEqual(a['loss_rate'], .293/3)
        self.assertEqual(a['loss_rate'], b['loss_rate'])
        self.assertEqual(b['normalized_rate'], a['normalized_rate']/2)
        for args in ((t,c,1,1,1),(t,c,0,1,0),([0,0], [1,.5],0,1,1)):
            with self.assertRaises(ValueError): average_reactant_rate(*args)

    def test_independent_ratios_and_invalid_inputs(self):
        self.assertEqual(experimental_rate_ratio(2,1), 4)
        self.assertEqual(experimental_rate_ratio(1,2), 2)
        self.assertEqual(experimental_rate_ratio(0,2), 0)
        self.assertEqual(temperature_rate_ratio(2,20,50), 8)
        self.assertEqual(temperature_rate_ratio(2,30,20), .5)
        with self.assertRaises(ValueError): experimental_rate_ratio(math.inf,1)
        with self.assertRaises(ValueError): temperature_rate_ratio(0,20,30)

    def test_only_exact_reviewed_context_uses_source_table(self):
        command='Tốc độ phản ứng H2O2 theo Bảng 19.1'
        topic='Tốc độ phản ứng — Hóa học 10, KNTT, Bài 19'
        self.assertEqual(reaction_rate_table_request(command,'Hóa học',10,topic)['type'],'chem_rate_table')
        self.assertIsNone(reaction_rate_table_request(command,'Hóa học',11,topic))
        self.assertIsNone(reaction_rate_table_request(command,'Vật lý',10,topic))
        self.assertIsNone(reaction_rate_table_request(command,'Hóa học',10,'Bài khác'))
