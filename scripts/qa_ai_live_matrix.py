# -*- coding: utf-8 -*-
"""Ma trận AI live tối thiểu — ghi JSON evidence (không lưu API key).

Chạy (đã có Key sidebar/secret + app local):
  python scripts/qa_ai_live_matrix.py

Mặc định: AppTest smoke (không gọi Gemini). Thêm --live để ghi checklist thủ công.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

VN = timezone(timedelta(hours=7))


def apptest_test_smoke() -> dict:
    from streamlit.testing.v1 import AppTest

    report = {"mode": "apptest_smoke", "stations": {}, "ok": True}
    at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=120)
    at.secrets["ADMIN_PASS"] = "qa-matrix-pass"
    at.run()
    labels = [
        "📖 Trạm 1: Học Tập & Phòng Lab",
        "✍️ Trạm 2: Gia Sư Socratic & Nộp Bài",
        "📝 Trạm 3: Luyện Tập & Khảo Thí",
        "💚 Trạm 4: Tư Vấn Tâm Lý Học Đường",
        "📊 Trạm 5: Dữ Liệu & Nghiên Cứu",
    ]
    for lab in labels:
        at.session_state["selected_station"] = lab
        at.session_state["sb_station_radio_selector"] = lab
        at.run()
        exc = [e.message for e in at.exception][:2]
        report["stations"][lab] = {"exc": exc, "ok": not exc}
        if exc:
            report["ok"] = False
    # Unlock T5
    at.session_state["selected_station"] = labels[4]
    at.session_state["sb_station_radio_selector"] = labels[4]
    at.run()
    next(t for t in at.text_input if t.label == "Mật khẩu giáo viên:").set_value("qa-matrix-pass")
    next(b for b in at.button if "Mở khóa Trạm 5" in (b.label or "")).click().run()
    stay = at.session_state.get("selected_station") == labels[4]
    auth = bool(at.session_state.get("teacher_authenticated"))
    report["tram5_unlock"] = {"auth": auth, "stay_on_t5": stay}
    report["ok"] = report["ok"] and auth and stay
    return report


def live_checklist() -> dict:
    return {
        "mode": "manual_live_checklist",
        "items": [
            {"id": "T1", "task": "Soạn bài AI 1 môn (vd Toán 12)", "status": "TODO"},
            {"id": "T2", "task": "Chat Socratic + tên sidebar không Ẩn danh", "status": "TODO"},
            {"id": "T3", "task": "Bốc đề + chấm 1 câu (có Key)", "status": "TODO"},
            {"id": "T4", "task": "1 lượt tư vấn AI", "status": "TODO"},
            {"id": "T5", "task": "Mở khóa MK + xuất CSV nghiên cứu", "status": "TODO"},
        ],
        "note": "Điền PASS/FAIL trên UI local hoặc Cloud rồi commit evidence.",
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--live", action="store_true", help="Xuất checklist thủ công thay vì AppTest")
    args = p.parse_args()
    out_dir = ROOT / "qa_evidence"
    out_dir.mkdir(exist_ok=True)
    stamp = datetime.now(VN).strftime("%Y%m%d_%H%M%S")
    report = live_checklist() if args.live else apptest_test_smoke()
    report["generated_at"] = datetime.now(VN).isoformat()
    path = out_dir / f"ai_live_matrix_{stamp}.json"
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    print("WROTE", path)
    return 0 if report.get("ok", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())
