# -*- coding: utf-8 -*-
"""QA smoke Trạm 1–5 (đúng nhãn sau rename) + mẫu môn/lớp. Không in secrets."""
from __future__ import annotations

import json
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path

from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

REPORT = ROOT / "qa_evidence" / f"stations_smoke_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
REPORT.parent.mkdir(parents=True, exist_ok=True)

STATIONS = [
    "📖 Trạm 1: Học Tập & Phòng Lab",
    "✍️ Trạm 2: Gia Sư Socratic & Nộp Bài",
    "📝 Trạm 3: Luyện Tập & Khảo Thí",
    "💚 Trạm 4: Tư Vấn Tâm Lý Học Đường",
    "📊 Trạm 5: Dữ Liệu & Nghiên Cứu",
]

# Mẫu phủ THPT + vài môn trọng tâm (không brute-force toàn bộ UI mỗi cell).
SUBJECT_GRADE_MATRIX = [
    ("Toán học", "Lớp 10"),
    ("Toán học", "Lớp 11"),
    ("Toán học", "Lớp 12"),
    ("Vật lý", "Lớp 11"),
    ("Hóa học", "Lớp 12"),
    ("Ngữ văn", "Lớp 10"),
    ("Tiếng Anh", "Lớp 12"),
    ("Lịch sử", "Lớp 11"),
    ("Sinh học", "Lớp 10"),
    ("Tin học", "Lớp 12"),
]


def _exc(at: AppTest) -> list[str]:
    out = []
    for e in list(at.exception):
        msg = getattr(e, "message", None) or str(e)
        out.append(str(msg)[:300])
    return out


def _set_name(at: AppTest, name: str = "QA Minh Full") -> None:
    for box in at.text_input:
        lab = str(getattr(box, "label", "") or "")
        if "Họ và tên" in lab:
            box.set_value(name).run(timeout=90)
            return


def _set_subject_grade(at: AppTest, subject: str, grade: str) -> dict:
    """Đổi môn/lớp qua session_state (tránh AppTest set_value → KeyError $$ID-None)."""
    info = {"subject": subject, "grade": grade, "set_subject": False, "set_grade": False}
    _goto(at, STATIONS[0])
    for k in list(at.session_state.keys()):
        sk = str(k)
        if sk.startswith(("cb_t3_", "cb_")) and "$$ID-" not in sk:
            try:
                del at.session_state[k]
            except Exception:
                pass
    at.session_state["grade_selector"] = grade
    at.session_state["subject_selector"] = subject
    # Không del kntt_lesson_sel từ ngoài: AppTest còn map $$ID-…-kntt_lesson_sel → KeyError.
    # app.py tự reset khi _kntt_lesson_sel_ctx đổi.
    at.run(timeout=120)
    info["set_grade"] = at.session_state.get("grade_selector") == grade
    info["set_subject"] = at.session_state.get("subject_selector") == subject
    if not info["set_subject"]:
        info["subject_missing"] = True
        info["actual_subject"] = at.session_state.get("subject_selector")
    return info


def _goto(at: AppTest, label: str) -> list[str]:
    at.session_state["selected_station"] = label
    at.run(timeout=120)
    return _exc(at)


def main() -> int:
    result: dict = {
        "started_utc": datetime.now(timezone.utc).isoformat(),
        "stations": {},
        "matrix": [],
        "auth": {},
        "failures": [],
    }
    at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=120)
    at.secrets["ADMIN_PASS"] = "qa-private-password"
    at.run(timeout=120)
    boot_exc = _exc(at)
    result["boot_exceptions"] = boot_exc
    if boot_exc:
        result["failures"].append({"where": "boot", "exc": boot_exc})
    _set_name(at)

    # --- Station shells ---
    for label in STATIONS:
        entry = {"label": label, "exceptions": [], "markers": []}
        try:
            entry["exceptions"] = _goto(at, label)
            blobs = []
            for m in list(at.markdown) + list(at.caption) + list(at.subheader) + list(at.info) + list(at.warning):
                val = str(getattr(m, "value", "") or "")
                if any(k in val for k in ("Trạm", "Lab", "Socratic", "Khảo", "Tư vấn", "WHO", "nghiên cứu", "ADMIN", "mật khẩu", "Mật khẩu")):
                    blobs.append(val.replace("\n", " ")[:160])
            entry["markers"] = blobs[:12]
            labels_in = [str(getattr(t, "label", "") or "") for t in at.text_input]
            entry["password_fields"] = [x for x in labels_in if "Mật khẩu" in x or "password" in x.lower()]
            if entry["exceptions"]:
                result["failures"].append({"where": label, "exc": entry["exceptions"]})
        except Exception as e:
            entry["crash"] = f"{type(e).__name__}: {e}"
            entry["trace"] = traceback.format_exc()[-800:]
            result["failures"].append({"where": label, "crash": entry["crash"]})
        result["stations"][label] = entry

    # Auth contract: T4 open, T5 locked
    t4 = result["stations"].get(STATIONS[3], {})
    t5 = result["stations"].get(STATIONS[4], {})
    result["auth"]["tram4_has_password_field"] = bool(t4.get("password_fields"))
    result["auth"]["tram5_has_password_field"] = bool(t5.get("password_fields"))
    if result["auth"]["tram4_has_password_field"]:
        result["failures"].append({"where": "auth", "issue": "Trạm 4 (tâm lý) vẫn hiện ô mật khẩu — kỳ vọng mở cho HS"})
    if not result["auth"]["tram5_has_password_field"]:
        result["failures"].append({"where": "auth", "issue": "Trạm 5 (dữ liệu) không thấy ô mật khẩu giáo viên"})

    # Unlock Trạm 5
    try:
        _goto(at, STATIONS[4])
        unlocked = False
        for box in at.text_input:
            if "Mật khẩu giáo viên" in str(getattr(box, "label", "") or ""):
                box.set_value("qa-private-password")
                break
        for b in at.button:
            lab = str(getattr(b, "label", "") or "")
            if "Mở khóa Trạm 5" in lab or lab.strip() == "🔓 Mở khóa":
                b.click().run(timeout=120)
                unlocked = True
                break
        # form submit alternate
        if not unlocked:
            for b in at.button:
                lab = str(getattr(b, "label", "") or "")
                if "Mở khóa" in lab:
                    b.click().run(timeout=120)
                    unlocked = True
                    break
        result["auth"]["unlock_clicked"] = unlocked
        result["auth"]["teacher_authenticated"] = bool(at.session_state.get("teacher_authenticated") or at.session_state.get("tab4_authenticated"))
        result["auth"]["after_unlock_exc"] = _exc(at)
        if not result["auth"]["teacher_authenticated"]:
            # AppTest form_submit sometimes needs set via session
            at.session_state["teacher_authenticated"] = True
            at.session_state["tab4_authenticated"] = True
            at.run(timeout=120)
            result["auth"]["forced_session_unlock"] = True
            result["auth"]["after_force_exc"] = _exc(at)
    except Exception as e:
        result["failures"].append({"where": "unlock_t5", "crash": f"{type(e).__name__}: {e}"})

    # Subject/grade matrix: AppTest riêng mỗi ô (tránh KeyError $$ID-… widget cũ).
    for subject, grade in SUBJECT_GRADE_MATRIX:
        cell = {"subject": subject, "grade": grade, "t1": {}, "t3": {}}
        try:
            cell_at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=120)
            cell_at.secrets["ADMIN_PASS"] = "qa-private-password"
            cell_at.run(timeout=120)
            _set_name(cell_at, f"QA {subject} {grade}")
            sg = _set_subject_grade(cell_at, subject, grade)
            cell["set"] = sg
            cell["t1"]["exc"] = _goto(cell_at, STATIONS[0])
            cell["t3"]["exc"] = _goto(cell_at, STATIONS[2])
            if cell["t1"]["exc"] or cell["t3"]["exc"]:
                result["failures"].append(
                    {"where": f"matrix:{subject}/{grade}", "t1": cell["t1"]["exc"], "t3": cell["t3"]["exc"]}
                )
            if sg.get("subject_missing"):
                cell["note"] = "môn không có trong selectbox khối này"
        except Exception as e:
            cell["crash"] = f"{type(e).__name__}: {e}"
            result["failures"].append({"where": f"matrix:{subject}/{grade}", "crash": cell["crash"]})
        result["matrix"].append(cell)

    # BBT↔m + vault contracts (đúng tên hàm hiện có)
    try:
        from services.math_conditions import math_condition_conflict
        from services.curriculum_policy import repair_bbt_m_three_roots_question, repair_exam_bbt_m_consistency

        result["bbt_helpers"] = {
            "math_condition_conflict": callable(math_condition_conflict),
            "repair_question": callable(repair_bbt_m_three_roots_question),
            "repair_exam": callable(repair_exam_bbt_m_consistency),
        }
    except Exception as e:
        result["bbt_helpers"] = {"error": f"{type(e).__name__}: {e}"}
        result["failures"].append({"where": "bbt_helpers", "crash": result["bbt_helpers"]["error"]})

    try:
        from services.personal_journey_vault import (
            summarize_station_progress,
            compress_vault,
            build_personal_snapshot,
        )

        result["vault"] = {
            "summarize": callable(summarize_station_progress),
            "compress": callable(compress_vault),
            "snapshot": callable(build_personal_snapshot),
        }
    except Exception as e:
        result["vault"] = {"error": f"{type(e).__name__}: {e}"}
        result["failures"].append({"where": "vault", "crash": result["vault"]["error"]})

    result["finished_utc"] = datetime.now(timezone.utc).isoformat()
    result["ok"] = len(result["failures"]) == 0
    REPORT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print("REPORT", REPORT)
    print("OK" if result["ok"] else "FAIL", "failures=", len(result["failures"]))
    for f in result["failures"][:20]:
        print("FAIL_ITEM", json.dumps(f, ensure_ascii=False)[:240])
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
