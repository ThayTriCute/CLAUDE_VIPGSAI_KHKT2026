"""Bảng 'Sức khỏe hệ thống' cho khu quản trị Trạm 4.

Thuần hàm, không đọc secrets và KHÔNG BAO GIỜ nhận hay trả về giá trị khóa API —
chỉ nhận SỐ LƯỢNG khóa đã cấu hình. App truyền sẵn các tín hiệu vào đây để dễ kiểm thử.
"""

OK, WARN, ERR = "ok", "warn", "err"


def _row(label, value, status, hint=""):
    return {"label": label, "value": value, "status": status, "hint": hint}


def collect_health(*, build=None, key_count=0, db_ok=False, db_records=0,
                   pending_sync=0, versions=None, ai_used=None, ai_limit=None):
    rows = []

    build = build or {}
    sha = str(build.get("sha") or "").strip()
    if sha:
        updated = str(build.get("updated") or "").strip()
        branch = str(build.get("branch") or "").strip()
        detail = sha + (f" · {branch}" if branch else "") + (f" · {updated}" if updated else "")
        rows.append(_row("Bản dựng đang chạy", detail, OK))
    else:
        rows.append(_row("Bản dựng đang chạy", "bản cục bộ (không có thông tin Git)", WARN,
                         "Cloud chưa đọc được commit; kiểm tra lại khi triển khai."))

    try:
        key_count = int(key_count)
    except (TypeError, ValueError):
        key_count = 0
    if key_count <= 0:
        rows.append(_row("Khóa Gemini đã cấu hình", "chưa có khóa", ERR,
                         "Thêm GEMINI_API_KEY trong Secrets hoặc ở thanh bên để dùng được AI."))
    else:
        status = OK if key_count >= 2 else WARN
        hint = "" if key_count >= 2 else "Chỉ 1 khóa: hết hạn mức là gián đoạn, nên thêm khóa dự phòng."
        rows.append(_row("Khóa Gemini đã cấu hình", f"{key_count} khóa (xoay vòng dự phòng)", status, hint))

    if db_ok:
        rows.append(_row("Cơ sở dữ liệu bền vững", f"đã kết nối · {max(0, int(db_records))} bản ghi", OK))
    else:
        rows.append(_row("Cơ sở dữ liệu bền vững", "chưa kết nối", ERR,
                         "Nhật ký chỉ nằm trong phiên; hãy tải CSV trước khi đóng app."))

    pending = max(0, int(pending_sync or 0))
    if pending == 0:
        rows.append(_row("Sự kiện chờ đồng bộ", "0 (đã đồng bộ hết)", OK))
    else:
        rows.append(_row("Sự kiện chờ đồng bộ", f"{pending} sự kiện chưa xác nhận", WARN,
                         "Vào mục Nhật ký bấm 'Thử gửi lại sự kiện' hoặc tải file dự phòng."))

    if ai_limit is not None:
        used = max(0, int(ai_used or 0))
        limit = int(ai_limit)
        remaining = max(0, limit - used)
        status = ERR if remaining == 0 else WARN if remaining <= 5 else OK
        hint = "Phiên này đã chạm giới hạn; học sinh cần tải lại trang để hỏi tiếp." if remaining == 0 else ""
        rows.append(_row("Lượt gọi AI trong phiên", f"{used}/{limit} (còn {remaining})", status, hint))

    for name, value in (versions or {}).items():
        rows.append(_row(name, str(value), OK))

    return rows


def health_summary(rows):
    """(trạng thái nặng nhất, số cảnh báo, số lỗi)."""
    err = sum(1 for r in rows if r["status"] == ERR)
    warn = sum(1 for r in rows if r["status"] == WARN)
    overall = ERR if err else WARN if warn else OK
    return overall, warn, err
