# -*- coding: utf-8 -*-
import unittest

from services.tram4_learner_insights import (
    build_learner_profiles,
    cohort_summary,
    collect_pre_post_pairs,
    parent_report_defaults,
    weak_topics,
)


def _exam(sid, name, subject, grade, phase, score, **extra):
    row = {
        "type": "EXAM_RESULT",
        "student_id": sid,
        "name": name,
        "subject": subject,
        "grade": grade,
        "phase": phase,
        "score": score,
        "code": extra.pop("code", "E1"),
        "answers": extra.pop("answers", {}),
    }
    row.update(extra)
    return row


class Tram4LearnerInsightsTests(unittest.TestCase):
    def sample_logs(self):
        return [
            _exam("hs01", "An", "Toán học", "Lớp 12", "pre", 5.0, answers={"_item_results": {"p1_0": False, "p1_1": True, "p1_2": True}}),
            _exam("hs01", "An", "Toán học", "Lớp 12", "post", 7.5, answers={"_item_results": {"p1_0": True, "p1_1": True, "p1_2": True}}),
            _exam("hs02", "Bình", "Toán học", "Lớp 12", "pre", 6.0),
            _exam("hs02", "Bình", "Toán học", "Lớp 12", "post", 6.5),
            {
                "type": "SOCRATIC_DIAGNOSTIC",
                "student_id": "hs01",
                "name": "An",
                "grade": "Lớp 12",
                "subject": "Toán học",
                "topic": "Đạo hàm",
                "error_type": "nhầm dấu",
            },
            {
                "type": "SOCRATIC_DIAGNOSTIC",
                "student_id": "hs01",
                "name": "An",
                "grade": "Lớp 12",
                "subject": "Toán học",
                "topic": "Đạo hàm",
                "error_type": "nhầm dấu",
            },
            {
                "type": "SOCRATIC_DIAGNOSTIC",
                "student_id": "hs01",
                "name": "An",
                "grade": "Lớp 12",
                "subject": "Toán học",
                "topic": "Tiệm cận",
                "error_type": "thiếu điều kiện",
            },
        ]

    def test_collect_pairs_and_cohort(self):
        pairs = collect_pre_post_pairs(self.sample_logs())
        self.assertEqual(len(pairs), 2)
        an = next(p for p in pairs if p["student_id"] == "hs01")
        self.assertEqual(an["pre"], 5.0)
        self.assertEqual(an["post"], 7.5)
        self.assertEqual(an["delta"], 2.5)
        summary = cohort_summary(self.sample_logs())
        self.assertEqual(summary["n_pairs"], 2)
        self.assertGreater(summary["mean_delta"], 0)

    def test_profiles_personalize_with_weak_topics(self):
        profiles = build_learner_profiles(self.sample_logs())
        an = next(p for p in profiles if p["student_id"] == "hs01")
        self.assertEqual(an["pair_count"], 1)
        self.assertEqual(an["weak_topics"][0]["topic"], "Đạo hàm")
        self.assertIn("Đạo hàm", an["recommendation"])
        self.assertIsNotNone(an["bkt_mastery"])

    def test_parent_defaults_from_observed_not_hardcoded(self):
        defaults = parent_report_defaults(self.sample_logs(), preferred_name="An", preferred_subject="Toán học")
        self.assertEqual(defaults["source"], "observed_pair")
        self.assertEqual(defaults["pre"], 5.0)
        self.assertEqual(defaults["post"], 7.5)
        self.assertNotEqual((defaults["pre"], defaults["post"]), (5.5, 8.5))

    def test_empty_logs_do_not_invent_scores(self):
        defaults = parent_report_defaults([])
        self.assertEqual(defaults["source"], "empty")
        self.assertIsNone(defaults["pre"])
        self.assertIsNone(defaults["post"])
        self.assertEqual(weak_topics([]), [])


if __name__ == "__main__":
    unittest.main()
