# Trạm 3 — UX hỗ trợ phòng thi / giao đề (không lộ đáp án).
"""Helpers thuần cho phiếu ô đáp án, mã truy cập đề, lọc đề giáo viên.

Lấy cảm hứng UX từ bàn giáo viên hiện đại (trạng thái làm bài, mã đề, đề thầy lưu)
nhưng bám linh hồn GSAI: luyện tập Socratic, đúng môn/lớp, không bịa khóa.
"""
from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional


T1_CONTEXT_REVISION = 2026111215


def _filled(value: Any) -> bool:
    return str(value or "").strip() not in ("", "Chưa chọn", "None", "null")


def answer_sheet_cells(exam: Dict[str, Any], answers: Dict[str, Any], subject: str = "") -> List[Dict[str, Any]]:
    """Phiếu ô đáp án lúc đang làm bài — chỉ trạng thái đã/chưa, không hiện đúng/sai."""
    answers = answers or {}
    cells: List[Dict[str, Any]] = []
    if str(subject) == "Ngữ văn":
        dh = (exam or {}).get("part_doc_hieu") or {}
        for idx, _q in enumerate(dh.get("questions") or []):
            key = f"nv_dh_{idx}"
            cells.append({"id": key, "label": f"ĐH{idx + 1}", "status": "filled" if _filled(answers.get(key)) else "empty"})
        for idx, _q in enumerate((exam or {}).get("part_viet") or []):
            key = f"nv_v_{idx}"
            cells.append({"id": key, "label": f"V{idx + 1}", "status": "filled" if _filled(answers.get(key)) else "empty"})
        return cells

    for idx, _q in enumerate((exam or {}).get("p1") or []):
        key = f"p1_{idx}"
        cells.append({"id": key, "label": f"I.{idx + 1}", "status": "filled" if _filled(answers.get(key)) else "empty"})

    for idx, q in enumerate((exam or {}).get("p2") or []):
        stmts = q.get("stmts") or []
        total = max(len(stmts), 1)
        done = sum(1 for s_idx in range(len(stmts)) if _filled(answers.get(f"p2_{idx}_{s_idx}")))
        if done <= 0:
            status = "empty"
        elif done >= total:
            status = "filled"
        else:
            status = "partial"
        cells.append({
            "id": f"p2_{idx}",
            "label": f"II.{idx + 1}",
            "status": status,
            "done": done,
            "total": total,
        })

    for idx, _q in enumerate((exam or {}).get("p3") or []):
        key = f"p3_{idx}"
        cells.append({"id": key, "label": f"III.{idx + 1}", "status": "filled" if _filled(answers.get(key)) else "empty"})
    return cells


def answer_sheet_summary(cells: Iterable[Dict[str, Any]]) -> Dict[str, int]:
    cells = list(cells or [])
    filled = sum(1 for c in cells if c.get("status") == "filled")
    partial = sum(1 for c in cells if c.get("status") == "partial")
    empty = sum(1 for c in cells if c.get("status") == "empty")
    return {"total": len(cells), "filled": filled, "partial": partial, "empty": empty}


def render_answer_sheet_html(cells: List[Dict[str, Any]]) -> str:
    """HTML phiếu ô — màu trạng thái, không in đáp án."""
    summary = answer_sheet_summary(cells)
    if summary["total"] <= 0:
        return ""
    chips = []
    for cell in cells:
        status = cell.get("status") or "empty"
        if status == "filled":
            bg, border, fg = "#064e3b", "#34d399", "#ecfdf5"
            mark = "✓"
        elif status == "partial":
            bg, border, fg = "#78350f", "#fbbf24", "#fffbeb"
            mark = f"{cell.get('done', 0)}/{cell.get('total', 4)}"
        else:
            bg, border, fg = "#1e293b", "#64748b", "#cbd5e1"
            mark = "·"
        label = str(cell.get("label") or "")
        chips.append(
            f'<span title="{label}" style="display:inline-flex;align-items:center;justify-content:center;'
            f'min-width:2.4rem;height:1.85rem;margin:2px;padding:0 6px;border-radius:6px;'
            f'background:{bg};border:1px solid {border};color:{fg};font-size:11px;font-weight:700;">'
            f'{label}<span style="opacity:.85;margin-left:3px;font-weight:600;">{mark}</span></span>'
        )
    partial_bit = ""
    if summary["partial"]:
        partial_bit = f' · <b style="color:#fbbf24;">{summary["partial"]}</b> đang dở'
    return (
        '<div style="background:rgba(15,23,42,.72);border:1px solid #334155;border-radius:10px;'
        'padding:10px 12px;margin:8px 0 14px 0;">'
        f'<div style="color:#94a3b8;font-size:12px;margin-bottom:6px;">📋 Phiếu trả lời nhanh — '
        f'<b style="color:#e2e8f0;">{summary["filled"]}</b> đã làm'
        f'{partial_bit}'
        f' · <b style="color:#94a3b8;">{summary["empty"]}</b> trống'
        f' / {summary["total"]}</div>'
        f'<div style="display:flex;flex-wrap:wrap;">{"".join(chips)}</div>'
        '<div style="color:#64748b;font-size:11px;margin-top:6px;">Chỉ báo đã chọn/điền — không hiện đáp án đúng.</div>'
        "</div>"
    )


def normalize_access_code(value: Any) -> str:
    return str(value or "").strip()


def exam_matches_access_code(exam: Dict[str, Any], code: str, identity_fn=None) -> bool:
    code = normalize_access_code(code)
    if not code or not isinstance(exam, dict):
        return False
    if normalize_access_code(exam.get("code")) == code:
        return True
    if identity_fn is not None:
        try:
            if normalize_access_code(identity_fn(exam)) == code:
                return True
        except Exception:
            pass
    return False


def find_exam_by_access_code(exams: Iterable[Dict[str, Any]], code: str, identity_fn=None) -> Optional[Dict[str, Any]]:
    code = normalize_access_code(code)
    if not code:
        return None
    for exam in exams or []:
        if exam_matches_access_code(exam, code, identity_fn=identity_fn):
            return exam
    return None


def is_teacher_uploaded_exam(exam: Dict[str, Any]) -> bool:
    if not isinstance(exam, dict):
        return False
    if exam.get("is_teacher_upload"):
        return True
    source = str(exam.get("source") or exam.get("origin") or "").lower()
    return "teacher" in source or "giáo viên" in source or "giao vien" in source


def filter_exams_for_listing(exams: Iterable[Dict[str, Any]], *, teacher_only: bool = False, exclude_held_fn=None) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for exam in exams or []:
        if not isinstance(exam, dict):
            continue
        if teacher_only and not is_teacher_uploaded_exam(exam):
            continue
        if exclude_held_fn is not None:
            try:
                if exclude_held_fn(exam):
                    continue
            except Exception:
                pass
        out.append(exam)
    return out
