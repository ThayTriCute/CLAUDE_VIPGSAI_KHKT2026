# -*- coding: utf-8 -*-
"""Hồ sơ hành trình cá nhân trên thiết bị + xuất nghiên cứu an toàn.

- Người dùng: lưu/nén/khôi phục/xóa ngữ cảnh & tiến bộ Trạm 1–5 trên thiết bị
  (file .gsai.xz tải về / mở lại; không bắt buộc đám mây).
- GV / chủ dự án: minh bạch học thuật–nghiên cứu qua bản đã ẩn danh / rút PII;
  không lộ nội dung tư vấn thô, secrets, API key.

Không thay thế đồng ý đạo đức nghiên cứu của nhà trường; chỉ là lớp kỹ thuật.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import lzma
import re
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

T1_CONTEXT_REVISION = 2026111229

VN_TZ = timezone(timedelta(hours=7))
VAULT_TYPE = "GSAI_PERSONAL_JOURNEY_VAULT_V1"
VAULT_VERSION = 3
LOCALSTORAGE_KEY = "gsai_personal_vault_v1"
MAX_VAULT_BYTES = 2 * 1024 * 1024
YEAR_RETENTION_DAYS = 365
MAX_CONTINUITY_NOTES = 12
MAX_SEMESTER_CARDS = 6
MAX_YEAR_DIGESTS = 3  # đủ đánh giá trọn 3 năm thanh xuân THPT (lớp 10–11–12)

SCHOOL_NAME = "Trường THPT Tân Hiệp"
SCHOOL_PROVINCE = "An Giang"
SCHOOL_MOTTO = "Dưỡng thiện tâm – Ươm nhân tài"
SCHOOL_AUTHOR = "Thầy Phan Minh Trí"

# Chính sách tối ưu (không xóa sạch mỗi HK):
# - Trong HK: giữ đầy đủ trên thiết bị (hot).
# - Sang HK mới / cuối HK: compact — bỏ thô dài, GIỮ thẻ HK + ghi chú tiếp nối (warm).
# - Sau ~1 năm học: xóa sự kiện thô, GIỮ year_continuity_digest → xếp vào hành trình 3 năm.
# - Cuối lớp 12: seal thpt_youth_arc + lời chào tạm biệt / dặn dò / triết lý hành trang.
RETENTION_POLICY = {
    "id": "GSAI_DEVICE_RETENTION_V2_THPT3Y",
    "semester_action": "compact_keep_continuity",  # KHÔNG hard-delete mỗi HK
    "year_action": "purge_raw_keep_continuity_digest",
    "thpt_arc_years": MAX_YEAR_DIGESTS,
    "year_retention_days": YEAR_RETENTION_DAYS,
    "graduation_action": "seal_farewell_keep_philosophy",
    "school": SCHOOL_NAME,
    "rationale_vi": (
        "Xóa sạch mỗi học kỳ làm gãy chuỗi đánh giá cả năm và cả 3 năm THPT. "
        "Tối ưu: nén cuối HK + ghi chú tiếp nối; sau mỗi năm xóa thô nhưng giữ digest; "
        "cuối cấp seal hành trình 3 năm kèm lời chào tạm biệt & triết lý hành trang khi rời "
        f"{SCHOOL_NAME}."
    ),
}

# Khóa session có thể xóa khi người dùng yêu cầu xóa hồ sơ trên thiết bị.
PURGEABLE_SESSION_KEYS = (
    "analytics_logs",
    "feedback_logs",
    "counseling_logs",
    "counseling_messages",
    "messages",
    "va_loi_logs",
    "parsed_quiz",
    "quiz_states",
    "quiz_selections",
    "current_lesson",
    "current_topic",
    "lab_data",
    "exam_answers",
    "exam_context",
    "tram3_chat_messages",
    "pending_sync",
    "personal_vault_last",
    "personal_vault_delta",
    "personal_continuity_notes",
    "personal_year_digest",
    "personal_thpt_arc",
    "personal_farewell",
)

_SENSITIVE_KEYS = frozenset({
    "user_excerpt", "assistant_excerpt", "journey_context", "detail",
    "answers", "answers_json", "api_key", "password", "token", "_token",
    "GEMINI_API_KEY", "SUPABASE_KEY", "SHEET_WEBHOOK_TOKEN",
})


def now_vn_iso() -> str:
    return datetime.now(VN_TZ).strftime("%Y-%m-%d %H:%M:%S")


def _parse_vn_dt(value: Any) -> Optional[datetime]:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=VN_TZ)
    text = str(value).strip()
    if not text:
        return None
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
        try:
            dt = datetime.strptime(text[:19] if "T" in text or " " in text else text[:10], fmt)
            return dt.replace(tzinfo=VN_TZ)
        except ValueError:
            continue
    return None


def vn_school_calendar(when: Optional[datetime] = None) -> Dict[str, Any]:
    """Năm học VN: HK1 ~ tháng 8–12; HK2 ~ tháng 1–7 (gần đúng lịch phổ thông)."""
    dt = when or datetime.now(VN_TZ)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=VN_TZ)
    if dt.month >= 8:
        start_year = dt.year
        semester = "HK1"
    else:
        start_year = dt.year - 1
        semester = "HK2"
    school_year = f"{start_year}-{start_year + 1}"
    return {
        "school_year": school_year,
        "semester": semester,
        "as_of": dt.strftime("%Y-%m-%d"),
        "start_year": start_year,
    }


def research_code(name: str, grade: Any = "", salt: str = "gsai-edu-2026") -> str:
    """Mã nghiên cứu một chiều — không đảo ngược ra họ tên."""
    raw = f"{salt}|{str(name or '').strip().casefold()}|{str(grade or '').strip()}"
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:12]
    return f"HS-{digest}"


def _event_station(event: Dict[str, Any]) -> int:
    t = str(event.get("type") or "")
    if t in {"LESSON_GENERATED", "LAB_RUN"} or event.get("station") == 1:
        return 1
    if t == "SOCRATIC_DIAGNOSTIC" or event.get("station") == 2:
        return 2
    if t == "EXAM_RESULT" or event.get("station") == 3:
        return 3
    # Counseling/outcome metrics feed vault keys tram5_* (research-bound).
    # Provenance on packets is station_from=4 → station_to=5 (UI); do not trust legacy swapped fields.
    if t in {"SCHOOL_COUNSELING_SESSION", "COUNSELING_OUTCOME_CHECKIN"}:
        return 5
    if t.startswith("RESEARCH") or event.get("station") == 5 or event.get("station_to") == 5:
        return 5
    if event.get("station") == 4:
        return 4
    return 0


def _score_of(event: Dict[str, Any]) -> Optional[float]:
    try:
        v = float(event.get("score"))
    except (TypeError, ValueError):
        return None
    if 0 <= v <= 10:
        return v
    return None


def summarize_station_progress(logs: Iterable[Dict[str, Any]], *, name: str = "") -> Dict[str, Any]:
    """Tóm tắt tiến bộ / thụt lùi theo trạm cho một cá nhân (theo tên hiển thị phiên)."""
    name_n = str(name or "").strip()
    by_station: Dict[int, List[Dict[str, Any]]] = {1: [], 2: [], 3: [], 4: [], 5: []}
    for event in logs or []:
        if not isinstance(event, dict):
            continue
        if name_n and str(event.get("name") or event.get("student_name") or "").strip() not in {name_n, ""}:
            # keep unnamed session events for current user if name matches or event has no name
            ename = str(event.get("name") or event.get("student_name") or "").strip()
            if ename and ename != name_n:
                continue
        stn = _event_station(event)
        if stn in by_station:
            by_station[stn].append(event)

    exam_scores = [_score_of(e) for e in by_station[3]]
    exam_scores = [s for s in exam_scores if s is not None]
    who5_percents = []
    for e in by_station[5]:
        who5 = e.get("who5") if isinstance(e.get("who5"), dict) else None
        if who5 and who5.get("percent_0_100") is not None:
            who5_percents.append(float(who5["percent_0_100"]))
        elif e.get("type") == "COUNSELING_OUTCOME_CHECKIN":
            w = e.get("who5") or {}
            if isinstance(w, dict) and w.get("percent_0_100") is not None:
                who5_percents.append(float(w["percent_0_100"]))

    def _trend(values: Sequence[float]) -> str:
        if len(values) < 2:
            return "insufficient_data"
        delta = values[-1] - values[0]
        if delta >= 0.5:
            return "progress"
        if delta <= -0.5:
            return "regress"
        return "stable"

    t3_trend = _trend(exam_scores)
    t5_trend = _trend([p / 10.0 for p in who5_percents])  # scale for same threshold spirit

    return {
        "tram1_events": len(by_station[1]),
        "tram2_diagnostics": len(by_station[2]),
        "tram3_exams": len(exam_scores),
        "tram3_scores": exam_scores[-12:],
        "tram3_trend": t3_trend,
        "tram3_last_score": exam_scores[-1] if exam_scores else None,
        "tram3_delta_first_last": (
            round(exam_scores[-1] - exam_scores[0], 2) if len(exam_scores) >= 2 else None
        ),
        "tram5_sessions": sum(1 for e in by_station[5] if e.get("type") == "SCHOOL_COUNSELING_SESSION"),
        "tram5_outcomes": sum(1 for e in by_station[5] if e.get("type") == "COUNSELING_OUTCOME_CHECKIN"),
        "tram5_who5_percents": who5_percents[-8:],
        "tram5_trend": t5_trend if who5_percents else "insufficient_data",
        "tram5_who5_delta": (
            round(who5_percents[-1] - who5_percents[0], 2) if len(who5_percents) >= 2 else None
        ),
        "weak_topics": _weak_topics(by_station[2]),
    }


def _weak_topics(diagnostics: Sequence[Dict[str, Any]], limit: int = 8) -> List[Dict[str, Any]]:
    counts: Dict[str, int] = {}
    for e in diagnostics:
        topic = str(e.get("topic") or "").strip()
        if topic:
            counts[topic] = counts.get(topic, 0) + 1
    ranked = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    return [{"topic": t, "count": c} for t, c in ranked[:limit]]


def build_personal_snapshot(
    *,
    student_name: str,
    grade: Any,
    subject: str,
    analytics_logs: Optional[List[Dict[str, Any]]] = None,
    counseling_logs: Optional[List[Dict[str, Any]]] = None,
    feedback_logs: Optional[List[Dict[str, Any]]] = None,
    tram_counts: Optional[Dict[str, int]] = None,
    current_topic: str = "",
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    logs = list(analytics_logs or []) + list(counseling_logs or [])
    # Prefer counseling_logs already inside analytics; dedupe by event_id
    seen = set()
    deduped = []
    for e in logs:
        if not isinstance(e, dict):
            continue
        eid = e.get("event_id") or e.get("id") or json.dumps(e, sort_keys=True, default=str)[:120]
        if eid in seen:
            continue
        seen.add(eid)
        deduped.append(_minify_event_for_vault(e))

    progress = summarize_station_progress(deduped, name=student_name)
    cal = vn_school_calendar()
    prior = (extra or {}).get("prior_vault") if isinstance(extra, dict) else None
    prior_cards = list((prior or {}).get("semester_cards") or []) if isinstance(prior, dict) else []
    prior_notes = list((prior or {}).get("continuity_notes") or []) if isinstance(prior, dict) else []
    prior_year = (prior or {}).get("year_continuity_digest") if isinstance(prior, dict) else None
    prior_years = list((prior or {}).get("thpt_year_digests") or []) if isinstance(prior, dict) else []
    prior_arc = (prior or {}).get("thpt_youth_arc") if isinstance(prior, dict) else None
    prior_farewell = (prior or {}).get("farewell") if isinstance(prior, dict) else None
    continuity_notes = list(prior_notes)
    snap = {
        "type": VAULT_TYPE,
        "version": VAULT_VERSION,
        "created_at": now_vn_iso(),
        "device_scope": "personal_device_only",
        "identity": {
            "display_name": str(student_name or "Ẩn danh"),
            "grade": str(grade),
            "subject": str(subject),
            "research_code": research_code(student_name, grade),
        },
        "tram_counts": dict(tram_counts or {}),
        "current_topic": str(current_topic or "")[:200],
        "progress": progress,
        "events": deduped[-200:],  # bound size
        "feedback_n": len(feedback_logs or []),
        "calendar": cal,
        "retention": dict(RETENTION_POLICY),
        "semester_cards": prior_cards[-MAX_SEMESTER_CARDS:],
        "continuity_notes": continuity_notes[-MAX_CONTINUITY_NOTES:],
        "year_continuity_digest": prior_year,
        "thpt_year_digests": prior_years[-MAX_YEAR_DIGESTS:],
        "thpt_youth_arc": prior_arc,
        "farewell": prior_farewell,
        "ethics": {
            "purpose": "personal_learning_continuity_on_device",
            "not_clinical_record": True,
            "user_may_export_or_delete": True,
            "semester_policy": "compact_not_hard_delete",
            "year_policy": "purge_raw_keep_continuity",
            "thpt_arc": "3_year_moments_and_farewell",
        },
    }
    if extra:
        # prior_vault chỉ dùng nội bộ khi dựng; không nhúng lại cả vault cũ
        clean_extra = {k: v for k, v in extra.items() if k != "prior_vault"}
        if clean_extra:
            snap["extra"] = clean_extra
    snap["content_sha256"] = _vault_hash(snap)
    return snap


def _vault_hash(snap: Dict[str, Any]) -> str:
    return hashlib.sha256(
        json.dumps({k: snap[k] for k in snap if k != "content_sha256"}, ensure_ascii=False, sort_keys=True, default=str).encode()
    ).hexdigest()


def _minify_event_for_vault(event: Dict[str, Any]) -> Dict[str, Any]:
    """Giữ tín hiệu tiến bộ; rút gọn nội dung nhạy cảm trên thiết bị cá nhân."""
    e = dict(event)
    # Truncate long text fields
    for key in ("user_excerpt", "assistant_excerpt", "journey_context", "detail", "current_lesson"):
        if key in e and isinstance(e[key], str) and len(e[key]) > 400:
            e[key] = e[key][:400] + "…"
    if isinstance(e.get("answers"), dict):
        # keep item results flags only
        ir = e["answers"].get("_item_results") if isinstance(e["answers"], dict) else None
        e["answers"] = {"_item_results": ir} if ir is not None else {"_omitted": True}
    return e


def compare_snapshots(previous: Optional[Dict[str, Any]], current: Dict[str, Any]) -> Dict[str, Any]:
    """Đối chiếu tiến bộ / thụt lùi giữa hai bản lưu thiết bị."""
    prev_p = (previous or {}).get("progress") or {}
    cur_p = (current or {}).get("progress") or {}
    notes = []

    def _side(label, prev_t, cur_t, prev_d, cur_d):
        if cur_t == "progress":
            notes.append(f"{label}: tiến bộ" + (f" (Δ={cur_d})" if cur_d is not None else ""))
        elif cur_t == "regress":
            notes.append(f"{label}: thụt lùi" + (f" (Δ={cur_d})" if cur_d is not None else ""))
        elif cur_t == "stable":
            notes.append(f"{label}: ổn định")
        elif prev_t and cur_t == "insufficient_data":
            notes.append(f"{label}: chưa đủ dữ liệu")

    _side(
        "Trạm 3 (điểm)",
        prev_p.get("tram3_trend"),
        cur_p.get("tram3_trend"),
        prev_p.get("tram3_delta_first_last"),
        cur_p.get("tram3_delta_first_last"),
    )
    _side(
        "Trạm 5 (WHO-5)",
        prev_p.get("tram5_trend"),
        cur_p.get("tram5_trend"),
        prev_p.get("tram5_who5_delta"),
        cur_p.get("tram5_who5_delta"),
    )
    return {
        "compared_at": now_vn_iso(),
        "notes": notes,
        "previous_created_at": (previous or {}).get("created_at"),
        "current_created_at": current.get("created_at"),
        "tram3_trend": cur_p.get("tram3_trend"),
        "tram5_trend": cur_p.get("tram5_trend"),
    }


def build_period_reflection(
    *,
    scope: str,
    progress: Optional[Dict[str, Any]] = None,
    cal: Optional[Dict[str, Any]] = None,
    grade: Any = "",
    subject: str = "",
    user_lookback: str = "",
    user_lesson: str = "",
    user_comment: str = "",
    user_confidence: str = "",
    user_direction: str = "",
) -> Dict[str, Any]:
    """Nhìn lại → rút kinh nghiệm → nhận xét → thúc đẩy tự tin → hướng đi tiếp.

    scope: 'semester' | 'year'
    """
    progress = progress or {}
    cal = cal or vn_school_calendar()
    t3 = progress.get("tram3_trend")
    t5 = progress.get("tram5_trend")
    last = progress.get("tram3_last_score")
    d3 = progress.get("tram3_delta_first_last")
    d5 = progress.get("tram5_who5_delta")
    weak = list(progress.get("weak_topics") or [])[:3]
    weak_txt = ", ".join(str(w.get("topic")) for w in weak if isinstance(w, dict) and w.get("topic"))

    period = (
        f"{cal.get('school_year')} · {cal.get('semester')}"
        if scope == "semester"
        else f"Năm học {cal.get('school_year')}"
    )
    gnum = _grade_num(grade)

    lookback_bits = [f"Giai đoạn: {period}"]
    if subject:
        lookback_bits.append(f"môn trọng tâm: {subject}")
    if last is not None:
        lookback_bits.append(f"điểm Trạm 3 gần nhất: {last}")
    if d3 is not None:
        lookback_bits.append(
            f"Δ điểm: {d3:+.2f}" if isinstance(d3, (int, float)) else f"Δ điểm: {d3}"
        )
    if d5 is not None:
        lookback_bits.append(
            f"Δ WHO-5: {d5:+.0f}" if isinstance(d5, (int, float)) else f"Δ WHO-5: {d5}"
        )
    if t3:
        lookback_bits.append(f"xu hướng học lực: {t3}")
    if t5:
        lookback_bits.append(f"xu hướng tinh thần học đường: {t5}")
    auto_lookback = "; ".join(lookback_bits)

    lessons = []
    if t3 == "progress":
        lessons.append("Cách học đang hiệu quả — giữ nhịp ôn–làm–chữa lỗi, đừng đổi hết phương pháp.")
    elif t3 == "regress":
        lessons.append("Thụt lùi là tín hiệu điều chỉnh: giảm lan man, chọn 1–2 chủ đề yếu để gỡ sâu.")
    elif t3 == "stable":
        lessons.append("Ổn định là nền — muốn bứt phá cần thêm vòng luyện có phản hồi (Trạm 2→3).")
    else:
        lessons.append("Chưa đủ dữ liệu điểm: hãy hoàn thành thêm bài Trạm 3 (pre/post) để soi rõ hơn.")
    if weak_txt:
        lessons.append(f"Chủ đề cần ưu tiên gỡ: {weak_txt}.")
    if t5 == "regress" or (isinstance(d5, (int, float)) and d5 <= -5):
        lessons.append("Sức khỏe tinh thần đang cần chăm: ngủ đủ, chia nhỏ mục tiêu, biết nhờ người lớn tin cậy.")
    elif t5 == "progress" or (isinstance(d5, (int, float)) and d5 >= 5):
        lessons.append("Tinh thần đang sáng hơn — giữ thói quen check-in và nghỉ ngơi có chủ đích.")

    if t3 == "progress" and (t5 in {"progress", "stable", "insufficient_data", None}):
        comment = "Em đang chứng minh sự tiến bộ bằng việc làm cụ thể. Đó là bản lĩnh, không phải may rủi."
    elif t3 == "regress":
        comment = "Một giai đoạn khó không định nghĩa cả năm. Em đã có dữ liệu để sửa đường đi — đó là điểm mạnh."
    elif t3 == "stable":
        comment = "Em giữ được nhịp đều. Hãy chọn một mục tiêu nhỏ đủ rõ để biến ổn định thành tiến bộ."
    else:
        comment = "Mỗi lần mở app và chịu khó ghi nhận tiến trình là một bước tự chịu trách nhiệm với tương lai của mình."

    confidence = [
        "Em không cần hoàn hảo — chỉ cần **tiến bộ có phương pháp**.",
        "Sai ở Trạm 2–3 là bản đồ, không phải bản án.",
        f"Khẩu hiệu chân trang: «{SCHOOL_MOTTO}».",
    ]
    if last is not None and isinstance(last, (int, float)) and last >= 7:
        confidence.append("Điểm gần đây cho thấy năng lực đang hiện rõ — hãy tin vào quy trình của mình.")
    if t3 == "progress":
        confidence.append("Em đã làm được lần này thì làm được lần sau — giữ đúng thói quen đã thắng.")

    next_scope = "học kỳ tới" if scope == "semester" else "năm học tới"
    if gnum == 10:
        direction = (
            f"Hướng {next_scope}: dựng thói quen tự học bền (mỗi tuần 1 vòng Trạm1→2→3); "
            "ghi chú 3 lỗi lặp lại để không mang sang giai đoạn sau."
        )
    elif gnum == 11:
        direction = (
            f"Hướng {next_scope}: đào sâu chủ đề yếu, tăng bài pre–post; "
            "giữ check-in tinh thần để không đánh đổi sức khỏe lấy điểm."
        )
    elif gnum == 12:
        direction = (
            f"Hướng {next_scope}: chốt hành trang tốt nghiệp — ôn theo ma trận lỗi cá nhân, "
            "giữ nhịp nghỉ, nhớ triết lý tử tế có năng lực khi ra đời."
        )
    else:
        direction = (
            f"Hướng {next_scope}: chọn 1 mục tiêu học lực + 1 mục tiêu sức khỏe tinh thần; "
            "đo lại bằng Trạm 3 và WHO-5."
        )
    if weak_txt:
        direction += f" Ưu tiên: {weak_txt}."

    reflection = {
        "type": "GSAI_PERIOD_REFLECTION_V1",
        "scope": scope,
        "period_label": period,
        "school_year": cal.get("school_year"),
        "semester": cal.get("semester") if scope == "semester" else None,
        "created_at": now_vn_iso(),
        "lookback": (user_lookback.strip()[:500] if user_lookback.strip() else auto_lookback),
        "lookback_auto": auto_lookback,
        "lessons": ([user_lesson.strip()[:400]] if user_lesson.strip() else lessons)[:4],
        "lessons_auto": lessons[:4],
        "comment": (user_comment.strip()[:400] if user_comment.strip() else comment),
        "comment_auto": comment,
        "confidence_boost": (
            [user_confidence.strip()[:300]] if user_confidence.strip() else confidence
        )[:4],
        "confidence_auto": confidence[:4],
        "next_direction": (user_direction.strip()[:500] if user_direction.strip() else direction),
        "next_direction_auto": direction,
        "signals": {
            "tram3_trend": t3,
            "tram5_trend": t5,
            "tram3_last_score": last,
            "tram3_delta": d3,
            "tram5_who5_delta": d5,
            "weak_topics": weak,
        },
        "reflection_md": "",
    }
    reflection["reflection_md"] = "\n".join([
        f"### Nhìn lại — {period}",
        reflection["lookback"],
        "",
        "### Rút kinh nghiệm",
        *[f"- {x}" for x in reflection["lessons"]],
        "",
        "### Nhận xét",
        reflection["comment"],
        "",
        "### Thúc đẩy tự tin",
        *[f"- {x}" for x in reflection["confidence_boost"]],
        "",
        "### Hướng đi tiếp theo",
        reflection["next_direction"],
    ])
    return reflection

def build_semester_card(
    vault: Dict[str, Any],
    *,
    user_lookback: str = "",
    user_lesson: str = "",
    user_comment: str = "",
    user_confidence: str = "",
    user_direction: str = "",
) -> Dict[str, Any]:
    """Thẻ học kỳ: tín hiệu + reflection (nhìn lại / KN / nhận xét / tự tin / hướng đi)."""
    cal = vault.get("calendar") or vn_school_calendar()
    progress = vault.get("progress") or {}
    identity = vault.get("identity") or {}
    reflection = build_period_reflection(
        scope="semester",
        progress=progress,
        cal=cal,
        grade=identity.get("grade"),
        subject=str(identity.get("subject") or ""),
        user_lookback=user_lookback,
        user_lesson=user_lesson,
        user_comment=user_comment,
        user_confidence=user_confidence,
        user_direction=user_direction,
    )
    return {
        "school_year": cal.get("school_year"),
        "semester": cal.get("semester"),
        "sealed_at": now_vn_iso(),
        "research_code": identity.get("research_code"),
        "grade": identity.get("grade"),
        "subject": identity.get("subject"),
        "tram3_trend": progress.get("tram3_trend"),
        "tram3_last_score": progress.get("tram3_last_score"),
        "tram3_delta_first_last": progress.get("tram3_delta_first_last"),
        "tram5_trend": progress.get("tram5_trend"),
        "tram5_who5_delta": progress.get("tram5_who5_delta"),
        "tram5_who5_percents": list(progress.get("tram5_who5_percents") or [])[-4:],
        "weak_topics": list(progress.get("weak_topics") or [])[:5],
        "tram_counts": dict(vault.get("tram_counts") or {}),
        "event_n": len(vault.get("events") or []),
        "note_for_next": _auto_continuity_note(progress, cal),
        "reflection": reflection,
    }

def _auto_continuity_note(progress: Dict[str, Any], cal: Dict[str, Any]) -> str:
    bits = [
        f"{cal.get('school_year')} {cal.get('semester')}",
        f"T3={progress.get('tram3_trend')}",
        f"điểm_cuối={progress.get('tram3_last_score')}",
        f"T5={progress.get('tram5_trend')}",
        f"ΔWHO5={progress.get('tram5_who5_delta')}",
    ]
    weak = progress.get("weak_topics") or []
    if weak:
        bits.append("yếu:" + ",".join(str(w.get("topic")) for w in weak[:3] if isinstance(w, dict)))
    return " | ".join(str(b) for b in bits if b is not None)


def build_year_continuity_digest(
    vault: Dict[str, Any],
    *,
    user_lookback: str = "",
    user_lesson: str = "",
    user_comment: str = "",
    user_confidence: str = "",
    user_direction: str = "",
) -> Dict[str, Any]:
    """Digest 1 năm: reflection cả năm + hướng đi năm sau; không PII tư vấn thô."""
    cards = list(vault.get("semester_cards") or [])
    if not any(
        c.get("school_year") == (vault.get("calendar") or {}).get("school_year")
        and c.get("semester") == (vault.get("calendar") or {}).get("semester")
        for c in cards
    ):
        cards = cards + [build_semester_card(vault)]
    progress = vault.get("progress") or {}
    identity = vault.get("identity") or {}
    cal = vault.get("calendar") or vn_school_calendar()
    notes = list(vault.get("continuity_notes") or [])
    auto = _auto_continuity_note(progress, cal)
    if auto and auto not in notes:
        notes.append(auto)
    t3_deltas = [c.get("tram3_delta_first_last") for c in cards if c.get("tram3_delta_first_last") is not None]
    who_deltas = [c.get("tram5_who5_delta") for c in cards if c.get("tram5_who5_delta") is not None]
    # Gộp tín hiệu năm từ các thẻ HK
    year_progress = dict(progress)
    if t3_deltas:
        year_progress["tram3_delta_first_last"] = round(sum(t3_deltas), 2)
        year_progress["tram3_trend"] = (
            "progress" if sum(t3_deltas) >= 0.5 else ("regress" if sum(t3_deltas) <= -0.5 else "stable")
        )
    if who_deltas:
        year_progress["tram5_who5_delta"] = round(sum(who_deltas), 2)
        year_progress["tram5_trend"] = (
            "progress" if sum(who_deltas) >= 5 else ("regress" if sum(who_deltas) <= -5 else "stable")
        )
    reflection = build_period_reflection(
        scope="year",
        progress=year_progress,
        cal=cal,
        grade=identity.get("grade"),
        subject=str(identity.get("subject") or ""),
        user_lookback=user_lookback,
        user_lesson=user_lesson,
        user_comment=user_comment,
        user_confidence=user_confidence,
        user_direction=user_direction,
    )
    # Kèm reflection từng HK đã seal
    semester_reflections = [
        c.get("reflection") for c in cards
        if isinstance(c, dict) and isinstance(c.get("reflection"), dict)
    ]
    notes.append(f"YEAR_REFLECT {cal.get('school_year')}: {reflection.get('next_direction')}")
    return {
        "type": "GSAI_YEAR_CONTINUITY_DIGEST_V1",
        "school_year": cal.get("school_year"),
        "sealed_at": now_vn_iso(),
        "research_code": identity.get("research_code"),
        "grade": identity.get("grade"),
        "subject": identity.get("subject"),
        "semester_cards": cards[-MAX_SEMESTER_CARDS:],
        "year_tram3_deltas": t3_deltas,
        "year_who5_deltas": who_deltas,
        "year_tram3_net": round(sum(t3_deltas), 2) if t3_deltas else None,
        "year_who5_net": round(sum(who_deltas), 2) if who_deltas else None,
        "carry_forward_topics": list(progress.get("weak_topics") or [])[:5],
        "continuity_notes": notes[-MAX_CONTINUITY_NOTES:],
        "reflection": reflection,
        "semester_reflections": semester_reflections[-4:],
        "ethics": {
            "raw_events_purged": True,
            "counseling_text_omitted": True,
            "purpose": "year_over_year_learning_continuity",
        },
    }


def compact_vault_end_of_semester(
    vault: Dict[str, Any],
    *,
    user_note: str = "",
    user_lookback: str = "",
    user_lesson: str = "",
    user_comment: str = "",
    user_confidence: str = "",
    user_direction: str = "",
) -> Dict[str, Any]:
    """Cuối HK: nhìn lại / rút KN / nhận xét / tự tin / hướng đi — không xóa sạch."""
    out = dict(vault)
    card = build_semester_card(
        out,
        user_lookback=user_lookback,
        user_lesson=user_lesson,
        user_comment=user_comment,
        user_confidence=user_confidence,
        user_direction=user_direction,
    )
    if user_note.strip():
        card["user_note"] = user_note.strip()[:300]
    cards = list(out.get("semester_cards") or [])
    # replace same year+semester if re-run
    cards = [
        c for c in cards
        if not (c.get("school_year") == card["school_year"] and c.get("semester") == card["semester"])
    ]
    cards.append(card)
    out["semester_cards"] = cards[-MAX_SEMESTER_CARDS:]
    out["latest_reflection"] = card.get("reflection")
    notes = list(out.get("continuity_notes") or [])
    note = card.get("note_for_next") or ""
    refl = card.get("reflection") or {}
    if refl.get("next_direction"):
        note = f"{note} || Hướng đi: {refl['next_direction'][:180]}"
    if user_note.strip():
        note = f"{note} || Ghi chú: {user_note.strip()[:200]}"
    if note and note not in notes:
        notes.append(note)
    out["continuity_notes"] = notes[-MAX_CONTINUITY_NOTES:]
    # Rút gọn thô: chỉ giữ tín hiệu số / chủ đề, bỏ excerpt
    slim_events = []
    for e in out.get("events") or []:
        if not isinstance(e, dict):
            continue
        slim = {
            "event_id": e.get("event_id") or e.get("id"),
            "time": e.get("time") or e.get("submitted_at"),
            "type": e.get("type"),
            "name": e.get("name"),
            "grade": e.get("grade"),
            "subject": e.get("subject"),
            "score": _score_of(e),
            "topic": e.get("topic"),
            "phase": e.get("phase"),
            "theme_key": e.get("theme_key"),
            "station_from": e.get("station_from"),
            "who5": e.get("who5") if isinstance(e.get("who5"), dict) else None,
            "safety": {
                "crisis": bool((e.get("safety") or {}).get("crisis")),
                "violence": bool((e.get("safety") or {}).get("violence")),
            } if isinstance(e.get("safety"), dict) else None,
            "_compacted": True,
        }
        slim_events.append({k: v for k, v in slim.items() if v is not None})
    out["events"] = slim_events[-80:]
    out["retention_state"] = {
        "tier": "warm_semester_compacted",
        "compacted_at": now_vn_iso(),
        "policy": RETENTION_POLICY["id"],
    }
    out["calendar"] = vn_school_calendar()
    out["created_at"] = now_vn_iso()
    out["content_sha256"] = _vault_hash(out)
    return out


def purge_raw_keep_year_continuity(
    vault: Dict[str, Any],
    *,
    user_note: str = "",
) -> Dict[str, Any]:
    """Sau ~1 năm: xóa events thô; giữ digest + xếp vào hành trình 3 năm THPT."""
    out = dict(vault)
    digest = build_year_continuity_digest(out)
    if user_note.strip():
        notes = list(digest.get("continuity_notes") or [])
        notes.append(f"Ghi chú năm: {user_note.strip()[:300]}")
        digest["continuity_notes"] = notes[-MAX_CONTINUITY_NOTES:]
    out["year_continuity_digest"] = digest
    years = list(out.get("thpt_year_digests") or [])
    years = [
        y for y in years
        if not (isinstance(y, dict) and y.get("school_year") == digest.get("school_year"))
    ]
    years.append(digest)
    out["thpt_year_digests"] = years[-MAX_YEAR_DIGESTS:]
    out["semester_cards"] = list(digest.get("semester_cards") or [])
    out["continuity_notes"] = list(digest.get("continuity_notes") or [])
    out["events"] = []  # hard-delete raw on device
    out["progress"] = {
        "tram3_trend": "carried_forward",
        "tram5_trend": "carried_forward",
        "tram3_last_score": (digest.get("semester_cards") or [{}])[-1].get("tram3_last_score"),
        "tram5_who5_delta": digest.get("year_who5_net"),
        "tram3_delta_first_last": digest.get("year_tram3_net"),
        "weak_topics": digest.get("carry_forward_topics") or [],
        "from_year_digest": True,
    }
    out["retention_state"] = {
        "tier": "cold_year_continuity_only",
        "purged_at": now_vn_iso(),
        "policy": RETENTION_POLICY["id"],
        "raw_events_removed": True,
        "thpt_years_kept": len(out["thpt_year_digests"]),
    }
    out["created_at"] = now_vn_iso()
    out["content_sha256"] = _vault_hash(out)
    return out


def _grade_num(value: Any) -> Optional[int]:
    text = str(value or "")
    m = re.search(r"(10|11|12)", text)
    return int(m.group(1)) if m else None


def _moment_title(kind: str) -> str:
    return {
        "first_exam": "Lần chạm Trạm 3 đầu tiên",
        "best_exam": "Đỉnh điểm số trong giai đoạn",
        "exam_progress": "Bứt phá điểm số",
        "exam_regress": "Lần thụt lùi cần đứng dậy",
        "weak_topic": "Chủ đề từng làm khó",
        "diagnostic": "Lần gỡ rối Socratic",
        "who5_lift": "WHO-5 sáng hơn",
        "who5_dip": "WHO-5 cần chăm sóc",
        "counseling_theme": "Chủ đề đồng hành Trạm 5",
        "semester_seal": "Khép học kỳ có ghi chú tiếp nối",
        "year_seal": "Khép năm học — giữ digest",
        "carry_forward": "Hành trang mang sang năm sau",
    }.get(kind, "Khoảnh khắc đáng nhớ")


def extract_important_moments(
    *,
    events: Optional[Sequence[Dict[str, Any]]] = None,
    semester_cards: Optional[Sequence[Dict[str, Any]]] = None,
    year_digest: Optional[Dict[str, Any]] = None,
    limit: int = 8,
) -> List[Dict[str, Any]]:
    """Lật lại khoảnh khắc quan trọng (không lộ excerpt tư vấn thô)."""
    moments: List[Dict[str, Any]] = []
    scores: List[Tuple[Optional[str], float]] = []
    who5s: List[Tuple[Optional[str], float]] = []
    topics: Dict[str, int] = {}
    themes: Dict[str, int] = {}
    first_exam_t = None

    for e in events or []:
        if not isinstance(e, dict):
            continue
        t = e.get("time") or e.get("submitted_at")
        et = str(e.get("type") or "")
        sc = _score_of(e)
        if et == "EXAM_RESULT" and sc is not None:
            scores.append((t, sc))
            if first_exam_t is None:
                first_exam_t = t
                moments.append({
                    "kind": "first_exam",
                    "title": _moment_title("first_exam"),
                    "when": t,
                    "detail": f"Điểm mở đầu: {sc}",
                    "station": 3,
                    "value": sc,
                })
        if et == "SOCRATIC_DIAGNOSTIC":
            topic = str(e.get("topic") or "").strip()
            if topic:
                topics[topic] = topics.get(topic, 0) + 1
                moments.append({
                    "kind": "diagnostic",
                    "title": _moment_title("diagnostic"),
                    "when": t,
                    "detail": f"Gỡ rối chủ đề: {topic}",
                    "station": 2,
                    "topic": topic,
                })
        who = e.get("who5") if isinstance(e.get("who5"), dict) else None
        if who and who.get("percent_0_100") is not None:
            try:
                wp = float(who["percent_0_100"])
            except (TypeError, ValueError):
                wp = None
            if wp is not None:
                who5s.append((t, wp))
        theme = str(e.get("theme_key") or e.get("theme_label") or "").strip()
        if et == "SCHOOL_COUNSELING_SESSION" and theme:
            themes[theme] = themes.get(theme, 0) + 1

    if len(scores) >= 2:
        delta = scores[-1][1] - scores[0][1]
        kind = "exam_progress" if delta >= 0.5 else ("exam_regress" if delta <= -0.5 else None)
        if kind:
            moments.append({
                "kind": kind,
                "title": _moment_title(kind),
                "when": scores[-1][0],
                "detail": f"Từ {scores[0][1]} → {scores[-1][1]} (Δ={delta:+.2f})",
                "station": 3,
                "value": round(delta, 2),
            })
    if scores:
        best_t, best_s = max(scores, key=lambda x: x[1])
        moments.append({
            "kind": "best_exam",
            "title": _moment_title("best_exam"),
            "when": best_t,
            "detail": f"Điểm cao nhất giai đoạn: {best_s}",
            "station": 3,
            "value": best_s,
        })
    if len(who5s) >= 2:
        wdelta = who5s[-1][1] - who5s[0][1]
        wkind = "who5_lift" if wdelta >= 5 else ("who5_dip" if wdelta <= -5 else None)
        if wkind:
            moments.append({
                "kind": wkind,
                "title": _moment_title(wkind),
                "when": who5s[-1][0],
                "detail": f"WHO-5 {who5s[0][1]:.0f} → {who5s[-1][1]:.0f} (Δ={wdelta:+.0f})",
                "station": 5,
                "value": round(wdelta, 1),
            })
    for topic, cnt in sorted(topics.items(), key=lambda kv: (-kv[1], kv[0]))[:3]:
        moments.append({
            "kind": "weak_topic",
            "title": _moment_title("weak_topic"),
            "when": None,
            "detail": f"«{topic}» xuất hiện {cnt} lần trong chẩn đoán",
            "station": 2,
            "topic": topic,
            "value": cnt,
        })
    for theme, cnt in sorted(themes.items(), key=lambda kv: (-kv[1], kv[0]))[:2]:
        moments.append({
            "kind": "counseling_theme",
            "title": _moment_title("counseling_theme"),
            "when": None,
            "detail": f"Chủ đề đồng hành: {theme} ({cnt} phiên) — không lưu nội dung thô",
            "station": 5,
            "theme_key": theme,
            "value": cnt,
        })

    for card in semester_cards or []:
        if not isinstance(card, dict):
            continue
        moments.append({
            "kind": "semester_seal",
            "title": _moment_title("semester_seal"),
            "when": card.get("sealed_at"),
            "detail": card.get("note_for_next") or f"{card.get('school_year')} {card.get('semester')}",
            "station": 0,
            "school_year": card.get("school_year"),
            "semester": card.get("semester"),
        })

    if isinstance(year_digest, dict) and year_digest:
        moments.append({
            "kind": "year_seal",
            "title": _moment_title("year_seal"),
            "when": year_digest.get("sealed_at"),
            "detail": (
                f"Năm {year_digest.get('school_year')}: "
                f"ΔT3={year_digest.get('year_tram3_net')}, ΔWHO5={year_digest.get('year_who5_net')}"
            ),
            "station": 0,
            "school_year": year_digest.get("school_year"),
        })
        for w in (year_digest.get("carry_forward_topics") or [])[:3]:
            if isinstance(w, dict) and w.get("topic"):
                moments.append({
                    "kind": "carry_forward",
                    "title": _moment_title("carry_forward"),
                    "when": year_digest.get("sealed_at"),
                    "detail": f"Mang sang năm sau: {w.get('topic')}",
                    "station": 2,
                    "topic": w.get("topic"),
                })

    # Prefer diversity of kinds, then recency
    seen_kinds = set()
    ranked: List[Dict[str, Any]] = []
    for m in sorted(moments, key=lambda x: (x.get("when") or ""), reverse=True):
        k = m.get("kind")
        # allow up to 2 of same kind
        count_k = sum(1 for r in ranked if r.get("kind") == k)
        if count_k >= 2 and k in seen_kinds:
            continue
        seen_kinds.add(k)
        ranked.append(m)
        if len(ranked) >= limit:
            break
    return ranked


def build_year_experience_journey(
    *,
    school_year: str = "",
    grade: Any = "",
    events: Optional[Sequence[Dict[str, Any]]] = None,
    semester_cards: Optional[Sequence[Dict[str, Any]]] = None,
    year_digest: Optional[Dict[str, Any]] = None,
    continuity_notes: Optional[Sequence[str]] = None,
) -> Dict[str, Any]:
    """Hành trình trải nghiệm một năm học — để lật lại từng năm."""
    cards = [
        c for c in (semester_cards or [])
        if isinstance(c, dict) and (not school_year or c.get("school_year") == school_year)
    ]
    moments = extract_important_moments(
        events=events, semester_cards=cards, year_digest=year_digest, limit=8,
    )
    g = _grade_num(grade) or _grade_num((year_digest or {}).get("grade") if year_digest else "")
    chapter = {
        10: "Năm mở đầu — làm quen nhịp tự học & bản lĩnh đứng dậy",
        11: "Năm bứt phá — sâu kiến thức, giữ nhịp và sức khỏe tinh thần",
        12: "Năm chín chắn — chốt hành trang trước khi rời cổng trường",
    }.get(g or 0, "Một năm đồng hành cùng Gia Sư AI")
    story_lines = [f"**{school_year or 'Năm học'}** · Lớp {grade or (year_digest or {}).get('grade') or '?'} — {chapter}"]
    for m in moments[:6]:
        when = f" ({m['when']})" if m.get("when") else ""
        story_lines.append(f"- {m.get('title')}{when}: {m.get('detail')}")
    notes = [n for n in (continuity_notes or []) if n]
    if notes:
        story_lines.append("- Ghi chú tiếp nối: " + " · ".join(str(n) for n in notes[-2:]))
    return {
        "type": "GSAI_YEAR_EXPERIENCE_JOURNEY_V1",
        "school_year": school_year or (year_digest or {}).get("school_year"),
        "grade": str(grade or (year_digest or {}).get("grade") or ""),
        "chapter": chapter,
        "moments": moments,
        "story_md": "\n".join(story_lines),
        "tram3_net": (year_digest or {}).get("year_tram3_net"),
        "who5_net": (year_digest or {}).get("year_who5_net"),
    }


def build_three_year_experience_recap(vault: Dict[str, Any]) -> Dict[str, Any]:
    """Nhắc lại hành trình trải nghiệm theo từng năm và cả 3 năm THPT."""
    years = list(vault.get("thpt_year_digests") or [])
    current = vault.get("year_continuity_digest")
    if isinstance(current, dict) and current.get("school_year"):
        if not any(y.get("school_year") == current.get("school_year") for y in years if isinstance(y, dict)):
            years = years + [current]
    # Nếu chưa có digest năm: dựng journey từ events hiện tại
    year_journeys: List[Dict[str, Any]] = []
    for y in [x for x in years if isinstance(x, dict)][-MAX_YEAR_DIGESTS:]:
        year_journeys.append(build_year_experience_journey(
            school_year=str(y.get("school_year") or ""),
            grade=y.get("grade"),
            events=[],  # đã purge thô — dùng card/digest
            semester_cards=y.get("semester_cards") or vault.get("semester_cards") or [],
            year_digest=y,
            continuity_notes=y.get("continuity_notes") or vault.get("continuity_notes") or [],
        ))
    if not year_journeys and (vault.get("events") or vault.get("semester_cards")):
        cal = vault.get("calendar") or vn_school_calendar()
        year_journeys.append(build_year_experience_journey(
            school_year=str(cal.get("school_year") or ""),
            grade=(vault.get("identity") or {}).get("grade"),
            events=vault.get("events") or [],
            semester_cards=vault.get("semester_cards") or [],
            year_digest=vault.get("year_continuity_digest"),
            continuity_notes=vault.get("continuity_notes") or [],
        ))

    # Khoảnh khắc nổi bật cả 3 năm
    arc_moments: List[Dict[str, Any]] = []
    for j in year_journeys:
        for m in j.get("moments") or []:
            mm = dict(m)
            mm["school_year"] = j.get("school_year")
            mm["grade"] = j.get("grade")
            arc_moments.append(mm)
    # Ưu tiên progress / best / who5_lift / year_seal
    priority = {
        "exam_progress": 0, "best_exam": 1, "who5_lift": 2, "year_seal": 3,
        "semester_seal": 4, "diagnostic": 5, "weak_topic": 6, "exam_regress": 7,
        "who5_dip": 8, "counseling_theme": 9, "carry_forward": 10, "first_exam": 11,
    }
    arc_moments = sorted(
        arc_moments,
        key=lambda m: (priority.get(str(m.get("kind")), 99), m.get("when") or ""),
    )[:12]

    chapters_md = []
    for j in year_journeys:
        chapters_md.append(j.get("story_md") or "")
    t3_nets = [j.get("tram3_net") for j in year_journeys if j.get("tram3_net") is not None]
    who_nets = [j.get("who5_net") for j in year_journeys if j.get("who5_net") is not None]
    arc_story = [
        f"# Hành trình 3 năm thanh xuân tại {SCHOOL_NAME}",
        f"*{SCHOOL_MOTTO}*",
        "",
        f"Đã ghi lại **{len(year_journeys)}** năm trải nghiệm trên thiết bị của em.",
    ]
    if t3_nets:
        arc_story.append(f"- Tổng Δ học lực (Trạm 3): **{sum(t3_nets):+.2f}**")
    if who_nets:
        arc_story.append(f"- Tổng Δ WHO-5: **{sum(who_nets):+.0f}**")
    arc_story.append("")
    arc_story.append("## Lật lại từng năm")
    for block in chapters_md:
        arc_story.append(block)
        arc_story.append("")
    if arc_moments:
        arc_story.append("## Khoảnh khắc quan trọng xuyên suốt 3 năm")
        for m in arc_moments[:10]:
            label = f"{m.get('school_year') or ''} L{m.get('grade') or ''}".strip()
            arc_story.append(f"- [{label}] **{m.get('title')}**: {m.get('detail')}")

    return {
        "type": "GSAI_THPT_3Y_EXPERIENCE_RECAP_V1",
        "school": SCHOOL_NAME,
        "motto": SCHOOL_MOTTO,
        "built_at": now_vn_iso(),
        "years_n": len(year_journeys),
        "year_journeys": year_journeys,
        "arc_moments": arc_moments,
        "story_md": "\n".join(arc_story).strip(),
        "arc_tram3_net": round(sum(t3_nets), 2) if t3_nets else None,
        "arc_who5_net": round(sum(who_nets), 2) if who_nets else None,
    }


def build_thpt_youth_arc(vault: Dict[str, Any]) -> Dict[str, Any]:
    """Tổng hợp tối đa 3 năm THPT để đánh giá trọn thanh xuân cấp 3."""
    years = list(vault.get("thpt_year_digests") or [])
    current = vault.get("year_continuity_digest")
    if isinstance(current, dict) and current.get("school_year"):
        if not any(y.get("school_year") == current.get("school_year") for y in years if isinstance(y, dict)):
            years = years + [current]
    years = [y for y in years if isinstance(y, dict)][-MAX_YEAR_DIGESTS:]
    identity = vault.get("identity") or {}
    t3_nets = [y.get("year_tram3_net") for y in years if y.get("year_tram3_net") is not None]
    who_nets = [y.get("year_who5_net") for y in years if y.get("year_who5_net") is not None]
    grades = sorted({g for g in (_grade_num(y.get("grade")) for y in years) if g})
    recap = build_three_year_experience_recap({**vault, "thpt_year_digests": years})
    return {
        "type": "GSAI_THPT_YOUTH_ARC_V1",
        "school": SCHOOL_NAME,
        "province": SCHOOL_PROVINCE,
        "motto": SCHOOL_MOTTO,
        "sealed_at": now_vn_iso(),
        "research_code": identity.get("research_code"),
        "display_name": identity.get("display_name"),
        "years_n": len(years) or recap.get("years_n") or 0,
        "grades_covered": grades,
        "year_digests": years,
        "arc_tram3_net": round(sum(t3_nets), 2) if t3_nets else recap.get("arc_tram3_net"),
        "arc_who5_net": round(sum(who_nets), 2) if who_nets else recap.get("arc_who5_net"),
        "continuity_notes": list(vault.get("continuity_notes") or [])[-MAX_CONTINUITY_NOTES:],
        "experience_recap": recap,
        "complete_3y": len(years) >= 3 or grades == [10, 11, 12],
    }


def build_farewell_letter(
    vault: Dict[str, Any],
    *,
    student_name: str = "",
    user_wish: str = "",
) -> Dict[str, Any]:
    """Lời chào tạm biệt + dặn dò + triết lý + lật lại hành trình 3 năm."""
    identity = vault.get("identity") or {}
    name = (student_name or identity.get("display_name") or "em").strip() or "em"
    arc = build_thpt_youth_arc(vault)
    recap = arc.get("experience_recap") or build_three_year_experience_recap(vault)
    years_n = int(arc.get("years_n") or 0)
    t3 = arc.get("arc_tram3_net")
    who = arc.get("arc_who5_net")
    growth_bits = []
    if t3 is not None:
        growth_bits.append(f"học lực (Δ điểm tích lũy ~ {t3:+.2f})")
    if who is not None:
        growth_bits.append(f"sức khỏe tinh thần học đường (Δ WHO-5 ~ {who:+.0f})")
    growth = ", ".join(growth_bits) if growth_bits else "những bước tiến nhỏ mỗi ngày trên hành trình tự học"

    year_blocks = []
    for j in recap.get("year_journeys") or []:
        year_blocks.append(j.get("story_md") or "")
    years_section = "\n\n".join(year_blocks) if year_blocks else "_Chưa đủ dữ liệu từng năm — hãy nén cuối HK / khép năm để lưu khoảnh khắc._"

    arc_moments_lines = []
    for m in (recap.get("arc_moments") or [])[:8]:
        label = f"{m.get('school_year') or ''} L{m.get('grade') or ''}".strip()
        arc_moments_lines.append(f"- [{label}] **{m.get('title')}**: {m.get('detail')}")
    moments_section = "\n".join(arc_moments_lines) if arc_moments_lines else "- Hãy giữ lại những lần đứng dậy sau sai lầm — đó chính là khoảnh khắc vàng."

    wish_block = f"\n## Lời nhắn của chính em\n{user_wish.strip()[:400]}\n" if user_wish.strip() else ""

    farewell_md = f"""# Lời chào tạm biệt từ {SCHOOL_NAME}

Kính gửi **{name}**,

Ba năm thanh xuân dưới mái trường **{SCHOOL_NAME} ({SCHOOL_PROVINCE})** — khoảng **{years_n or '…'}** năm đồng hành cùng Gia Sư AI — rồi cũng đến ngày em bước ra thế giới rộng lớn hơn.

Thầy không giữ em lại bằng điểm số. Thầy gửi em **hành trang**: biết tự hỏi, biết sửa lỗi, biết đứng dậy sau lần thụt lùi, và biết giữ **thiện tâm** khi cạnh tranh ngoài đời trở nên gắt hơn.

**Triết lý chân trang của nhà trường:** *{SCHOOL_MOTTO}*

## Lật lại hành trình theo từng năm
{years_section}

## Khoảnh khắc quan trọng xuyên suốt 3 năm
{moments_section}

## Dặn dò khi rời cổng trường
1. **Học là cách yêu thương bản thân có phương pháp** — không học để hơn người, học để mình vững hơn hôm qua.
2. **Sai là dữ liệu, không phải bản án** — mỗi lần vấp ở Trạm 2–3 là một tấm bản đồ để đi tiếp.
3. **Giữ sức khỏe tinh thần** như giữ sức khỏe thể chất — biết nghỉ, biết nhờ người lớn tin cậy, biết nói “em cần giúp”.
4. **Đi xa vẫn nhớ gốc** — gốc là kỷ luật, lòng biết ơn, và tình bạn đã cùng em đi qua lớp 10–11–12.
5. **Ra đời hãy là người tử tế có năng lực** — tử tế không yếu; năng lực không lạnh.

## Nhìn lại tín hiệu tăng trưởng
- {growth}.
- Đây không phải hồ sơ bệnh án, cũng không phải bản án nhân cách — chỉ là **gương soi tiến bộ** em tự giữ trên thiết bị.
{wish_block}
Chúc em **bình an – bản lĩnh – nhân ái**.  
Cổng trường có thể khép lại phía sau, nhưng **thiện tâm và chí học** thì đi cùng em mãi.

Trân trọng,  
**{SCHOOL_AUTHOR}**  
*{SCHOOL_NAME} • {SCHOOL_MOTTO}*
""".strip()

    return {
        "type": "GSAI_THPT_FAREWELL_V1",
        "school": SCHOOL_NAME,
        "motto": SCHOOL_MOTTO,
        "author": SCHOOL_AUTHOR,
        "sealed_at": now_vn_iso(),
        "student_display_name": name,
        "research_code": identity.get("research_code"),
        "years_n": years_n,
        "arc_summary": {
            "grades_covered": arc.get("grades_covered"),
            "arc_tram3_net": arc.get("arc_tram3_net"),
            "arc_who5_net": arc.get("arc_who5_net"),
            "complete_3y": arc.get("complete_3y"),
        },
        "experience_recap": recap,
        "farewell_md": farewell_md,
        "parting_advice": [
            "Học để vững hơn hôm qua, không để hơn người.",
            "Sai là dữ liệu — đứng dậy là bản lĩnh.",
            "Giữ sức khỏe tinh thần như giữ sức khỏe thể chất.",
            "Đi xa nhớ gốc: kỷ luật, biết ơn, tình bạn.",
            "Ra đời: tử tế có năng lực.",
        ],
        "philosophy": SCHOOL_MOTTO,
        "ethics": {
            "on_device_keepsake": True,
            "not_clinical_record": True,
            "counseling_text_omitted": True,
        },
    }


def seal_thpt_graduation_farewell(
    vault: Dict[str, Any],
    *,
    student_name: str = "",
    user_wish: str = "",
) -> Dict[str, Any]:
    """Cuối cấp THPT: seal hành trình 3 năm + lời chào tạm biệt; xóa thô nếu còn."""
    out = dict(vault)
    # Bảo đảm năm hiện tại đã vào digest nếu còn events
    if out.get("events"):
        out = purge_raw_keep_year_continuity(out, user_note="seal_graduation")
    arc = build_thpt_youth_arc(out)
    farewell = build_farewell_letter(out, student_name=student_name, user_wish=user_wish)
    out["thpt_youth_arc"] = arc
    out["farewell"] = farewell
    out["events"] = []
    notes = list(out.get("continuity_notes") or [])
    seal_note = (
        f"FAREWELL {SCHOOL_NAME} @ {farewell.get('sealed_at')} | "
        f"years={arc.get('years_n')} | motto={SCHOOL_MOTTO}"
    )
    if seal_note not in notes:
        notes.append(seal_note)
    if user_wish.strip():
        notes.append(f"Ước nguyện tốt nghiệp: {user_wish.strip()[:200]}")
    out["continuity_notes"] = notes[-MAX_CONTINUITY_NOTES:]
    out["retention_state"] = {
        "tier": "sealed_thpt_farewell",
        "sealed_at": now_vn_iso(),
        "policy": RETENTION_POLICY["id"],
        "raw_events_removed": True,
        "keepsake": "farewell+philosophy+3y_arc",
    }
    out["created_at"] = now_vn_iso()
    out["content_sha256"] = _vault_hash(out)
    return out


def vault_age_days(vault: Dict[str, Any]) -> Optional[int]:
    times = []
    created = _parse_vn_dt(vault.get("created_at"))
    if created:
        times.append(created)
    for e in vault.get("events") or []:
        if isinstance(e, dict):
            dt = _parse_vn_dt(e.get("time") or e.get("submitted_at") or e.get("created_at"))
            if dt:
                times.append(dt)
    digest = vault.get("year_continuity_digest") or {}
    sealed = _parse_vn_dt(digest.get("sealed_at"))
    if sealed:
        times.append(sealed)
    if not times:
        return None
    oldest = min(times)
    return max(0, (datetime.now(VN_TZ) - oldest).days)


def retention_status(vault: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Trạng thái retention để UI/gợi ý hành động."""
    cal = vn_school_calendar()
    if not vault:
        return {
            "tier": "empty",
            "calendar": cal,
            "recommend": "keep_hot",
            "message_vi": (
                f"Năm học {cal['school_year']} · {cal['semester']}: "
                "đang ở chế độ đủ dữ liệu. Cuối HK chỉ nén + ghi chú — không xóa sạch."
            ),
            "policy": RETENTION_POLICY,
        }
    state = vault.get("retention_state") or {}
    tier = state.get("tier") or "hot"
    age = vault_age_days(vault)
    cards = vault.get("semester_cards") or []
    notes = vault.get("continuity_notes") or []
    recommend = "keep_hot"
    message = (
        f"Năm học {cal['school_year']} · {cal['semester']} · tier={tier}. "
        "Cuối HK: nén giữ ghi chú tiếp nối; sau 1 năm: xóa thô, giữ digest."
    )
    if age is not None and age >= YEAR_RETENTION_DAYS and tier != "cold_year_continuity_only":
        recommend = "purge_year_keep_continuity"
        message = (
            f"Hồ sơ đã ~{age} ngày (≥{YEAR_RETENTION_DAYS}). "
            "Nên xóa sự kiện thô và giữ year_continuity_digest để năm sau tiếp nối."
        )
    elif tier == "hot" and any(
        c.get("school_year") == cal["school_year"] and c.get("semester") != cal["semester"]
        for c in cards
    ):
        recommend = "compact_semester"
        message = (
            f"Phát hiện thẻ học kỳ khác trong {cal['school_year']}. "
            f"Nên nén HK hiện tại + ghi chú tiếp nối (không xóa sạch)."
        )
    elif tier == "cold_year_continuity_only":
        recommend = "continue_from_digest"
        message = "Đang dùng digest năm trước — dữ liệu thô đã xóa; ghi chú tiếp nối vẫn còn (tối đa 3 năm THPT)."
    years_n = len(vault.get("thpt_year_digests") or [])
    gnum = _grade_num((vault.get("identity") or {}).get("grade"))
    if tier == "sealed_thpt_farewell" or vault.get("farewell"):
        recommend = "farewell_keepsake"
        message = (
            f"Đã seal hành trình THPT tại {SCHOOL_NAME}: lời chào tạm biệt & triết lý "
            f"«{SCHOOL_MOTTO}» giữ trên thiết bị làm hành trang."
        )
    elif gnum == 12 and (years_n >= 2 or age is not None and age >= YEAR_RETENTION_DAYS):
        recommend = "seal_graduation_farewell"
        message = (
            "Lớp 12 / cuối cuối cấp: có thể **seal 3 năm thanh xuân** + lời chào tạm biệt, "
            f"dặn dò và triết lý hành trang khi rời {SCHOOL_NAME}."
        )
    return {
        "tier": tier,
        "age_days": age,
        "calendar": cal,
        "semester_cards_n": len(cards),
        "continuity_notes_n": len(notes),
        "has_year_digest": bool(vault.get("year_continuity_digest")),
        "thpt_years_n": years_n,
        "has_farewell": bool(vault.get("farewell")),
        "recommend": recommend,
        "message_vi": message,
        "policy": RETENTION_POLICY,
    }


def compress_vault(snapshot: Dict[str, Any]) -> bytes:
    raw = json.dumps(snapshot, ensure_ascii=False, separators=(",", ":"), default=str).encode("utf-8")
    blob = lzma.compress(raw, preset=6)
    if len(blob) > MAX_VAULT_BYTES:
        raise ValueError("vault_too_large")
    return blob


def decompress_vault(blob: bytes) -> Dict[str, Any]:
    if not blob:
        raise ValueError("vault_empty")
    if len(blob) > MAX_VAULT_BYTES * 2:
        raise ValueError("vault_too_large")
    # accept raw lzma or base64-wrapped
    data = blob
    try:
        raw = lzma.decompress(data)
    except Exception:
        try:
            data = base64.b64decode(blob, validate=False)
            raw = lzma.decompress(data)
        except Exception as exc:
            raise ValueError("vault_decompress_failed") from exc
    obj = json.loads(raw.decode("utf-8"))
    if not isinstance(obj, dict) or obj.get("type") != VAULT_TYPE:
        raise ValueError("vault_type_invalid")
    return obj


def vault_to_base64(snapshot: Dict[str, Any]) -> str:
    return base64.b64encode(compress_vault(snapshot)).decode("ascii")


def vault_from_base64(text: str) -> Dict[str, Any]:
    return decompress_vault(base64.b64decode(str(text or "").strip(), validate=False))


def research_safe_events(
    logs: Iterable[Dict[str, Any]],
    *,
    salt: str = "gsai-edu-2026",
) -> List[Dict[str, Any]]:
    """Bản minh bạch nghiên cứu: ẩn danh, bỏ PII/nội dung tư vấn thô/secrets."""
    out = []
    for event in logs or []:
        if not isinstance(event, dict):
            continue
        name = str(event.get("name") or event.get("student_name") or "").strip()
        grade = event.get("grade") or event.get("grade_level")
        code = event.get("student_id") or research_code(name, grade, salt=salt)
        safe = {
            "event_id": event.get("event_id") or event.get("id"),
            "time": event.get("time") or event.get("submitted_at") or event.get("created_at"),
            "type": event.get("type"),
            "research_code": code if str(code).startswith("HS-") else research_code(str(code), grade, salt=salt),
            "grade": str(grade) if grade is not None else "",
            "subject": event.get("subject"),
            "phase": event.get("phase"),
            "score": _score_of(event),
            "topic": event.get("topic"),
            "error_type": event.get("error_type"),
            "theme_key": event.get("theme_key"),
            "station_from": event.get("station_from"),
            "safety_crisis": bool((event.get("safety") or {}).get("crisis")) if isinstance(event.get("safety"), dict) else None,
            "safety_violence": bool((event.get("safety") or {}).get("violence")) if isinstance(event.get("safety"), dict) else None,
            "who5_percent": (event.get("who5") or {}).get("percent_0_100") if isinstance(event.get("who5"), dict) else None,
            "school_wellbeing_0_10": (event.get("school_checkin") or {}).get("wellbeing_index_0_10")
            if isinstance(event.get("school_checkin"), dict) else None,
            "weekly_goal_progress": (event.get("weekly_goal") or {}).get("progress_0_10")
            if isinstance(event.get("weekly_goal"), dict) else None,
            "pii_redacted": True,
            "counseling_text_omitted": event.get("type") in {
                "SCHOOL_COUNSELING_SESSION", "COUNSELING_OUTCOME_CHECKIN"
            },
        }
        # Never copy sensitive keys
        out.append(safe)
    return out


def research_safe_csv_rows(logs: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return research_safe_events(logs)


def ethics_banner_md() -> str:
    return (
        "**Minh bạch & bảo mật:** hồ sơ đầy đủ chỉ lưu trên **thiết bị cá nhân** (nén `.gsai.xz`), "
        "người dùng được **tải / khôi phục / xóa**. "
        "**Không xóa sạch mỗi học kỳ** — cuối HK **nén + ghi chú tiếp nối**; "
        "**sau mỗi năm** xóa thô, **giữ digest** (tối đa **3 năm THPT**) để đánh giá trọn thanh xuân. "
        f"**Cuối cấp:** seal lời chào tạm biệt & triết lý «{SCHOOL_MOTTO}» từ {SCHOOL_NAME}. "
        "Bản GV–nghiên cứu: mã HS-…, ẩn danh, không excerpt tư vấn / secrets. Không phải hồ sơ bệnh án."
    )


def apply_vault_to_session_payload(vault: Dict[str, Any]) -> Dict[str, Any]:
    """Chuẩn bị dict để ghi lại session_state (caller gán)."""
    events = [e for e in (vault.get("events") or []) if isinstance(e, dict)]
    analytics = [e for e in events if e.get("type") != "USER_FEEDBACK"]
    counseling = [
        e for e in events
        if e.get("type") in {"SCHOOL_COUNSELING_SESSION", "COUNSELING_OUTCOME_CHECKIN"}
    ]
    identity = vault.get("identity") or {}
    counts = vault.get("tram_counts") or {}
    return {
        "analytics_logs": analytics,
        "counseling_logs": counseling,
        "tram1_count": int(counts.get("tram1") or counts.get("tram1_count") or 0),
        "tram2_count": int(counts.get("tram2") or counts.get("tram2_count") or 0),
        "tram3_count": int(counts.get("tram3") or counts.get("tram3_count") or 0),
        "tram5_count": int(counts.get("tram5") or counts.get("tram5_count") or 0),
        "current_topic": vault.get("current_topic") or "",
        "personal_vault_last": vault,
        "personal_continuity_notes": list(vault.get("continuity_notes") or []),
        "personal_year_digest": vault.get("year_continuity_digest"),
        "personal_thpt_arc": vault.get("thpt_youth_arc"),
        "personal_farewell": vault.get("farewell"),
        "restored_display_name": identity.get("display_name") or "",
        "restored_grade": identity.get("grade") or "",
        "restored_subject": identity.get("subject") or "",
    }
