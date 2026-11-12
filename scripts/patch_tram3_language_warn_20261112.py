# -*- coding: utf-8 -*-
"""Cảnh báo khi đề đang mở lệch ngôn ngữ môn (không tự dịch)."""
from pathlib import Path

APP = Path(__file__).resolve().parents[1] / "app.py"

OLD = (
    '        if st.session_state.get("custom_request_text"):\r\n'
    '\r\n'
    '            req_str = st.session_state.custom_request_text\r\n'
    '\r\n'
    '            st.info(f"🎯 **CHẾ ĐỘ TÙY BIẾN GIÁO VIÊN ĐANG HOẠT ĐỘNG:** '
    'Đề thi đã được biên soạn theo yêu cầu riêng: *\\"{req_str}\\"*")\r\n'
)

NEW = (
    '        # Cảnh báo ngôn ngữ đề theo môn (shared policy) — không tự dịch câu đã sinh sai\r\n'
    '        _lang_bad = []\r\n'
    '        for _part_key in ("p1", "p2", "p3"):\r\n'
    '            for _qi, _qq in enumerate(exam.get(_part_key) or []):\r\n'
    '                if not isinstance(_qq, dict):\r\n'
    '                    continue\r\n'
    '                if item_display_language_issue(_qq.get("q", ""), subject):\r\n'
    '                    _lang_bad.append(f"{_part_key.upper()}.{_qi + 1}")\r\n'
    '                for _si, _st in enumerate(_qq.get("stmts") or []):\r\n'
    '                    if isinstance(_st, dict) and item_display_language_issue(_st.get("t") or "", subject):\r\n'
    '                        _lang_bad.append(f"{_part_key.upper()}.{_qi + 1}{chr(97 + _si)}")\r\n'
    '        if _lang_bad:\r\n'
    '            st.error(\r\n'
    '                "⚠️ Đề đang mở có câu/mệnh đề viết bằng **tiếng Anh** trong khi môn không phải Tiếng Anh: "\r\n'
    '                + ", ".join(_lang_bad[:12])\r\n'
    '                + ("…" if len(_lang_bad) > 12 else "")\r\n'
    '                + ". Nội dung toán/khoa học vẫn phải đặt câu bằng **tiếng Việt**. "\r\n'
    '                "Hãy tạo lại đề (AI) hoặc chọn đề khác — hệ thống đã chặn giao đề lệch ngôn ngữ."\r\n'
    '            )\r\n'
    '\r\n'
    '        if st.session_state.get("custom_request_text"):\r\n'
    '\r\n'
    '            req_str = st.session_state.custom_request_text\r\n'
    '\r\n'
    '            st.info(f"🎯 **CHẾ ĐỘ TÙY BIẾN GIÁO VIÊN ĐANG HOẠT ĐỘNG:** '
    'Đề thi đã được biên soạn theo yêu cầu riêng: *\\"{req_str}\\"*")\r\n'
)


def main():
    data = APP.read_bytes()
    lf0 = data.count(b"\n") - data.count(b"\r\n")
    old_b = OLD.encode("utf-8")
    new_b = NEW.encode("utf-8")
    # Only patch the testing-room occurrence (first after ĐANG LÀM BÀI)
    marker = "ĐANG LÀM BÀI".encode("utf-8")
    pos = data.find(marker)
    if pos < 0:
        raise SystemExit("testing marker missing")
    rel = data.find(old_b, pos)
    if rel < 0:
        raise SystemExit("testing custom_request block not found after marker")
    # import helper
    if b"item_display_language_issue" not in data.split(b"def ")[0]:
        imp_old = b"from services.curriculum_policy import (T1_CONTEXT_REVISION as CURRICULUM_POLICY_REVISION, assessment_profile,"
        imp_new = b"from services.curriculum_policy import (T1_CONTEXT_REVISION as CURRICULUM_POLICY_REVISION, assessment_profile, item_display_language_issue,"
        if imp_old not in data:
            raise SystemExit("import line not found")
        data = data.replace(imp_old, imp_new, 1)
        rel = data.find(old_b, data.find(marker))
    data2 = data[:rel] + new_b + data[rel + len(old_b):]
    lf1 = data2.count(b"\n") - data2.count(b"\r\n")
    if lf1 != lf0:
        raise SystemExit(f"LF drift {lf0}->{lf1}")
    APP.write_bytes(data2)
    print("WARN_PATCH_OK", "lf_only", lf1)


if __name__ == "__main__":
    main()
