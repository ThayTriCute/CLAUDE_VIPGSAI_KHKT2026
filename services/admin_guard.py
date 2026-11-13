"""Bảo vệ khu quản trị Trạm 5 (nơi có tên, điểm, bài làm của học sinh).

- Khóa dò mật khẩu bền theo máy (file JSON dưới data/) — khóa chỉ trong RAM dễ bị vượt bằng phiên mới.
- Vô hiệu hóa công thức trong CSV: tên học sinh là văn bản tự do, có thể bắt đầu bằng
  '=', '+', '-', '@' và bị Excel chạy như công thức khi giáo viên mở tệp.
"""
from __future__ import annotations

import json
import threading
import time
from pathlib import Path

MAX_FAILURES = 15
WINDOW_SECONDS = 600.0
LOCK_SECONDS = 120.0

_lock = threading.Lock()
_failures: list[float] = []
_locked_until = 0.0
_STATE_PATH = Path(__file__).resolve().parents[1] / "data" / "admin_guard_state.json"


def _wall_now() -> float:
    return time.time()


def _load_state() -> None:
    global _failures, _locked_until
    try:
        if not _STATE_PATH.is_file():
            return
        raw = json.loads(_STATE_PATH.read_text(encoding="utf-8"))
        now = _wall_now()
        fails = [float(t) for t in (raw.get("failures") or []) if now - float(t) < WINDOW_SECONDS]
        locked = float(raw.get("locked_until") or 0.0)
        _failures = fails
        _locked_until = locked if locked > now else 0.0
    except Exception:
        pass


def _save_state() -> None:
    try:
        _STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
        payload = {"failures": list(_failures), "locked_until": float(_locked_until)}
        tmp = _STATE_PATH.with_suffix(".tmp")
        tmp.write_text(json.dumps(payload), encoding="utf-8")
        tmp.replace(_STATE_PATH)
    except Exception:
        pass


_load_state()


def admin_globally_locked(now=None):
    """now=None: dùng đồng hồ tường + file bền. now=số: chỉ RAM (kiểm thử)."""
    with _lock:
        if now is None:
            _load_state()
            now = _wall_now()
        else:
            now = float(now)
        return now < _locked_until


def record_admin_failure(now=None):
    """Ghi một lần nhập sai; trả về True nếu vừa kích hoạt khóa toàn cục."""
    global _locked_until
    persist = now is None
    with _lock:
        if persist:
            _load_state()
            now = _wall_now()
        else:
            now = float(now)
        _failures[:] = [t for t in _failures if now - t < WINDOW_SECONDS]
        _failures.append(now)
        tripped = False
        if len(_failures) >= MAX_FAILURES:
            _locked_until = now + LOCK_SECONDS
            _failures.clear()
            tripped = True
        if persist:
            _save_state()
        return tripped


def reset_admin_guard():
    global _locked_until
    with _lock:
        _failures.clear()
        _locked_until = 0.0
        _save_state()


def csv_safe_text(value):
    if isinstance(value, str) and value[:1] in ("=", "+", "-", "@", "\t", "\r"):
        return "'" + value
    return value


def csv_safe(frame):
    """Bản sao DataFrame với ô văn bản dạng công thức đã được vô hiệu hóa."""
    result = frame.copy()
    for name in result.columns:
        if result[name].dtype == object or str(result[name].dtype).startswith(("str", "string")):
            result[name] = result[name].map(csv_safe_text)
    return result
