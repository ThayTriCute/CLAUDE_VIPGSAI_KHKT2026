# -*- coding: utf-8 -*-
"""Mô phỏng đúng khối import app.py + chấm 1 đề — bắt stub raise cũ."""
import logging
logging.basicConfig()

from importlib import reload as _reload_scoring
import qa_runtime as _qa_runtime_for_scoring
_reload_scoring(_qa_runtime_for_scoring)
import services.scoring_service as _scoring_service_mod
if getattr(_scoring_service_mod, "T3_SCORING_REVISION", None) != 2026111219:
    _reload_scoring(_scoring_service_mod)
from services.scoring_service import grade_exam_by_profile

exam = {
    "p1": [{"q": "?", "opt": ["A.1", "B.2", "C.3", "D.4"], "ans": "A"}] * 12,
    "p2": [{"q": "?", "stmts": [{"t": "a", "a": True}, {"t": "b", "a": False},
                                {"t": "c", "a": True}, {"t": "d", "a": False}]}] * 4,
    "p3": [{"q": "?", "ans": "2"}] * 6,
}
answers = {}
for i in range(12):
    answers[f"p1_{i}"] = "A.1"
for i in range(4):
    answers[f"p2_{i}_0"] = "Đúng"
    answers[f"p2_{i}_1"] = "Sai"
    answers[f"p2_{i}_2"] = "Đúng"
    answers[f"p2_{i}_3"] = "Sai"
for i in range(6):
    answers[f"p3_{i}"] = "2"

r = grade_exam_by_profile(exam, answers, "Toán học", 12)
assert r["total"] == 10.0, r
assert "chưa sẵn sàng" not in str(r)
print("IMPORT_GRADE_OK", r["total"], r["p2_label"])
