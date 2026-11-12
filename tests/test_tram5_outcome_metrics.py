# -*- coding: utf-8 -*-
import unittest

from services.tram5_outcome_metrics import (
    WHO5_LICENSE,
    build_outcome_checkin,
    collect_who5_pre_post_pairs,
    score_school_checkin,
    score_who5,
    summarize_who5_pairs,
)


class Tram5OutcomeMetricsTests(unittest.TestCase):
    def test_who5_scoring_and_license(self):
        out = score_who5([5, 4, 3, 2, 1])
        self.assertEqual(out["raw_0_25"], 15)
        self.assertEqual(out["percent_0_100"], 60)
        self.assertEqual(out["license"], WHO5_LICENSE)
        self.assertFalse(out["below_screening_hint_50"])
        low = score_who5([1, 1, 1, 1, 1])
        self.assertTrue(low["below_screening_hint_50"])

    def test_school_checkin_inverts_pressure(self):
        high_pressure = score_school_checkin(
            {
                "sleep_rest": 10,
                "study_pressure": 10,
                "peer_safety": 10,
                "self_confidence": 10,
                "help_seeking": 10,
            }
        )
        low_pressure = score_school_checkin(
            {
                "sleep_rest": 10,
                "study_pressure": 0,
                "peer_safety": 10,
                "self_confidence": 10,
                "help_seeking": 10,
            }
        )
        self.assertLess(
            high_pressure["wellbeing_index_0_10"],
            low_pressure["wellbeing_index_0_10"],
        )

    def test_pre_post_pairs(self):
        pre = build_outcome_checkin(
            student_name="An",
            grade="12",
            subject="Toán học",
            phase="pre",
            who5_scores=[2, 2, 2, 2, 2],
            school_answers={
                "sleep_rest": 5,
                "study_pressure": 5,
                "peer_safety": 5,
                "self_confidence": 5,
                "help_seeking": 5,
            },
            weekly_goal_text="Học Pomodoro",
            weekly_goal_progress=3,
        )
        post = build_outcome_checkin(
            student_name="An",
            grade="12",
            subject="Toán học",
            phase="post",
            who5_scores=[4, 4, 4, 4, 4],
            school_answers={
                "sleep_rest": 7,
                "study_pressure": 3,
                "peer_safety": 7,
                "self_confidence": 7,
                "help_seeking": 8,
            },
            weekly_goal_text="Học Pomodoro",
            weekly_goal_progress=7,
        )
        self.assertEqual(pre["type"], "COUNSELING_OUTCOME_CHECKIN")
        pairs = collect_who5_pre_post_pairs([pre, post])
        self.assertEqual(len(pairs), 1)
        self.assertTrue(pairs[0]["improved"])
        summary = summarize_who5_pairs(pairs)
        self.assertEqual(summary["n_pairs"], 1)
        self.assertEqual(summary["mean_pre"], 40.0)
        self.assertEqual(summary["mean_post"], 80.0)


if __name__ == "__main__":
    unittest.main()
