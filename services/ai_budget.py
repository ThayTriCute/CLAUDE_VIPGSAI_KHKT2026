"""Giới hạn số lượt gọi AI mỗi phiên — bảo vệ khóa Gemini khỏi lạm dụng/cạn hạn mức.

Thuần hàm, không đọc secrets và không đụng session_state. App truyền số đã dùng
và hạn mức vào. Mặc định 40 lượt/phiên; chỉnh bằng secret MAX_AI_CALLS_PER_SESSION.
"""

DEFAULT_LIMIT = 40
MIN_LIMIT = 5
MAX_LIMIT = 500


def ai_call_limit(raw, default=DEFAULT_LIMIT):
    """Số nguyên hạn mức trong [MIN_LIMIT, MAX_LIMIT]; giá trị hỏng -> mặc định."""
    try:
        if isinstance(raw, bool):
            raise ValueError
        value = int(float(str(raw).strip())) if str(raw).strip() != "" else default
    except (TypeError, ValueError):
        return default
    return max(MIN_LIMIT, min(MAX_LIMIT, value))


def remaining_calls(used, limit):
    try:
        used = max(0, int(used))
    except (TypeError, ValueError):
        used = 0
    return max(0, int(limit) - used)


def is_over_budget(used, limit):
    return remaining_calls(used, limit) <= 0


def over_budget_message(limit):
    return (f"Em đã dùng hết {int(limit)} lượt hỏi AI trong phiên học này rồi. "
            "Hãy nghỉ ôn lại phần vừa học, rồi tải lại trang (F5) để bắt đầu phiên mới nhé. "
            "Giới hạn này giúp hệ thống phục vụ ổn định cho tất cả các bạn.")


def low_budget_notice(remaining, limit):
    """Nhắc nhẹ khi sắp hết lượt; None nếu còn nhiều."""
    if remaining <= 0 or remaining > 5:
        return None
    return f"⏳ Em còn {int(remaining)}/{int(limit)} lượt hỏi AI trong phiên này."
