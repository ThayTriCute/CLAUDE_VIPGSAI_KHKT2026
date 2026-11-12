# -*- coding: utf-8 -*-
"""Smoke chấm điểm đa môn/lớp bằng grade_exam_by_profile + đề synth đúng counts."""
from services.academic_context import subjects_for_grade
from services.curriculum_policy import assessment_profile
from services.scoring_service import grade_exam_by_profile


def synth(subject, grade, counts):
    c1, c2, c3 = counts
    exam = {"p1": [], "p2": [], "p3": []}
    for i in range(c1):
        exam["p1"].append({"q": "?", "opt": ["A.1", "B.2", "C.3", "D.4"], "ans": "A"})
    for i in range(c2):
        exam["p2"].append({"q": "?", "stmts": [{"t": "a", "a": True}, {"t": "b", "a": False},
                                               {"t": "c", "a": True}, {"t": "d", "a": False}]})
    for i in range(c3):
        exam["p3"].append({"q": "?", "ans": "3"})
    return exam


def perfect(exam):
    a = {}
    for i, q in enumerate(exam["p1"]):
        a[f"p1_{i}"] = q["opt"][0]
    for i, q in enumerate(exam["p2"]):
        for j, s in enumerate(q["stmts"]):
            a[f"p2_{i}_{j}"] = "Đúng" if s["a"] else "Sai"
    for i, q in enumerate(exam["p3"]):
        a[f"p3_{i}"] = q["ans"]
    return a


def main():
    fails = []
    n = 0
    for g in range(6, 13):
        for s in subjects_for_grade(g):
            if s == "Ngữ văn":
                continue
            n += 1
            counts = assessment_profile(s, g)["counts"]
            if counts == (0, 0, 0):
                continue
            exam = synth(s, g, counts)
            r = grade_exam_by_profile(exam, perfect(exam), s, g)
            if r["total"] != 10.0:
                fails.append((s, g, r["total"], r))
            blank = grade_exam_by_profile(exam, {}, s, g)
            if blank["total"] != 0.0:
                fails.append((s, g, "blank", blank["total"]))
    print("CHECKED", n, "FAILS", len(fails))
    for f in fails[:10]:
        print("FAIL", f)
    assert not fails
    # Địa 12 must expose P3
    dia = grade_exam_by_profile(synth("Địa lý", 12, (18, 4, 6)), perfect(synth("Địa lý", 12, (18, 4, 6))), "Địa lý", 12)
    assert dia["has_p3"] and dia["w_p3"] == 1.5
    print("DIA12_P3_OK", dia["w_p3"], dia["p2_label"])
    print("SMOKE_MULTI_OK")


if __name__ == "__main__":
    main()
