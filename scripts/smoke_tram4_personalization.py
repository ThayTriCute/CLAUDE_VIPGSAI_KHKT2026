# -*- coding: utf-8 -*-
"""Smoke Trạm 4 (tâm lý): mở cho HS — không cần MK station."""
from pathlib import Path

from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]

T4 = "💚 Trạm 4: Tư Vấn Tâm Lý Học Đường"


def main():
    at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=90)
    at.secrets["ADMIN_PASS"] = "qa-private-password"
    at.run()
    at.session_state["selected_station"] = T4
    at.run()
    assert list(at.exception) == [], [e.message for e in at.exception]
    labels = [getattr(t, "label", "") for t in at.text_input]
    assert "Mật khẩu quản trị:" not in labels, "Trạm 4 không được khóa station"
    assert "Mật khẩu giáo viên:" not in labels, "Trạm 4 không được khóa station"
    print("AUTH_OK", "open_for_students")

    md = " ".join(str(getattr(x, "value", x)) for x in list(at.markdown) + list(at.caption) + list(at.info))
    print("HAS_COUNSEL_UI", "Tư vấn" in md or "WHO-5" in md or "tâm lý" in md.lower())
    print("HAS_T4_OPEN_CAPTION", "Trạm 4 mở" in md or "học sinh" in md.lower())
    print("SMOKE_TRAM4_OK")


if __name__ == "__main__":
    main()
