# -*- coding: utf-8 -*-
"""Smoke: nạp đề thật Toán 12 + chấm grade_exam_by_profile (không cần Streamlit UI)."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

from real_exam_engine import get_baseline_full_exams
from services.curriculum_policy import assessment_profile, prepare_exam_for_delivery
from services.scoring_service import grade_exam_by_profile
from qa_runtime import mcq_answer_matches


def main():
    profile = assessment_profile("Toán học", 12)
    print("PROFILE", profile["counts"], profile["weights"], profile["scope"])
    exams = get_baseline_full_exams("Toán học", 12) or []
    print("BANK", len(exams))
    if not exams:
        raise SystemExit("no bank exams")
    exam = exams[0]
    # normalize delivery if needed
    try:
        exam = prepare_exam_for_delivery(json.loads(json.dumps(exam)), "Toán học", 12, profile["minutes"])
    except Exception as exc:
        print("DELIVERY_WARN", type(exc).__name__, exc)
    p1, p2, p3 = len(exam.get("p1") or []), len(exam.get("p2") or []), len(exam.get("p3") or [])
    print("COUNTS", p1, p2, p3)

    # perfect answers where keys allow
    answers = {}
    p1_ok = 0
    for i, q in enumerate(exam.get("p1") or []):
        ans = str(q.get("ans") or "").strip().upper()[:1]
        opts = q.get("opt") or []
        if ans in "ABCD" and opts:
            answers[f"p1_{i}"] = opts[ord(ans) - ord("A")]
            if mcq_answer_matches(q, answers[f"p1_{i}"]):
                p1_ok += 1
        elif opts:
            # try text key
            answers[f"p1_{i}"] = opts[0]
    for i, q in enumerate(exam.get("p2") or []):
        for j, stmt in enumerate(q.get("stmts") or []):
            a = stmt.get("a") if "a" in stmt else stmt.get("ans")
            answers[f"p2_{i}_{j}"] = "Đúng" if a in (True, "Đúng", "true", "True", 1, "1") else "Sai"
    for i, q in enumerate(exam.get("p3") or []):
        answers[f"p3_{i}"] = str(q.get("ans", ""))

    graded = grade_exam_by_profile(exam, answers, "Toán học", 12)
    print("GRADED", {k: graded[k] for k in (
        "total", "score_p1", "score_p2", "score_p3", "w_p1", "w_p2", "w_p3",
        "p1_correct", "p3_correct", "p2_label", "p2_absolute_ladder", "has_p3"
    )})
    print("P1_MATCHER_OK", p1_ok, "/", p1)
    # blank paper
    blank = grade_exam_by_profile(exam, {}, "Toán học", 12)
    print("BLANK_TOTAL", blank["total"])
    assert blank["total"] == 0.0
    print("SMOKE_OK")


if __name__ == "__main__":
    main()
