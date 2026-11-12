# -*- coding: utf-8 -*-
"""Chỉ số tiến bộ Trạm 5 — giáo dục, 0đ, không công cụ bản quyền trả phí.

Bộ đo đã chốt:
1) WHO-5 (WHO, 2024) — CC BY-NC-SA 3.0 IGO, phi thương mại, ghi nguồn.
2) Check-in học đường GSAI (tự xây) — không sao chép SDQ/ORS.
3) Mục tiêu tuần 0–10 (kiểu GBO giáo dục).

Không phải chẩn đoán lâm sàng; không dùng điểm thi Trạm 3 làm outcome tâm lý.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

T1_CONTEXT_REVISION = 2026111226

VN_TZ = timezone(timedelta(hours=7))

WHO5_CITATION = (
    "World Health Organization. The World Health Organization-Five Well-Being Index (WHO-5). "
    "Geneva: World Health Organization; 2024. Licence: CC BY-NC-SA 3.0 IGO. "
    "WHO/UCN/MSD/MHE/2024.1"
)
WHO5_LICENSE = "CC BY-NC-SA 3.0 IGO"
WHO5_SOURCE_URL = (
    "https://www.who.int/publications/m/item/WHO-UCN-MSD-MHE-2024.01"
)

# Bản tiếng Anh là bản gốc ràng buộc (WHO).
WHO5_ITEMS_EN = (
    "I have felt cheerful and in good spirits",
    "I have felt calm and relaxed",
    "I have felt active and vigorous",
    "I woke up feeling fresh and rested",
    "My daily life has been filled with things that interest me",
)

# Bản Việt cho HS phổ thông — KHÔNG do WHO tạo; kèm disclaimer bắt buộc.
WHO5_ITEMS_VI = (
    "Em cảm thấy vui vẻ và tinh thần phấn chấn",
    "Em cảm thấy bình tĩnh và thư giãn",
    "Em cảm thấy năng động và tràn đầy sinh lực",
    "Em thức dậy cảm thấy sảng khoái và được nghỉ ngơi đầy đủ",
    "Cuộc sống hằng ngày của em tràn ngập những điều khiến em quan tâm",
)

WHO5_VI_DISCLAIMER = (
    "Bản dịch tiếng Việt này không do Tổ chức Y tế Thế giới (WHO) tạo. "
    "WHO không chịu trách nhiệm về nội dung hay độ chính xác của bản dịch. "
    "Bản tiếng Anh gốc là bản ràng buộc và xác thực."
)

WHO5_SCALE_VI = (
    (5, "Mọi lúc"),
    (4, "Hầu hết thời gian"),
    (3, "Hơn một nửa thời gian"),
    (2, "Ít hơn một nửa thời gian"),
    (1, "Thỉnh thoảng"),
    (0, "Không lúc nào"),
)

# Check-in học đường tự xây (GSAI) — không phải SDQ/ORS.
SCHOOL_CHECKIN_ITEMS = (
    ("sleep_rest", "Em ngủ nghỉ đủ để học hôm nay?", False),
    ("study_pressure", "Áp lực học/thi hôm nay của em?", True),  # inverted
    ("peer_safety", "Em cảm thấy an toàn với bạn bè / lớp hôm nay?", False),
    ("self_confidence", "Em tự tin xử lý việc học hôm nay?", False),
    ("help_seeking", "Em sẵn sàng nhờ người lớn tin cậy nếu cần?", False),
)

OUTCOME_EVENT_TYPE = "COUNSELING_OUTCOME_CHECKIN"
BUNDLE_ID = "who5_nc__gsai_school_checkin_v1__weekly_goal"


def now_vn_iso() -> str:
    return datetime.now(VN_TZ).strftime("%Y-%m-%d %H:%M:%S")


def who5_attribution_md() -> str:
    return (
        f"**WHO-5** — chỉ số hạnh phúc chủ quan (5 câu, 2 tuần gần nhất).  \n"
        f"Nguồn: {WHO5_CITATION}  \n"
        f"Dùng phi thương mại / giáo dục theo {WHO5_LICENSE}; không hàm ý WHO xác nhận app này.  \n"
        f"{WHO5_VI_DISCLAIMER}  \n"
        f"Đây là theo dõi tiến bộ học đường, **không** phải chẩn đoán bệnh."
    )


def score_who5(item_scores: Sequence[Any]) -> Dict[str, Any]:
    """item_scores: 5 giá trị 0–5. raw 0–25; percent = raw*4 (0–100)."""
    vals: List[int] = []
    for x in list(item_scores)[:5]:
        try:
            v = int(x)
        except (TypeError, ValueError):
            raise ValueError("who5_item_not_int")
        if v < 0 or v > 5:
            raise ValueError("who5_item_out_of_range")
        vals.append(v)
    if len(vals) != 5:
        raise ValueError("who5_need_five_items")
    raw = sum(vals)
    percent = raw * 4
    return {
        "instrument": "WHO-5",
        "license": WHO5_LICENSE,
        "citation": WHO5_CITATION,
        "source_url": WHO5_SOURCE_URL,
        "items_en": list(WHO5_ITEMS_EN),
        "items_vi_school": list(WHO5_ITEMS_VI),
        "vi_translation_disclaimer": WHO5_VI_DISCLAIMER,
        "item_scores": vals,
        "raw_0_25": raw,
        "percent_0_100": percent,
        "below_screening_hint_50": percent < 50,
        "interpretation_note": (
            "Điểm càng cao càng phản ánh wellbeing chủ quan tốt hơn trong 2 tuần. "
            "Ngưỡng gợi ý theo tài liệu WHO: dưới 50 có thể cần hỗ trợ thêm / hỏi người lớn tin cậy "
            "(không phải chẩn đoán)."
        ),
    }


def score_school_checkin(answers: Dict[str, Any]) -> Dict[str, Any]:
    """Thang 0–10 từng mục; áp lực học bị đảo để tổng wellbeing học đường."""
    scored: Dict[str, float] = {}
    contrib: List[float] = []
    for key, _label, invert in SCHOOL_CHECKIN_ITEMS:
        try:
            v = float(answers.get(key))
        except (TypeError, ValueError):
            raise ValueError(f"school_checkin_missing_{key}")
        if v < 0 or v > 10:
            raise ValueError(f"school_checkin_range_{key}")
        scored[key] = v
        contrib.append(10.0 - v if invert else v)
    mean = sum(contrib) / len(contrib)
    return {
        "instrument": "GSAI_SCHOOL_CHECKIN_V1",
        "license": "GSAI educational original; not SDQ/ORS",
        "answers_0_10": scored,
        "wellbeing_index_0_10": round(mean, 2),
        "items": [
            {"key": k, "label": lab, "inverted": inv}
            for k, lab, inv in SCHOOL_CHECKIN_ITEMS
        ],
    }


def score_weekly_goal(text: str, progress: Any) -> Dict[str, Any]:
    try:
        p = float(progress)
    except (TypeError, ValueError):
        raise ValueError("weekly_goal_progress_invalid")
    if p < 0 or p > 10:
        raise ValueError("weekly_goal_progress_range")
    goal = str(text or "").strip()[:240]
    if not goal:
        raise ValueError("weekly_goal_empty")
    return {
        "instrument": "GSAI_WEEKLY_GOAL_V1",
        "license": "GSAI educational original (GBO-style)",
        "goal_text": goal,
        "progress_0_10": p,
    }


def build_outcome_checkin(
    *,
    student_name: str,
    grade: Any,
    subject: str,
    phase: str,
    who5_scores: Optional[Sequence[Any]] = None,
    school_answers: Optional[Dict[str, Any]] = None,
    weekly_goal_text: str = "",
    weekly_goal_progress: Any = None,
    theme_key: str = "",
    theme_label: str = "",
) -> Dict[str, Any]:
    """Tạo sự kiện COUNSELING_OUTCOME_CHECKIN đưa sang Trạm 4."""
    phase_n = str(phase or "session").strip().casefold()
    if phase_n in {"đầu đợt", "dau dot", "pre_test", "baseline"}:
        phase_n = "pre"
    elif phase_n in {"cuối đợt", "cuoi dot", "post_test", "endline"}:
        phase_n = "post"
    elif phase_n not in {"session", "pre", "post"}:
        phase_n = "session"

    payload: Dict[str, Any] = {
        "type": OUTCOME_EVENT_TYPE,
        "event_id": f"outcome-{now_vn_iso().replace(' ', 'T').replace(':', '')}",
        "time": now_vn_iso(),
        "name": student_name,
        "grade": str(grade),
        "subject": subject,
        "theme_key": theme_key,
        "theme_label": theme_label,
        "phase": phase_n,
        "bundle_id": BUNDLE_ID,
        "philosophy": "Duong thien tam - Uom nhan tai",
        "station_from": 5,
        "station_to": 4,
        "not_clinical_diagnosis": True,
        "fee_note": "educational_free_stack__no_paid_rom_license",
    }
    if who5_scores is not None:
        payload["who5"] = score_who5(who5_scores)
    if school_answers is not None:
        payload["school_checkin"] = score_school_checkin(school_answers)
    if weekly_goal_text or weekly_goal_progress is not None:
        payload["weekly_goal"] = score_weekly_goal(weekly_goal_text, weekly_goal_progress)
    if "who5" not in payload and "school_checkin" not in payload and "weekly_goal" not in payload:
        raise ValueError("outcome_empty")
    return payload


def outcome_events(logs: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [
        e for e in (logs or [])
        if isinstance(e, dict) and e.get("type") == OUTCOME_EVENT_TYPE
    ]


def _student_key(event: Dict[str, Any]) -> str:
    name = str(event.get("name") or event.get("student_name") or "").strip()
    grade = str(event.get("grade") or "").strip()
    subject = str(event.get("subject") or "").strip()
    return f"{name}|{grade}|{subject}"


def collect_who5_pre_post_pairs(logs: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Ghép WHO-5 pre/post theo học sinh (+lớp+môn). Không suy nhân quả."""
    buckets: Dict[str, Dict[str, Any]] = {}
    for event in outcome_events(logs):
        who5 = event.get("who5")
        if not isinstance(who5, dict):
            continue
        percent = who5.get("percent_0_100")
        if percent is None:
            continue
        phase = str(event.get("phase") or "").casefold()
        if phase not in {"pre", "post"}:
            continue
        key = _student_key(event)
        if not key.startswith("|"):
            slot = buckets.setdefault(key, {"key": key, "name": event.get("name"),
                                            "grade": event.get("grade"),
                                            "subject": event.get("subject")})
            # giữ bản mới nhất theo thời gian chuỗi
            prev_t = str(slot.get(f"{phase}_time") or "")
            cur_t = str(event.get("time") or "")
            if cur_t >= prev_t:
                slot[f"{phase}_percent"] = float(percent)
                slot[f"{phase}_raw"] = who5.get("raw_0_25")
                slot[f"{phase}_time"] = cur_t
    pairs = []
    for slot in buckets.values():
        if "pre_percent" in slot and "post_percent" in slot:
            delta = float(slot["post_percent"]) - float(slot["pre_percent"])
            pairs.append({
                **slot,
                "delta_percent": round(delta, 2),
                "improved": delta > 0,
            })
    return pairs


def summarize_who5_pairs(pairs: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    if not pairs:
        return {"n_pairs": 0, "mean_pre": None, "mean_post": None,
                "mean_delta": None, "improved_share": None}
    n = len(pairs)
    mean_pre = sum(float(p["pre_percent"]) for p in pairs) / n
    mean_post = sum(float(p["post_percent"]) for p in pairs) / n
    mean_delta = sum(float(p["delta_percent"]) for p in pairs) / n
    improved = sum(1 for p in pairs if p.get("improved")) / n
    return {
        "n_pairs": n,
        "mean_pre": round(mean_pre, 2),
        "mean_post": round(mean_post, 2),
        "mean_delta": round(mean_delta, 2),
        "improved_share": round(improved, 3),
    }


def session_checkin_trend(logs: Iterable[Dict[str, Any]], student_name: str = "") -> List[Dict[str, Any]]:
    """Chuỗi wellbeing học đường theo phiên (check-in GSAI)."""
    name = str(student_name or "").strip()
    rows = []
    for event in outcome_events(logs):
        if name and str(event.get("name") or "").strip() != name:
            continue
        sc = event.get("school_checkin")
        if not isinstance(sc, dict):
            continue
        rows.append({
            "time": event.get("time"),
            "phase": event.get("phase"),
            "wellbeing_index_0_10": sc.get("wellbeing_index_0_10"),
            "weekly_goal_progress": (event.get("weekly_goal") or {}).get("progress_0_10"),
            "who5_percent": (event.get("who5") or {}).get("percent_0_100"),
        })
    rows.sort(key=lambda r: str(r.get("time") or ""))
    return rows
