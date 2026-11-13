# -*- coding: utf-8 -*-
import unittest

from services.personal_journey_vault import (
    VAULT_TYPE,
    build_personal_snapshot,
    compare_snapshots,
    compress_vault,
    decompress_vault,
    research_code,
    research_safe_events,
    summarize_station_progress,
)


class PersonalJourneyVaultTests(unittest.TestCase):
    def test_compress_roundtrip_and_progress(self):
        logs = [
            {"type": "EXAM_RESULT", "event_id": "a", "name": "An", "score": 5.0, "subject": "Toán học", "grade": "12"},
            {"type": "EXAM_RESULT", "event_id": "b", "name": "An", "score": 7.0, "subject": "Toán học", "grade": "12"},
            {"type": "COUNSELING_OUTCOME_CHECKIN", "event_id": "c", "name": "An",
             "who5": {"percent_0_100": 40}, "station_from": 4, "station_to": 5},
            {"type": "COUNSELING_OUTCOME_CHECKIN", "event_id": "d", "name": "An",
             "who5": {"percent_0_100": 64}, "station_from": 4, "station_to": 5},
            {"type": "SOCRATIC_DIAGNOSTIC", "event_id": "e", "name": "An", "topic": "Đạo hàm"},
        ]
        snap = build_personal_snapshot(
            student_name="An", grade="12", subject="Toán học",
            analytics_logs=logs, tram_counts={"tram3": 2, "tram5": 1},
        )
        self.assertEqual(snap["type"], VAULT_TYPE)
        self.assertEqual(snap["progress"]["tram3_trend"], "progress")
        self.assertEqual(snap["progress"]["tram5_trend"], "progress")
        blob = compress_vault(snap)
        back = decompress_vault(blob)
        self.assertEqual(back["content_sha256"], snap["content_sha256"])
        delta = compare_snapshots(None, snap)
        self.assertTrue(any("tiến bộ" in n for n in delta["notes"]))

    def test_research_safe_strips_pii_and_counseling_text(self):
        logs = [{
            "type": "SCHOOL_COUNSELING_SESSION",
            "event_id": "x",
            "name": "Nguyễn Văn A",
            "grade": "10",
            "subject": "Ngữ văn",
            "user_excerpt": "em buồn vì bị bắt nạt",
            "assistant_excerpt": "thầy lắng nghe...",
            "safety": {"crisis": False, "violence": True},
            "theme_key": "ban_be",
        }]
        safe = research_safe_events(logs)
        self.assertEqual(len(safe), 1)
        row = safe[0]
        self.assertTrue(row["research_code"].startswith("HS-"))
        self.assertNotEqual(row["research_code"], "Nguyễn Văn A")
        self.assertNotIn("user_excerpt", row)
        self.assertTrue(row["pii_redacted"])
        self.assertTrue(row["counseling_text_omitted"])
        self.assertTrue(row["safety_violence"])
        self.assertEqual(research_code("Nguyễn Văn A", "10"), research_code("Nguyễn Văn A", "10"))


if __name__ == "__main__":
    unittest.main()
