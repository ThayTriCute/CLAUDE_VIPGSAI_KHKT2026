"""Gói neo đi kèm repo phải NEO ĐƯỢC trên Cloud (không có F:), và chỉ chứa bản diễn giải nhỏ."""
import hashlib
import json
import lzma
import os
import unittest
from pathlib import Path
from unittest.mock import patch

from services.lesson_sources import local_textbook_grounding

BUNDLE = Path(__file__).resolve().parents[1] / "textbook_archive_6_12" / "reviewed_lesson_packets"


class BundledGroundingPacketTests(unittest.TestCase):
    def setUp(self):
        self.index = json.loads((BUNDLE / "index.json").read_text(encoding="utf-8"))
        self.entries = self.index["entries"]

    def test_bundle_exists_and_is_shipped_in_repo(self):
        self.assertTrue(BUNDLE.is_dir())
        self.assertGreaterEqual(len(self.entries), 20)

    def test_packets_ground_on_cloud_without_F_drive(self):
        # Mô phỏng Cloud: KHÔNG có biến môi trường trỏ kho → phải tự dùng gói kèm repo.
        loaded = 0
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("GSAI_TEXTBOOK_ARCHIVE_ROOT", None)
            for row in self.entries:
                status = local_textbook_grounding(row["subject"], row["grade"], row["topic"])["status"]
                self.assertIn(status, ("reviewed_excerpt_packet_loaded", "invalid_reviewed_packet"))
                loaded += status == "reviewed_excerpt_packet_loaded"
        # Phần lớn gói phải neo được; nếu tụt mạnh là cơ chế Cloud đã hỏng.
        self.assertGreaterEqual(loaded, len(self.entries) - 1)

    def test_every_indexed_packet_file_matches_its_hash_and_schema(self):
        for row in self.entries:
            packet = BUNDLE / row["path"]
            self.assertTrue(packet.is_file(), row["path"])
            raw = packet.read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(), row["sha256"], row["path"])
            payload = json.loads(lzma.open(packet).read())
            self.assertEqual(payload["schema_version"], 1)
            self.assertEqual(payload["review_status"], "source_reviewed")

    def test_bundle_carries_only_small_paraphrase_packets_no_raw_books(self):
        files = list(BUNDLE.iterdir())
        self.assertFalse([p for p in files if p.suffix.lower() in (".pdf", ".png", ".jpg", ".jpeg")],
                         "Kho kèm repo không được chứa ảnh/sách gốc.")
        for p in files:
            if p.suffix == ".xz":
                self.assertLess(p.stat().st_size, 262144, p.name)
        self.assertLess(sum(p.stat().st_size for p in files), 2_000_000)


if __name__ == "__main__":
    unittest.main()
