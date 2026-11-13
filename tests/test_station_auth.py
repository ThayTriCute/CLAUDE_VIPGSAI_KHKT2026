# -*- coding: utf-8 -*-
import unittest

from services.station_auth import is_teacher_authenticated, set_teacher_authenticated
from services.station_nav import STATION_LABELS, ensure_station_selection, force_tram5


class StationAuthTests(unittest.TestCase):
    def test_single_flag_syncs_legacy_alias(self):
        state = {}
        self.assertFalse(is_teacher_authenticated(state))
        set_teacher_authenticated(state, True)
        self.assertTrue(state["teacher_authenticated"])
        self.assertTrue(state["tab4_authenticated"])
        self.assertTrue(is_teacher_authenticated(state))
        set_teacher_authenticated(state, False)
        self.assertFalse(is_teacher_authenticated(state))

    def test_legacy_alias_alone_counts(self):
        state = {"tab4_authenticated": True}
        self.assertTrue(is_teacher_authenticated(state))
        self.assertTrue(state["teacher_authenticated"])


class StationNavTests(unittest.TestCase):
    def test_force_tram5(self):
        state = {"selected_station": STATION_LABELS[0]}
        force_tram5(state)
        ensure_station_selection(state)
        self.assertEqual(state["selected_station"], STATION_LABELS[4])
        self.assertEqual(state["sb_station_radio_selector"], STATION_LABELS[4])


if __name__ == "__main__":
    unittest.main()
