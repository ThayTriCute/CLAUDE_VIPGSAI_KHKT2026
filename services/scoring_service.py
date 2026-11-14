# VIP 74.1 - HỆ THỐNG GIA SƯ AI THPT 2026 (CHUẨN GDPT 2018 - BẢN VÁ HOÀN THIỆN ĐA MÔN & ĐA KHỐI LỚP)
"""
SERVICE CHẤM ĐIỂM KHẢO THÍ — GSAI THPT 2026
- Thang bậc Phần II theo QĐ 764/QĐ-BGDĐT (0.1 / 0.25 / 0.5 / 1.0).
- Trạm 3 UI và test dùng grade_exam_by_profile (assessment_profile đa môn/đa lớp).
- grade_part1/2/3 giữ tương thích ngược (Tin0530 / test cũ); đường học sinh chính là grade_exam_by_profile.
"""
from __future__ import annotations

T3_SCORING_REVISION = 2026111415  # reload contract cho worker Streamlit

from typing import Any, Dict, List, Optional, Tuple

from qa_runtime import mcq_answer_matches, normalize_bool, short_answer_matches


def calculate_part2_statement_score(correct_statements: int) -> float:
    """Thang bậc Phần II (Đúng/Sai) theo QĐ 764/QĐ-BGDĐT."""
    return {1: 0.1, 2: 0.25, 3: 0.5, 4: 1.0}.get(int(correct_statements or 0), 0.0)


def part2_ladder_caption(w_per_question: float) -> str:
    """Nhãn trung thực: tuyệt đối QĐ 764 khi mỗi câu = 1.0; ngược lại là thang luyện tập tỷ lệ."""
    if float(w_per_question or 0) <= 0:
        return "không có Phần II"
    if abs(float(w_per_question) - 1.0) < 1e-9:
        return "0.1-0.25-0.5-1.0 (QĐ 764)"
    return "thang luyện tập tỷ lệ theo bậc QĐ 764"


def grade_part1(
    questions: List[Dict[str, Any]],
    user_answers: Dict[str, Any],
    max_score: float = None,
    subject: str = "Toán học",
) -> Tuple[float, int, int]:
    """Chấm Phần I — tương thích cũ. Ưu tiên max_score; không thì suy theo môn (không theo lớp)."""
    if not questions:
        return 0.0, 0, 0
    correct_count = 0
    total = len(questions)
    for idx, q in enumerate(questions):
        if mcq_answer_matches(q, user_answers.get(f"p1_{idx}")):
            correct_count += 1
    if max_score is not None:
        target_max = float(max_score)
    elif subject == "Tiếng Anh":
        target_max = 10.0
    elif any(
        k in str(subject).lower()
        for k in ["vật lý", "vật lí", "hóa học", "sinh học", "khtn", "khoa học tự nhiên", "địa lý", "địa lí"]
    ):
        target_max = 4.5
    elif any(
        k in str(subject).lower()
        for k in ["lịch sử", "gdkt", "công dân", "tin học", "công nghệ"]
    ):
        target_max = 6.0
    else:
        target_max = 3.0
    score = (correct_count / total) * target_max if total > 0 else 0.0
    return round(score, 2), correct_count, total


def grade_part2(questions: List[Dict[str, Any]], user_answers: Dict[str, Any]) -> Tuple[float, int, int]:
    """Chấm Phần II tuyệt đối theo bậc QĐ 764 (mỗi câu tối đa 1.0) — tương thích cũ."""
    if not questions:
        return 0.0, 0, 0
    total_score = 0.0
    total_stmts = 0
    correct_stmts = 0
    for q_idx, q in enumerate(questions):
        stmts = q.get("stmts", [])
        q_correct = 0
        for s_idx, stmt in enumerate(stmts):
            total_stmts += 1
            user_val = str(user_answers.get(f"p2_{q_idx}_{s_idx}", "Chưa chọn")).strip()
            expected_bool = normalize_bool(stmt.get("a") if "a" in stmt else stmt.get("ans"))
            if expected_bool is None:
                continue
            expected_str = "Đúng" if expected_bool else "Sai"
            if user_val == expected_str:
                q_correct += 1
                correct_stmts += 1
        total_score += calculate_part2_statement_score(q_correct)
    return round(total_score, 2), correct_stmts, total_stmts


def grade_part3(
    questions: List[Dict[str, Any]],
    user_answers: Dict[str, Any],
    max_score: float = None,
    subject: str = "Toán học",
) -> Tuple[float, int, int]:
    """Chấm Phần III — tương thích cũ; hỗ trợ TLN số và văn bản ngắn."""
    if not questions:
        return 0.0, 0, 0
    correct_count = 0
    total = len(questions)
    for idx, q in enumerate(questions):
        user_val = str(user_answers.get(f"p3_{idx}", "")).strip()
        expected = str(q.get("ans", "")).strip()
        if short_answer_matches(user_val, expected, q.get("rounding_decimals")):
            correct_count += 1
    if max_score is not None:
        score = (correct_count / total) * float(max_score) if total > 0 else 0.0
    elif any(
        k in str(subject).lower()
        for k in ["vật lý", "vật lí", "hóa học", "sinh học", "khtn", "khoa học tự nhiên", "địa lý", "địa lí"]
    ):
        score = correct_count * 0.25
    else:
        score = correct_count * 0.5
    return round(score, 2), correct_count, total


def grade_exam_by_profile(
    exam: Dict[str, Any],
    user_answers: Dict[str, Any],
    subject: str,
    grade: int,
) -> Dict[str, Any]:
    """API chấm điểm duy nhất cho Trạm 3 (đa môn × lớp 6–12).

    - Trọng số lấy từ assessment_profile; Tiếng Anh ép (10,0,0).
    - Phần có mặt được quy về thang 10 (scale = 10 / tổng trọng số phần hiện có).
    - Phần II: ladder(k) × (w_p2 / N_p2); khi w/N = 1 trùng tuyệt đối QĐ 764.
    """
    from services.curriculum_policy import assessment_profile

    profile = assessment_profile(subject, grade)
    base_p1, base_p2, base_p3 = profile["weights"]
    if subject == "Tiếng Anh":
        base_p1, base_p2, base_p3 = 10.0, 0.0, 0.0

    p1_items = list(exam.get("p1") or [])
    p2_items = list(exam.get("p2") or [])
    p3_items = list(exam.get("p3") or [])

    present = (bool(p1_items), bool(p2_items), bool(p3_items))
    bases = (base_p1, base_p2, base_p3)
    active_max = sum(w for w, has in zip(bases, present) if has)
    scale = (10.0 / active_max) if active_max else 0.0
    w_p1 = base_p1 * scale if p1_items else 0.0
    w_p2 = base_p2 * scale if p2_items else 0.0
    w_p3 = base_p3 * scale if p3_items else 0.0

    p1_correct = 0
    for idx, q in enumerate(p1_items):
        if mcq_answer_matches(q, user_answers.get(f"p1_{idx}")):
            p1_correct += 1
    score_p1 = round((p1_correct / len(p1_items)) * w_p1, 2) if p1_items else 0.0

    score_p2 = 0.0
    p2_correct_stmts = 0
    p2_total_stmts = 0
    w_per_q2 = (w_p2 / len(p2_items)) if p2_items else 0.0
    for idx, q in enumerate(p2_items):
        stmts = q.get("stmts", []) or []
        q_correct = 0
        for s_idx, stmt in enumerate(stmts):
            p2_total_stmts += 1
            user_choice = str(user_answers.get(f"p2_{idx}_{s_idx}", "")).strip()
            expected_bool = normalize_bool(stmt["a"] if "a" in stmt else stmt.get("ans"))
            if expected_bool is None:
                continue
            expected_str = "Đúng" if expected_bool else "Sai"
            if user_choice == expected_str:
                q_correct += 1
                p2_correct_stmts += 1
        score_p2 += calculate_part2_statement_score(q_correct) * w_per_q2
    score_p2 = round(score_p2, 2)

    p3_correct = 0
    for idx, q in enumerate(p3_items):
        user_ans = str(user_answers.get(f"p3_{idx}", "")).strip()
        expected = str(q.get("ans", "")).strip()
        if short_answer_matches(user_ans, expected, q.get("rounding_decimals")):
            p3_correct += 1
    score_p3 = round((p3_correct / len(p3_items)) * w_p3, 2) if p3_items else 0.0

    total = min(10.0, round(score_p1 + score_p2 + score_p3, 2))
    return {
        "total": total,
        "score_p1": score_p1,
        "score_p2": score_p2,
        "score_p3": score_p3,
        "w_p1": w_p1,
        "w_p2": w_p2,
        "w_p3": w_p3,
        "p1_correct": p1_correct,
        "p1_total": len(p1_items),
        "p2_correct_stmts": p2_correct_stmts,
        "p2_total_stmts": p2_total_stmts,
        "p3_correct": p3_correct,
        "p3_total": len(p3_items),
        "w_per_q2": w_per_q2,
        "p2_absolute_ladder": abs(w_per_q2 - 1.0) < 1e-9,
        "p2_label": part2_ladder_caption(w_per_q2),
        "scope": profile.get("scope"),
        "profile_note": profile.get("note", ""),
        "has_p1": bool(p1_items),
        "has_p2": bool(p2_items),
        "has_p3": bool(p3_items),
    }
