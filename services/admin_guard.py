"""Bảo vệ khu quản trị Trạm 4 (nơi có tên, điểm, bài làm của học sinh).

- Khóa dò mật khẩu ở mức TIẾN TRÌNH: khóa theo phiên dễ bị vượt bằng cách mở phiên mới.
- Vô hiệu hóa công thức trong CSV: tên học sinh là văn bản tự do, có thể bắt đầu bằng
  '=', '+', '-', '@' và bị Excel chạy như công thức khi giáo viên mở tệp.
"""
import threading
import time

MAX_FAILURES = 15
WINDOW_SECONDS = 600.0
LOCK_SECONDS = 120.0

_lock = threading.Lock()
_failures = []
_locked_until = 0.0


def admin_globally_locked(now=None):
    now = time.monotonic() if now is None else now
    with _lock:
        return now < _locked_until


def record_admin_failure(now=None):
    """Ghi một lần nhập sai; trả về True nếu vừa kích hoạt khóa toàn cục."""
    global _locked_until
    now = time.monotonic() if now is None else now
    with _lock:
        _failures[:] = [t for t in _failures if now - t < WINDOW_SECONDS]
        _failures.append(now)
        if len(_failures) >= MAX_FAILURES:
            _locked_until = now + LOCK_SECONDS
            _failures.clear()
            return True
        return False


def reset_admin_guard():
    global _locked_until
    with _lock:
        _failures.clear()
        _locked_until = 0.0


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
