# -*- coding: utf-8 -*-
"""Smoke Trạm 4: unlock + hồ sơ cá nhân hóa + phiếu phụ huynh từ logs."""
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
    next(t for t in at.text_input if t.label == "Mật khẩu quản trị:").set_value("qa-private-password")
    next(b for b in at.button if b.label == "🔓 Mở khóa").click().run()
    assert at.session_state.get("tab4_authenticated"), "auth failed"
    assert list(at.exception) == [], [e.message for e in at.exception]

    md = " ".join(str(getattr(x, "value", x)) for x in at.markdown)
    print("AUTH_OK", True)
    print("HAS_PROFILE", "Hồ sơ cá nhân hóa" in md)
    print("HAS_OBS_NOTE", "quan sát" in md.lower() or any("quan sát" in str(getattr(i, "value", i)).lower() for i in at.info))

    pre = next((t.value for t in at.number_input if "Pre-test" in t.label), None)
    post = next((t.value for t in at.number_input if "Post-test" in t.label), None)
    print("REP_PRE_DEFAULT", pre)
    print("REP_POST_DEFAULT", post)
    assert pre == 5.0 and post == 7.5, (pre, post)

    next(r for r in at.radio if r.label == "Nguồn dữ liệu").set_value("Mô phỏng minh họa").run()
    next(b for b in at.button if b.label == "Phân tích các cặp điểm").click().run()
    assert list(at.exception) == []
    print("ANALYZE_OK", bool(at.session_state.get("research_result")))
    print("HAS_CONTROL_EXPANDER", any("đối chứng" in str(getattr(e, "label", e)).lower() for e in at.expander))
    print("SMOKE_OK")


if __name__ == "__main__":
    main()
