"""Durable Supabase sync outbox: failures are retained and retried, never lost.

The local SQLite record is always kept; the cloud payload is queued in the same
transaction and drained with retry/backoff. Secrets are never written to the DB.
"""
import os
import tempfile
import unittest
from unittest.mock import patch

import database


class TestSyncOutbox(unittest.TestCase):
    def setUp(self):
        handle = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        handle.close()
        self._path = handle.name
        self.db = database.DatabaseManager(db_path=self._path)
        # Drive the drain deterministically instead of via background threads.
        self.db._auto_drain = False

    def tearDown(self):
        for suffix in ("", "-wal", "-shm"):
            try:
                os.unlink(self._path + suffix)
            except OSError:
                pass

    def _conn(self):
        return self.db._get_connection()

    def _outbox_count(self, status=None):
        sql = "SELECT COUNT(*) FROM sync_outbox"
        args = ()
        if status:
            sql += " WHERE status=?"
            args = (status,)
        return self._conn().execute(sql, args).fetchone()[0]

    def test_no_creds_enqueues_nothing(self):
        self.assertTrue(self.db.save_exam_attempt(
            {"event_id": "e1", "student_id": "s1", "grade": 12, "score": 5}))
        self.assertEqual(self._outbox_count(), 0)

    def test_failed_sync_is_retained_not_lost(self):
        with patch.object(self.db, "_sync_to_supabase", return_value=False):
            self.db.save_exam_attempt(
                {"event_id": "e2", "student_id": "s1", "grade": 12, "score": 5}, "url", "key")
            self.assertEqual(self._outbox_count("pending"), 1)   # queued atomically
            self.db._drain_outbox()                               # attempt fails
        # Still pending with a bumped attempt count; local record preserved.
        self.assertEqual(self._outbox_count("pending"), 1)
        attempts = self._conn().execute("SELECT attempts FROM sync_outbox").fetchone()[0]
        self.assertGreaterEqual(attempts, 1)
        self.assertEqual(self._conn().execute(
            "SELECT COUNT(*) FROM exam_attempts").fetchone()[0], 1)

    def test_flush_sends_parent_before_child_and_clears(self):
        with patch.object(self.db, "_sync_to_supabase", return_value=False):
            self.db.save_exam_attempt(
                {"event_id": "e3", "student_id": "s9", "grade": 12, "score": 5,
                 "subject": "Toán học"}, "url", "key")
        self.assertEqual(self._outbox_count(), 1)
        with patch.object(self.db, "_sync_to_supabase", return_value=True) as sync:
            sent = self.db.flush_pending_sync("url", "key")
        self.assertEqual(sent, 1)
        self.assertEqual(self._outbox_count(), 0)
        self.assertEqual([c.args[0] for c in sync.call_args_list],
                         ["students", "exam_attempts"])

    def test_replayed_event_enqueues_once(self):
        with patch.object(self.db, "_sync_to_supabase", return_value=False):
            for _ in range(3):
                self.db.save_exam_attempt(
                    {"event_id": "dup", "student_id": "s1", "grade": 12, "score": 5}, "url", "key")
        self.assertEqual(self._outbox_count(), 1)

    def test_diagnostic_and_feedback_are_queued(self):
        with patch.object(self.db, "_sync_to_supabase", return_value=False):
            self.db.save_diagnostic(
                {"event_id": "d1", "student_id": "s1", "grade": 11, "subject": "Vật lý",
                 "topic": "Dao động", "error_type": "Lỗi khái niệm"}, "url", "key")
            self.db.save_feedback(
                {"event_id": "f1", "grade": 10, "category": "Góp ý", "detail": "Tốt"}, "url", "key")
        tables = {row[0] for row in self._conn().execute(
            "SELECT table_name FROM sync_outbox").fetchall()}
        self.assertEqual(tables, {"diagnostic_logs", "user_feedbacks"})

    def test_secrets_never_written_to_outbox(self):
        with patch.object(self.db, "_sync_to_supabase", return_value=False):
            self.db.save_exam_attempt(
                {"event_id": "e4", "student_id": "s1", "grade": 12, "score": 5},
                "https://secret.supabase.co", "super-secret-key")
        dump = "".join(str(r) for r in self._conn().execute(
            "SELECT * FROM sync_outbox").fetchall())
        self.assertNotIn("super-secret-key", dump)
        self.assertNotIn("secret.supabase.co", dump)


if __name__ == "__main__":
    unittest.main()
