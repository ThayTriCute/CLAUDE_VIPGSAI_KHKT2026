# VIP 74.3 - HỆ THỐNG GIA SƯ AI THPT 2026 (CHUẨN GDPT 2018 - HYBRID DATABASE & SỰ KIỆN KHẢO THÍ ĐỒNG BỘ)
import sqlite3
import os
import json
import logging
import requests
import threading
import uuid
import math
from qa_runtime import parse_grade
from datetime import datetime, timedelta, timezone

DB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
DB_PATH = os.path.join(DB_DIR, "gsai_learning.db")

class DatabaseManager:
    """
    HỆ THỐNG GSAI - THPT 2026 (VIP 66.2): Quản trị CSDL lai (Hybrid Database):
    - Cập nhật VIP 66.2 (18/10/2026): Tối ưu hóa lưu trữ đề thi, ma trận chấm điểm và nhật ký làm bài Socratic.
    - Tầng 1: CSDL SQLite cục bộ bền vững (Offline-first, 0ms, lưu trữ vĩnh viễn không mất dữ liệu).
    - Tầng 2: CSDL Đám mây Supabase PostgreSQL (nếu cấu hình trong secrets.toml).
    """
    def __init__(self, db_path=None):
        self.db_path = str(db_path or DB_PATH)
        os.makedirs(os.path.dirname(os.path.abspath(self.db_path)), exist_ok=True)
        self._local = threading.local()
        # Đồng bộ Cloud bền vững: khóa bí mật chỉ giữ trong bộ nhớ (không ghi DB/Git);
        # hàng đợi sync_outbox nằm trong SQLite nên sống qua Cloud restart.
        self._supabase_creds = None
        self._outbox_lock = threading.Lock()
        self._outbox_draining = False
        self._auto_drain = True
        self._init_sqlite()

    def _get_connection(self):
        conn = getattr(self._local, "conn", None)
        if conn is None:
            conn = sqlite3.connect(self.db_path, timeout=15, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys=ON;")
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA synchronous=NORMAL;")
            conn.execute("PRAGMA temp_store=MEMORY;")
            conn.execute("PRAGMA cache_size=-16000;")
            self._local.conn = conn
        return conn

    def _init_sqlite(self):
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.executescript("""
                CREATE TABLE IF NOT EXISTS students (
                    id TEXT PRIMARY KEY,
                    student_code VARCHAR(30) UNIQUE NOT NULL,
                    display_name VARCHAR(100) NOT NULL,
                    grade_level SMALLINT NOT NULL,
                    school_name VARCHAR(150) DEFAULT 'THPT Tân Hiệp',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS exam_attempts (
                    id TEXT PRIMARY KEY,
                    student_id TEXT NOT NULL,
                    student_name VARCHAR(100),
                    grade_level SMALLINT NOT NULL,
                    subject VARCHAR(50) NOT NULL,
                    exam_code VARCHAR(20) NOT NULL,
                    score NUMERIC(4, 2) NOT NULL,
                    phase VARCHAR(20) DEFAULT 'practice',
                    duration_seconds INT DEFAULT 0,
                    grading_status VARCHAR(30) DEFAULT 'auto_graded',
                    answers_json TEXT DEFAULT '{}',
                    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS diagnostic_logs (
                    id TEXT PRIMARY KEY,
                    student_id TEXT NOT NULL,
                    student_name VARCHAR(100),
                    grade_level SMALLINT NOT NULL,
                    subject VARCHAR(50) NOT NULL,
                    topic VARCHAR(200) NOT NULL,
                    error_type VARCHAR(100) NOT NULL,
                    evaluation VARCHAR(100) DEFAULT 'Cần theo dõi',
                    radar_scores_json TEXT DEFAULT '{}',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS user_feedbacks (
                    id TEXT PRIMARY KEY,
                    student_name VARCHAR(100),
                    grade_level SMALLINT,
                    subject VARCHAR(50),
                    category VARCHAR(50) NOT NULL,
                    rating SMALLINT,
                    detail TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE INDEX IF NOT EXISTS idx_exam_study ON exam_attempts (subject, grade_level, phase, student_id);
                CREATE INDEX IF NOT EXISTS idx_diagnostic_search ON diagnostic_logs (subject, grade_level, topic);

                CREATE TABLE IF NOT EXISTS sync_outbox (
                    id TEXT PRIMARY KEY,
                    table_name TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'pending',
                    attempts INTEGER NOT NULL DEFAULT 0,
                    last_error TEXT,
                    next_attempt_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                );
                CREATE INDEX IF NOT EXISTS idx_outbox_pending ON sync_outbox (status, next_attempt_at);
                """)
                conn.commit()
        except Exception as e:
            logging.error("Lỗi khởi tạo CSDL SQLite: %s", e)

    def _sync_to_supabase(self, table_name: str, payload: dict, supabase_url: str, supabase_key: str):
        """Đồng bộ ngầm lên Supabase qua PostgREST API nếu có thông tin kết nối."""
        if not supabase_url or not supabase_key:
            return False
        try:
            url = f"{supabase_url.rstrip('/')}/rest/v1/{table_name}"
            headers = {
                "apikey": supabase_key,
                "Authorization": f"Bearer {supabase_key}",
                "Content-Type": "application/json",
                "Prefer": "resolution=merge-duplicates"
            }
            res = requests.post(url, json=payload, headers=headers, timeout=5)
            return 200 <= res.status_code < 300
        except Exception as exc:
            logging.warning("Không thể đồng bộ Supabase: %s", exc)
            return False

    def _sync_parent_and_event(self, table_name, payload, supabase_url, supabase_key):
        student_id = payload.get("student_id")
        if student_id:
            parent = {"id": student_id, "student_code": student_id,
                      "display_name": payload.get("student_name") or "Ẩn danh",
                      "grade_level": payload.get("grade_level", 12)}
            if not self._sync_to_supabase("students", parent, supabase_url, supabase_key):
                logging.warning("Chưa đồng bộ được học sinh; giữ bản ghi cục bộ để đối chiếu.")
                return False
        ok = self._sync_to_supabase(table_name, payload, supabase_url, supabase_key)
        if not ok:
            logging.warning("Chưa đồng bộ được sự kiện; bản ghi cục bộ vẫn được giữ.")
        return ok

    # --- Hàng đợi đồng bộ bền vững (durable outbox) ------------------------------
    @staticmethod
    def _utc_now():
        return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    def _remember_creds(self, supabase_url, supabase_key):
        """Giữ khóa Supabase trong bộ nhớ tiến trình; không bao giờ ghi vào DB."""
        if supabase_url and supabase_key:
            self._supabase_creds = (supabase_url, supabase_key)

    def _enqueue_sync(self, cursor, table_name, payload):
        """Ghi payload vào sync_outbox TRONG CÙNG giao dịch với bản ghi cục bộ.

        Dùng INSERT OR IGNORE theo khóa idempotency '{bảng}:{id}' nên phát lại
        không tạo bản trùng. Không lưu khóa/bí mật ở đây.
        """
        identity = str(payload.get("id") or uuid.uuid4())
        now = self._utc_now()
        cursor.execute(
            "INSERT OR IGNORE INTO sync_outbox "
            "(id, table_name, payload_json, status, next_attempt_at, created_at, updated_at) "
            "VALUES (?, ?, ?, 'pending', ?, ?, ?)",
            (f"{table_name}:{identity}", table_name,
             json.dumps(payload, ensure_ascii=False), now, now, now))

    def _trigger_drain(self):
        """Khởi chạy một lượt rút hàng đợi ở nền, không chồng lượt."""
        if not self._auto_drain or not self._supabase_creds:
            return
        with self._outbox_lock:
            if self._outbox_draining:
                return
            self._outbox_draining = True

        def worker():
            try:
                self._drain_outbox()
            finally:
                with self._outbox_lock:
                    self._outbox_draining = False

        threading.Thread(target=worker, daemon=True).start()

    def _drain_outbox(self, limit=50):
        """Gửi các mục pending tới hạn; thành công thì xóa, thất bại thì lùi lịch.

        Trả về số mục đã gửi thành công. Idempotency nhờ 'resolution=merge-duplicates'
        của Supabase nên gửi lại an toàn.
        """
        creds = self._supabase_creds
        if not creds:
            return 0
        supabase_url, supabase_key = creds
        now = self._utc_now()
        try:
            with self._get_connection() as conn:
                rows = conn.execute(
                    "SELECT id, table_name, payload_json, attempts FROM sync_outbox "
                    "WHERE status='pending' AND next_attempt_at <= ? "
                    "ORDER BY next_attempt_at LIMIT ?",
                    (now, int(limit))).fetchall()
        except Exception as exc:
            logging.warning("Không đọc được sync_outbox: %s", exc)
            return 0
        sent = 0
        for row in rows:
            try:
                payload = json.loads(row["payload_json"])
            except (ValueError, TypeError):
                payload = None
            ok = False
            last_error = "payload_json không hợp lệ" if payload is None else ""
            if isinstance(payload, dict):
                try:
                    ok = self._sync_parent_and_event(row["table_name"], payload, supabase_url, supabase_key)
                    if not ok:
                        last_error = "đồng bộ Supabase trả về thất bại"
                except Exception as exc:
                    last_error = str(exc)[:300]
                    logging.warning("Lỗi đồng bộ outbox %s: %s", row["id"], exc)
            try:
                with self._get_connection() as conn:
                    if ok:
                        conn.execute("DELETE FROM sync_outbox WHERE id=?", (row["id"],))
                        sent += 1
                    else:
                        attempts = int(row["attempts"]) + 1
                        delay = min(3600, 30 * (2 ** min(attempts, 7)))
                        nxt = (datetime.now(timezone.utc) + timedelta(seconds=delay)).strftime("%Y-%m-%d %H:%M:%S")
                        status = "failed" if (payload is None or attempts >= 12) else "pending"
                        conn.execute(
                            "UPDATE sync_outbox SET attempts=?, next_attempt_at=?, status=?, "
                            "last_error=?, updated_at=? WHERE id=?",
                            (attempts, nxt, status, last_error, self._utc_now(), row["id"]))
                    conn.commit()
            except Exception as exc:
                logging.warning("Không cập nhật được sync_outbox: %s", exc)
        return sent

    def flush_pending_sync(self, supabase_url="", supabase_key=""):
        """Gọi khi khởi động (hoặc định kỳ) để đẩy nốt các mục còn tồn sau restart."""
        self._remember_creds(supabase_url, supabase_key)
        if not self._supabase_creds:
            return 0
        return self._drain_outbox()

    def save_student_if_not_exists(self, student_id: str, student_name: str, grade_level: int):
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                INSERT OR IGNORE INTO students (id, student_code, display_name, grade_level)
                VALUES (?, ?, ?, ?)
                """, (student_id, student_id, student_name, grade_level))
                conn.commit()
        except Exception as e:
            logging.error("Lỗi lưu học sinh: %s", e)

    def save_exam_attempt(self, entry: dict, supabase_url: str = "", supabase_key: str = "") -> bool:
        """Lưu kết quả khảo thí Trạm 3."""
        try:
            student_id = str(entry.get("student_id") or "anon-" + str(uuid.uuid4())).strip()
            entry["student_id"] = student_id
            grade_val = entry.get("grade", "Lớp 12")
            grade_num = parse_grade(grade_val)

            self.save_student_if_not_exists(student_id, entry.get("name", "Ẩn danh"), grade_num)

            attempt_id = str(entry.get("event_id") or entry.get("attempt_id") or uuid.uuid4())
            entry["event_id"] = attempt_id
            score = float(entry.get("score", 0.0))
            if not math.isfinite(score) or not 0 <= score <= 10:
                raise ValueError("Điểm phải nằm trong thang 0–10.")
            submitted_time = entry.get("time", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            answers_str = json.dumps(entry.get("answers", {}), ensure_ascii=False)

            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                INSERT OR IGNORE INTO exam_attempts (
                    id, student_id, student_name, grade_level, subject, exam_code,
                    score, phase, duration_seconds, grading_status, answers_json, submitted_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    attempt_id,
                    student_id,
                    entry.get("name", "Ẩn danh"),
                    grade_num,
                    entry.get("subject", "Toán học"),
                    str(entry.get("code", "")),
                    float(entry.get("score", 0.0)),
                    str(entry.get("phase", "practice")),
                    int(entry.get("duration_seconds", 0)),
                    str(entry.get("grading_status", "auto_graded")),
                    answers_str,
                    submitted_time
                ))
                inserted = cursor.rowcount != 0
                # Enqueue đồng bộ TRONG CÙNG giao dịch với bản ghi cục bộ.
                if supabase_url and supabase_key and inserted:
                    self._enqueue_sync(cursor, "exam_attempts", {
                        "id": attempt_id,
                        "student_id": student_id,
                        "student_name": entry.get("name", "Ẩn danh"),
                        "grade_level": grade_num,
                        "subject": entry.get("subject", "Toán học"),
                        "exam_code": str(entry.get("code", "")),
                        "score": float(entry.get("score", 0.0)),
                        "phase": str(entry.get("phase", "practice")),
                        "duration_seconds": int(entry.get("duration_seconds", 0)),
                        "grading_status": str(entry.get("grading_status", "auto_graded")),
                        "answers_json": answers_str,
                        "submitted_at": submitted_time
                    })
                conn.commit()

            if supabase_url and supabase_key:
                self._remember_creds(supabase_url, supabase_key)
                self._trigger_drain()
            return True
        except Exception as e:
            logging.error("Lỗi lưu kết quả bài thi: %s", e)
            return False

    def save_diagnostic(self, entry: dict, supabase_url: str = "", supabase_key: str = "") -> bool:
        """Lưu chẩn đoán lỗi kiến thức Trạm 2."""
        try:
            student_id = str(entry.get("student_id") or "anon-" + str(uuid.uuid4())).strip()
            entry["student_id"] = student_id
            grade_val = entry.get("grade", "Lớp 12")
            grade_num = parse_grade(grade_val)

            self.save_student_if_not_exists(student_id, entry.get("name", "Ẩn danh"), grade_num)

            diag_id = str(entry.get("event_id") or uuid.uuid4())
            entry["event_id"] = diag_id
            diag_time = entry.get("time", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            scores_str = json.dumps(entry.get("scores", {}), ensure_ascii=False)

            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                INSERT OR IGNORE INTO diagnostic_logs (
                    id, student_id, student_name, grade_level, subject,
                    topic, error_type, evaluation, radar_scores_json, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    diag_id,
                    student_id,
                    entry.get("name", "Ẩn danh"),
                    grade_num,
                    entry.get("subject", "Toán học"),
                    entry.get("topic", ""),
                    entry.get("error_type", ""),
                    entry.get("evaluation", ""),
                    scores_str,
                    diag_time
                ))
                inserted = cursor.rowcount != 0
                if supabase_url and supabase_key and inserted:
                    self._enqueue_sync(cursor, "diagnostic_logs", {
                        "id": diag_id,
                        "student_id": student_id,
                        "student_name": entry.get("name", "Ẩn danh"),
                        "grade_level": grade_num,
                        "subject": entry.get("subject", "Toán học"),
                        "topic": entry.get("topic", ""),
                        "error_type": entry.get("error_type", ""),
                        "evaluation": entry.get("evaluation", ""),
                        "radar_scores_json": scores_str,
                        "created_at": diag_time
                    })
                conn.commit()

            if supabase_url and supabase_key:
                self._remember_creds(supabase_url, supabase_key)
                self._trigger_drain()
            return True
        except Exception as e:
            logging.error("Lỗi lưu chẩn đoán lỗi: %s", e)
            return False

    def save_feedback(self, entry: dict, supabase_url: str = "", supabase_key: str = "") -> bool:
        """Lưu phản hồi từ sidebar."""
        try:
            grade_val = entry.get("grade", "Lớp 12")
            grade_num = parse_grade(grade_val)
            entry["event_id"] = str(entry.get("event_id") or uuid.uuid4())
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                INSERT OR IGNORE INTO user_feedbacks (
                    id, student_name, grade_level, subject, category, rating, detail, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    str(entry.get("event_id")),
                    entry.get("name", "Ẩn danh"),
                    grade_num,
                    entry.get("subject", ""),
                    entry.get("category", ""),
                    int(entry.get("rating", 5)),
                    entry.get("detail", ""),
                    entry.get("time", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                ))
                inserted = cursor.rowcount != 0
                if supabase_url and supabase_key and inserted:
                    self._enqueue_sync(cursor, "user_feedbacks", {
                        "id": str(entry.get("event_id")),
                        "student_name": entry.get("name", "Ẩn danh"),
                        "grade_level": grade_num,
                        "subject": entry.get("subject", ""),
                        "category": entry.get("category", ""),
                        "rating": int(entry.get("rating", 5)),
                        "detail": entry.get("detail", ""),
                        "created_at": entry.get("time", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    })
                conn.commit()

            if supabase_url and supabase_key:
                self._remember_creds(supabase_url, supabase_key)
                self._trigger_drain()
            return True
        except Exception as e:
            logging.error("Lỗi lưu phản hồi: %s", e)
            return False

    def get_paired_exam_data(self, subject: str, grade_level: int):
        """
        Truy vấn cặp điểm Pre-test và Post-test trực tiếp bằng SQL với Indexing < 5ms.
        Phục vụ kiểm định Paired t-Test và Cohen's d tại Trạm 4.
        Hỗ trợ chuẩn hóa đa danh pháp (Vật lý/Vật lí, Địa lý/Địa lí, GD KT&PL).
        """
        try:
            subj_clean = (subject or "").strip()
            eq_map = {
                "Vật lý": ["Vật lý", "Vật lí"],
                "Vật lí": ["Vật lý", "Vật lí"],
                "Địa lý": ["Địa lý", "Địa lí"],
                "Địa lí": ["Địa lý", "Địa lí"],
                "Giáo dục kinh tế và pháp luật": ["Giáo dục kinh tế và pháp luật", "GD KT&PL", "GDKT&PL", "GDKT & PL"],
                "GD KT&PL": ["Giáo dục kinh tế và pháp luật", "GD KT&PL", "GDKT&PL", "GDKT & PL"],
                "Khoa học tự nhiên": ["Khoa học tự nhiên", "KHTN"],
                "Lịch sử & Địa lý": ["Lịch sử & Địa lý", "Lịch sử và Địa lý", "LS & ĐL"],
            }
            subj_list = eq_map.get(subj_clean, [subj_clean])
            placeholders = ",".join("?" for _ in subj_list)

            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(f"""
                SELECT
                    pre.student_id,
                    ROUND(AVG(pre.score), 2) AS pre,
                    ROUND(AVG(post.score), 2) AS post,
                    ROUND(AVG(post.duration_seconds) / 60.0, 1) AS minutes
                FROM exam_attempts pre
                INNER JOIN exam_attempts post
                    ON pre.student_id = post.student_id
                    AND pre.grade_level = post.grade_level
                WHERE pre.subject IN ({placeholders})
                  AND post.subject IN ({placeholders})
                  AND pre.grade_level = ?
                  AND LOWER(pre.phase) IN ('pre', 'pre_test', 'trước')
                  AND LOWER(post.phase) IN ('post', 'post_test', 'sau')
                  AND pre.grading_status != 'ai_reference'
                  AND post.grading_status != 'ai_reference'
                GROUP BY pre.student_id
                HAVING COUNT(DISTINCT pre.id) = 1 AND COUNT(DISTINCT post.id) = 1
                """, (*subj_list, *subj_list, grade_level))
                rows = cursor.fetchall()
                return [dict(r) for r in rows]
        except Exception as e:
            logging.error("Lỗi truy vấn cặp điểm: %s", e)
            return []

    def get_all_logs(self):
        """Lấy toàn bộ nhật ký để phục vụ xuất CSV / phân tích Trạm 4."""
        logs = []
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT *, 'EXAM_RESULT' AS type FROM exam_attempts ORDER BY submitted_at DESC")
                for r in cursor.fetchall():
                    d = dict(r)
                    d["event_id"] = d.get("id")
                    d["code"] = d.get("exam_code")
                    d["time"] = d.get("submitted_at")
                    d["grade"] = f"Lớp {d.get('grade_level', 12)}"
                    d["name"] = d.get("student_name")
                    logs.append(d)

                cursor.execute("SELECT *, 'SOCRATIC_DIAGNOSTIC' AS type FROM diagnostic_logs ORDER BY created_at DESC")
                for r in cursor.fetchall():
                    d = dict(r)
                    d["event_id"] = d.get("id")
                    d["time"] = d.get("created_at")
                    d["grade"] = f"Lớp {d.get('grade_level', 12)}"
                    d["name"] = d.get("student_name")
                    try:
                        d["scores"] = json.loads(d.get("radar_scores_json", "{}"))
                    except Exception:
                        d["scores"] = {}
                    logs.append(d)

                cursor.execute("SELECT *, 'USER_FEEDBACK' AS type FROM user_feedbacks ORDER BY created_at DESC")
                for r in cursor.fetchall():
                    d = dict(r)
                    d["event_id"] = d.get("id")
                    d["time"] = d.get("created_at")
                    d["grade"] = f"Lớp {d.get('grade_level', 12)}"
                    d["name"] = d.get("student_name")
                    logs.append(d)
        except Exception as e:
            logging.error("Lỗi lấy nhật ký CSDL: %s", e)
        return logs

# Khởi tạo instance dùng chung toàn ứng dụng
db_manager = DatabaseManager()
