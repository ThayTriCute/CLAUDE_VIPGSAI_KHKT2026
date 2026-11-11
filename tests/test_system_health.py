"""Bảng sức khỏe hệ thống: đúng trạng thái và TUYỆT ĐỐI không lộ giá trị khóa."""
import unittest

from services.system_health import ERR, OK, WARN, collect_health, health_summary


class SystemHealthTests(unittest.TestCase):
    def test_all_green_when_everything_configured(self):
        rows = collect_health(build={"sha": "566d4af", "branch": "main", "updated": "11/11/2026 14:00"},
                              key_count=5, db_ok=True, db_records=12, pending_sync=0,
                              versions={"Python": "3.13"})
        self.assertEqual(health_summary(rows), (OK, 0, 0))
        self.assertTrue(any("566d4af" in r["value"] for r in rows))

    def test_flags_missing_key_and_db_as_errors(self):
        rows = collect_health(build={"sha": ""}, key_count=0, db_ok=False, db_records=0, pending_sync=3)
        overall, warn, err = health_summary(rows)
        self.assertEqual(overall, ERR)
        self.assertGreaterEqual(err, 2)
        labels = {r["label"]: r for r in rows}
        self.assertEqual(labels["Khóa Gemini đã cấu hình"]["status"], ERR)
        self.assertEqual(labels["Cơ sở dữ liệu bền vững"]["status"], ERR)
        self.assertEqual(labels["Bản dựng đang chạy"]["status"], WARN)
        self.assertEqual(labels["Sự kiện chờ đồng bộ"]["status"], WARN)

    def test_single_key_is_warning_not_error(self):
        rows = collect_health(build={"sha": "abc1234"}, key_count=1, db_ok=True, db_records=0, pending_sync=0)
        labels = {r["label"]: r for r in rows}
        self.assertEqual(labels["Khóa Gemini đã cấu hình"]["status"], WARN)

    def test_never_emits_a_key_value(self):
        # Chuỗi dạng khóa dựng lúc chạy để không nằm thành literal trong kho công khai.
        key_shape = "AIza" + "Sy" + "B" * 35
        rows = collect_health(build={"sha": "abc1234"}, key_count=5, db_ok=True, db_records=1, pending_sync=0)
        blob = repr(rows)
        self.assertNotIn(key_shape, blob)
        self.assertNotIn("AIza", blob)
        self.assertTrue(any(r["value"].startswith("5 khóa") for r in rows))

    def test_bad_inputs_do_not_crash(self):
        rows = collect_health(build=None, key_count="x", db_ok=False, db_records=-9, pending_sync=None)
        self.assertTrue(rows)
        self.assertIn(health_summary(rows)[0], (OK, WARN, ERR))

    def test_app_wires_panel(self):
        with open("app.py", encoding="utf-8") as handle:
            source = handle.read()
        self.assertIn("Sức khỏe hệ thống", source)
        self.assertIn("key_count=len(active_keys_pool)", source)
        self.assertNotIn("keys=active_keys_pool", source)


if __name__ == "__main__":
    unittest.main()
