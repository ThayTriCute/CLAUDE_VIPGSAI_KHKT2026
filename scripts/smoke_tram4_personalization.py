# -*- coding: utf-8 -*-
"""Smoke Trạm 4: mở cho HS — hồ sơ cá nhân hóa không cần MK station."""
from pathlib import Path

from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]


def main():
    at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=90)
    at.secrets["ADMIN_PASS"] = "qa-private-password"
    at.run()
    at.session_state["selected_station"] = "📊 Trạm 4: Dữ Liệu & Nghiên Cứu"
    at.run()
    at.session_state["analytics_logs"] = [
        {
            "type": "EXAM_RESULT",
            "event_id": "e1",
            "student_id": "hs01",
            "name": "An",
            "subject": "Toán học",
            "grade": "Lớp 12",
            "phase": "pre",
            "score": 5.0,
            "code": "T1",
            "answers": {"_item_results": {"a": False, "b": True, "c": True}},
        },
        {
            "type": "EXAM_RESULT",
            "event_id": "e2",
            "student_id": "hs01",
            "name": "An",
            "subject": "Toán học",
            "grade": "Lớp 12",
            "phase": "post",
            "score": 7.5,
            "code": "T2",
            "answers": {"_item_results": {"a": True, "b": True, "c": True}},
        },
        {
            "type": "SOCRATIC_DIAGNOSTIC",
            "event_id": "d1",
            "student_id": "hs01",
            "name": "An",
            "grade": "Lớp 12",
            "subject": "Toán học",
            "topic": "Đạo hàm",
            "error_type": "nhầm dấu",
        },
    ]
    at.run()
    assert list(at.exception) == [], [e.message for e in at.exception]
    labels = [getattr(t, "label", "") for t in at.text_input]
    assert "Mật khẩu quản trị:" not in labels, "Trạm 4 không được khóa station"
    print("AUTH_OK", "open_for_students")

    md = " ".join(str(getattr(x, "value", x)) for x in at.markdown)
    print("HAS_PROFILE", "Hồ sơ cá nhân hóa" in md)
    print("HAS_OBS_NOTE", "quan sát" in md.lower() or any("quan sát" in str(getattr(i, "value", i)).lower() for i in at.info))
    print("HAS_T4_OPEN_CAPTION", "Trạm 4 mở cho học sinh" in md or any(
        "Trạm 4 mở" in str(getattr(c, "value", c)) for c in at.caption
    ))
    print("SMOKE_TRAM4_OK")


if __name__ == "__main__":
    main()
