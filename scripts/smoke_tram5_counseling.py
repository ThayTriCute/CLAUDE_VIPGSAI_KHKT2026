# -*- coding: utf-8 -*-
"""Smoke Trạm 5: khóa GV + WHO-5 stack. Trạm 4 không cần MK."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from streamlit.testing.v1 import AppTest

from services.school_counseling import TRAM5_LOCK_MARKER, is_tram5_locked_instruction, counseling_system_instruction, legal_anchor_markdown
from services.tram5_outcome_metrics import build_outcome_checkin, WHO5_LICENSE


def main():
    si = counseling_system_instruction(
        student_name="An", grade=10, subject="Toán học",
        theme_label="Áp lực", journey_context="ctx", legal_block=legal_anchor_markdown(),
    )
    assert is_tram5_locked_instruction(si) and TRAM5_LOCK_MARKER in si
    sample = build_outcome_checkin(
        student_name="An", grade=10, subject="Toán học", phase="pre",
        who5_scores=[3, 3, 3, 3, 3],
        school_answers={k: 5 for k in ("sleep_rest", "study_pressure", "peer_safety", "self_confidence", "help_seeking")},
        weekly_goal_text="Ngủ đủ 8 tiếng", weekly_goal_progress=4,
    )
    assert sample["who5"]["license"] == WHO5_LICENSE
    print("LOCK_AND_METRICS_OK")

    at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=90)
    at.secrets["ADMIN_PASS"] = "qa-private-password"
    at.run()

    # Trạm 4: không đòi mật khẩu station
    at.session_state["selected_station"] = "📊 Trạm 4: Dữ Liệu & Nghiên Cứu"
    at.run()
    print("EXC_T4", [e.message for e in at.exception][:3])
    assert list(at.exception) == [], [e.message for e in at.exception]
    labels = [getattr(t, "label", "") for t in at.text_input]
    assert "Mật khẩu quản trị:" not in labels
    assert "Mật khẩu giáo viên:" not in labels
    print("T4_OPEN_OK")

    # Trạm 5: phải khóa
    at.session_state["selected_station"] = "💚 Trạm 5: Tư Vấn Tâm Lý Học Đường"
    at.run()
    print("EXC_T5_LOCKED", [e.message for e in at.exception][:3])
    labels = [getattr(t, "label", "") for t in at.text_input]
    assert "Mật khẩu giáo viên:" in labels
    assert not at.session_state.get("teacher_authenticated")
    next(t for t in at.text_input if t.label == "Mật khẩu giáo viên:").set_value("qa-private-password")
    next(b for b in at.button if "Mở khóa Trạm 5" in (b.label or "")).click().run()
    assert at.session_state.get("teacher_authenticated"), "tram5 auth failed"
    print("T5_AUTH_OK")

    body = " ".join(str(getattr(x, "value", "")) for x in list(at.markdown) + list(at.caption) + list(at.info))
    assert "WHO-5" in body or "who5" in body.casefold() or any(
        "WHO-5" in (getattr(x, "value", "") or "") for x in at.markdown
    ) or any("Đo tiến bộ" in (getattr(x, "label", "") or "") for x in at.expander)
    print("HAS_OUTCOME_UI", True)
    print("SMOKE_TRAM5_OK")


if __name__ == "__main__":
    main()
