# -*- coding: utf-8 -*-
"""Trạm 4 — hồ sơ người học & đối chiếu trước/sau từ nhật ký quan sát.

Không chứng nhận nhân quả; chỉ tổng hợp dữ liệu EXAM_RESULT / SOCRATIC_DIAGNOSTIC
đã ghi để giáo viên cá nhân hóa và đối chiếu Pre–Post. Không đọc khóa/bí mật.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any, Dict, Iterable, List, Optional


def _norm(text: Any) -> str:
    return str(text or "").strip()


def student_key(event: Dict[str, Any]) -> str:
    sid = _norm(event.get("student_id"))
    if sid:
        return sid
    name = _norm(event.get("name") or event.get("student_name"))
    grade = _norm(event.get("grade") or event.get("grade_level"))
    subject = _norm(event.get("subject"))
    if name:
        return f"{name}|{grade}|{subject}"
    return ""


def _score(event: Dict[str, Any]) -> Optional[float]:
    try:
        value = float(event.get("score"))
    except (TypeError, ValueError):
        return None
    if value < 0 or value > 10:
        return None
    return value


def _phase(event: Dict[str, Any]) -> str:
    raw = _norm(event.get("phase")).casefold()
    if raw in {"pre", "pre_test", "trước", "truoc"}:
        return "pre"
    if raw in {"post", "post_test", "sau"}:
        return "post"
    return ""


def exam_events(logs: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out = []
    for event in logs or []:
        if not isinstance(event, dict):
            continue
        etype = event.get("type")
        looks_exam = etype == "EXAM_RESULT" or (
            etype is None
            and event.get("score") is not None
            and (event.get("exam_code") is not None or event.get("code") is not None or event.get("phase") is not None)
        )
        if not looks_exam:
            continue
        if event.get("grading_status") == "ai_reference":
            continue
        out.append(event)
    return out


def diagnostic_events(logs: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [
        e for e in (logs or [])
        if isinstance(e, dict) and e.get("type") == "SOCRATIC_DIAGNOSTIC"
    ]


def collect_pre_post_pairs(logs: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Ghép Pre/Post theo student_id (+ môn + lớp). Một cặp / khóa; bỏ trùng phase."""
    buckets: Dict[tuple, Dict[str, Any]] = {}
    for event in exam_events(logs):
        phase = _phase(event)
        if phase not in {"pre", "post"}:
            continue
        score = _score(event)
        if score is None:
            continue
        key = (
            student_key(event),
            _norm(event.get("subject")),
            _norm(event.get("grade") or event.get("grade_level")),
        )
        if not key[0]:
            continue
        slot = buckets.setdefault(key, {"pre": None, "post": None, "meta": event})
        # Giữ lần ghi gần nhất theo time nếu có nhiều; ưu tiên bản sau cùng trong list.
        slot[phase] = {
            "score": score,
            "minutes": _minutes(event),
            "name": _norm(event.get("name") or event.get("student_name")),
            "code": _norm(event.get("code") or event.get("exam_code")),
            "time": _norm(event.get("time") or event.get("submitted_at")),
        }
        slot["meta"] = event

    pairs = []
    for (sid, subject, grade), slot in buckets.items():
        if not slot.get("pre") or not slot.get("post"):
            continue
        pre, post = slot["pre"], slot["post"]
        pairs.append({
            "student_id": sid,
            "name": post.get("name") or pre.get("name") or sid,
            "subject": subject,
            "grade": grade,
            "pre": pre["score"],
            "post": post["score"],
            "delta": round(post["score"] - pre["score"], 3),
            "minutes": post.get("minutes") if post.get("minutes") is not None else pre.get("minutes"),
            "pre_code": pre.get("code"),
            "post_code": post.get("code"),
        })
    pairs.sort(key=lambda row: (row["subject"], row["grade"], row["name"]))
    return pairs


def _minutes(event: Dict[str, Any]) -> Optional[float]:
    for key in ("minutes", "duration_minutes"):
        if event.get(key) is not None:
            try:
                return float(event.get(key))
            except (TypeError, ValueError):
                pass
    if event.get("duration_seconds") is not None:
        try:
            return round(float(event["duration_seconds"]) / 60.0, 1)
        except (TypeError, ValueError):
            return None
    return None


def weak_topics(logs: Iterable[Dict[str, Any]], student_id: str = "", limit: int = 8) -> List[Dict[str, Any]]:
    counts: Counter = Counter()
    errors: Counter = Counter()
    for event in diagnostic_events(logs):
        if student_id and student_key(event) != student_id and _norm(event.get("student_id")) != student_id:
            name = _norm(event.get("name") or event.get("student_name"))
            if student_id and name and student_id not in (name, student_key(event)):
                # allow match by bare name when profile key is name|grade|subject
                if not student_id.startswith(name):
                    continue
        topic = _norm(event.get("topic")) or "(chưa gắn chủ đề)"
        counts[topic] += 1
        et = _norm(event.get("error_type"))
        if et:
            errors[et] += 1
    rows = [{"topic": t, "count": c} for t, c in counts.most_common(limit)]
    return rows


def item_correctness_sequence(event: Dict[str, Any]) -> List[bool]:
    answers = event.get("answers") or {}
    if not isinstance(answers, dict):
        return []
    results = answers.get("_item_results")
    if isinstance(results, dict) and results:
        seq = []
        for key in sorted(results.keys()):
            val = results[key]
            if isinstance(val, bool):
                seq.append(val)
            elif isinstance(val, dict) and "correct" in val:
                seq.append(bool(val["correct"]))
        return seq
    return []


def build_learner_profiles(logs: Iterable[Dict[str, Any]], limit: int = 40) -> List[Dict[str, Any]]:
    """Hồ sơ cá nhân hóa từ dữ liệu quan sát: Pre/Post, chủ đề yếu, BKT nếu có chuỗi đúng/sai."""
    pairs = collect_pre_post_pairs(logs)
    by_student: Dict[str, Dict[str, Any]] = {}

    for pair in pairs:
        sid = pair["student_id"]
        profile = by_student.setdefault(sid, {
            "student_id": sid,
            "name": pair["name"],
            "subjects": [],
            "pair_count": 0,
            "mean_delta": 0.0,
            "weak_topics": [],
            "bkt_mastery": None,
            "recommendation": "",
        })
        profile["subjects"].append({
            "subject": pair["subject"],
            "grade": pair["grade"],
            "pre": pair["pre"],
            "post": pair["post"],
            "delta": pair["delta"],
            "minutes": pair["minutes"],
        })
        profile["pair_count"] += 1
        profile["name"] = pair["name"] or profile["name"]

    # Diagnostics / BKT from latest exam with item results
    exam_by_student: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for event in exam_events(logs):
        key = student_key(event)
        if key:
            exam_by_student[key].append(event)

    for sid, profile in by_student.items():
        deltas = [s["delta"] for s in profile["subjects"]]
        profile["mean_delta"] = round(sum(deltas) / len(deltas), 3) if deltas else 0.0
        profile["weak_topics"] = weak_topics(logs, student_id=sid)
        seq: List[bool] = []
        for event in exam_by_student.get(sid, []):
            seq.extend(item_correctness_sequence(event))
        if len(seq) >= 3:
            try:
                from services.bkt_service import compute_bkt_trajectory
                traj = compute_bkt_trajectory(seq[-20:], is_socratic=False, is_mcq=True)
                if traj:
                    profile["bkt_mastery"] = traj[-1]["p_posterior"]
            except Exception:
                profile["bkt_mastery"] = None
        profile["recommendation"] = _recommend(profile)

    # Students with diagnostics but no pre/post yet
    for event in diagnostic_events(logs):
        sid = student_key(event) or _norm(event.get("name") or event.get("student_name"))
        if not sid or sid in by_student:
            continue
        by_student[sid] = {
            "student_id": sid,
            "name": _norm(event.get("name") or event.get("student_name")) or sid,
            "subjects": [],
            "pair_count": 0,
            "mean_delta": 0.0,
            "weak_topics": weak_topics(logs, student_id=sid),
            "bkt_mastery": None,
            "recommendation": "Chưa có cặp Pre/Post — nên gắn phase=pre/post khi làm đề Trạm 3 để đối chiếu trước–sau.",
        }

    profiles = list(by_student.values())
    profiles.sort(key=lambda p: (p["pair_count"] == 0, -abs(p["mean_delta"]), p["name"]))
    return profiles[:limit]


def _recommend(profile: Dict[str, Any]) -> str:
    topics = [t["topic"] for t in profile.get("weak_topics") or []]
    mean_delta = profile.get("mean_delta") or 0.0
    if mean_delta >= 1.5:
        pace = "Tiến bộ rõ trên bài đối chiếu Pre–Post."
    elif mean_delta > 0:
        pace = "Có tiến bộ nhẹ; cần củng cố chủ đề còn lệch."
    elif mean_delta == 0 and profile.get("pair_count"):
        pace = "Điểm Pre–Post chưa đổi; nên ôn mục yếu rồi làm lại Post."
    else:
        pace = "Điểm sau thấp hơn trước trên bài đối chiếu — ưu tiên ôn lại lỗ hổng."
    if topics:
        return f"{pace} Ưu tiên: {', '.join(topics[:3])}."
    return pace + " Chưa có chẩn đoán Trạm 2 gắn chủ đề."


def parent_report_defaults(
    logs: Iterable[Dict[str, Any]],
    preferred_name: str = "",
    preferred_subject: str = "",
    preferred_grade: str = "",
) -> Dict[str, Any]:
    """Điền phiếu phụ huynh từ cặp Pre/Post quan sát — không dùng điểm mẫu cứng."""
    pairs = collect_pre_post_pairs(logs)
    preferred_name = _norm(preferred_name)
    preferred_subject = _norm(preferred_subject)
    preferred_grade = _norm(preferred_grade)

    def _match(pair: Dict[str, Any]) -> int:
        score = 0
        if preferred_name and preferred_name.casefold() in str(pair.get("name", "")).casefold():
            score += 4
        if preferred_name and preferred_name == pair.get("student_id"):
            score += 5
        if preferred_subject and preferred_subject == pair.get("subject"):
            score += 2
        if preferred_grade and preferred_grade in str(pair.get("grade", "")):
            score += 1
        return score

    chosen = None
    if pairs:
        ranked = sorted(pairs, key=_match, reverse=True)
        if preferred_name or preferred_subject:
            chosen = ranked[0] if _match(ranked[0]) > 0 else ranked[0]
        else:
            chosen = ranked[0]

    if not chosen:
        return {
            "source": "empty",
            "name": preferred_name or "",
            "subject": preferred_subject or "Toán học",
            "grade": preferred_grade or "Lớp 12",
            "pre": None,
            "post": None,
            "minutes": None,
            "pair_count": 0,
            "note": "Chưa có cặp Pre/Post trong nhật ký — giáo viên nhập tay hoặc chọn nguồn nghiên cứu.",
        }

    grade = chosen["grade"]
    if grade and not str(grade).startswith("Lớp"):
        try:
            grade = f"Lớp {int(grade)}"
        except (TypeError, ValueError):
            grade = str(grade)

    return {
        "source": "observed_pair",
        "name": chosen["name"],
        "subject": chosen["subject"] or preferred_subject or "Toán học",
        "grade": grade or preferred_grade or "Lớp 12",
        "pre": float(chosen["pre"]),
        "post": float(chosen["post"]),
        "minutes": int(chosen["minutes"]) if chosen.get("minutes") is not None else None,
        "pair_count": len(pairs),
        "note": f"Tự điền từ {len(pairs)} cặp Pre/Post quan sát trong nhật ký/CSDL phiên.",
    }


def cohort_summary(logs: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    pairs = collect_pre_post_pairs(logs)
    if not pairs:
        return {"n_pairs": 0, "mean_pre": None, "mean_post": None, "mean_delta": None, "improved_share": None}
    n = len(pairs)
    mean_pre = sum(p["pre"] for p in pairs) / n
    mean_post = sum(p["post"] for p in pairs) / n
    mean_delta = mean_post - mean_pre
    improved = sum(1 for p in pairs if p["delta"] > 0) / n
    return {
        "n_pairs": n,
        "mean_pre": round(mean_pre, 3),
        "mean_post": round(mean_post, 3),
        "mean_delta": round(mean_delta, 3),
        "improved_share": round(improved, 3),
    }
