# -*- coding: utf-8 -*-
import unittest

from services.legal_source_watch import effectivity_label
from services.school_counseling import (
    OWNER_HANDBOOK_DOC,
    PHILOSOPHY,
    TRAM5_HANDBOOK_MARKER,
    TRAM5_LOCK_MARKER,
    build_journey_context,
    build_research_packet,
    counseling_system_instruction,
    enforce_tram5_reply,
    growth_micro_plan,
    is_crisis_text,
    is_tram5_locked_instruction,
    is_violence_disclosure,
    legal_anchor_markdown,
    owner_handbook_text,
    public_legal_anchors,
)


class SchoolCounselingTests(unittest.TestCase):
    def test_crisis_and_violence_flags(self):
        self.assertTrue(is_crisis_text("em muốn chết"))
        self.assertFalse(is_crisis_text("em muốn cải thiện điểm toán"))
        self.assertTrue(is_violence_disclosure("bị bạn bắt nạt và đánh"))
        self.assertFalse(is_violence_disclosure("em cãi nhau nhẹ về bài tập"))

    def test_packet_routes_to_tram4_research(self):
        packet = build_research_packet(
            student_name="An",
            grade="Lớp 10",
            subject="Toán học",
            theme_key="tu_tin",
            theme_label="Tự tin",
            user_message="Em sợ phát biểu",
            assistant_message="Thầy lắng nghe em...",
            journey_context="• Trạm 1: đang học",
            safety_flags={"crisis": False, "violence": False},
        )
        self.assertEqual(packet["type"], "SCHOOL_COUNSELING_SESSION")
        self.assertEqual(packet["station_from"], 5)
        self.assertEqual(packet["station_to"], 4)
        self.assertIn("Dưỡng thiện tâm", packet["philosophy"])
        self.assertEqual(packet["lock_marker"], TRAM5_LOCK_MARKER)

    def test_system_instruction_hard_lock(self):
        text = counseling_system_instruction(
            student_name="An",
            grade=10,
            subject="Ngữ văn",
            theme_label="Áp lực học",
            journey_context="ctx",
            legal_block=legal_anchor_markdown(),
        )
        self.assertTrue(text.startswith(TRAM5_LOCK_MARKER) or TRAM5_LOCK_MARKER in text[:80])
        self.assertTrue(is_tram5_locked_instruction(text))
        self.assertIn(TRAM5_HANDBOOK_MARKER, text)
        self.assertIn(OWNER_HANDBOOK_DOC, text)
        self.assertIn("ảo giác", owner_handbook_text().casefold() + text.casefold())
        self.assertIn("KHÔNG chẩn đoán", text)
        self.assertIn("111", text)
        self.assertIn("DƯỠNG THIỆN TÂM", text)
        self.assertIn("102/2016/QH13", legal_anchor_markdown())
        self.assertIn("còn hiệu lực", legal_anchor_markdown())
        self.assertIn("docid=190430", legal_anchor_markdown())
        self.assertNotIn("docid=190440", legal_anchor_markdown())

    def test_owner_handbook_file_exists_and_forbids_fabrication(self):
        from pathlib import Path

        hb = owner_handbook_text()
        self.assertIn(TRAM5_HANDBOOK_MARKER, hb)
        self.assertIn("Bịa Điều/Khoản", hb)
        self.assertIn("vbpl", hb.casefold())
        self.assertTrue(Path("docs/AI_TRAM5_COUNSELING_LOCK.md").is_file())
        self.assertTrue(Path("docs/AI_TRAM5_COUNSELING_LOCK.txt").is_file())


    def test_nd80_and_old_still_in_force_labels(self):
        codes = {r["code"]: r for r in public_legal_anchors("2026-11-12")}
        self.assertIn("80/2017/NĐ-CP", codes)
        self.assertIn("còn hiệu lực", codes["80/2017/NĐ-CP"]["effectivity_label"])
        self.assertIn("102/2016/QH13", codes)
        self.assertIn("còn hiệu lực", effectivity_label(codes["102/2016/QH13"], "2026-11-12"))
        upcoming = {r["code"]: r for r in public_legal_anchors("2026-11-12")}
        self.assertIn("89/2026/TT-BGDĐT", upcoming)
        self.assertIn("chưa có hiệu lực", upcoming["89/2026/TT-BGDĐT"]["effectivity_label"])

    def test_enforce_reply_keeps_philosophy(self):
        out, flags = enforce_tram5_reply("Em hãy thở sâu và nói với bố mẹ.")
        self.assertIn("thiện tâm", out.casefold())
        self.assertIn("philosophy_reminder_appended", flags)
        clinical, cflags = enforce_tram5_reply("Thầy chẩn đoán em bị rối loạn lo âu.")
        self.assertIn("possible_clinical_language", cflags)
        self.assertIn("không", clinical.casefold())

    def test_journey_and_growth_plan(self):
        journey = build_journey_context(
            student_name="An",
            grade=12,
            subject="Toán học",
            cross_station_text="• Trạm 3: đã thi thử",
            last_exam_score=6.5,
            weak_topics=[{"topic": "Đạo hàm", "count": 2}],
        )
        self.assertIn("Trạm 3", journey)
        self.assertIn("Đạo hàm", journey)
        self.assertIn("nhân phẩm", journey)
        self.assertGreaterEqual(len(growth_micro_plan("ap_luc_hoc")), 3)
        self.assertIn(PHILOSOPHY.split("–")[0].strip().split()[0], "Dưỡng")


if __name__ == "__main__":
    unittest.main()
