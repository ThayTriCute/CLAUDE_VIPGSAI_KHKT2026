"""Restore source figures only when a local registry entry matches.

Claude-safe identity (không kẹt hash VIP):
1. `visual_id` / `source_figure_id` / `reviewed_visual_id` tường minh → khóa ổn định
2. Soft key: (môn, lớp, source/exam_code, original_number)
3. Content SHA chỉ là phương án cuối để đăng ký local sau này

Thiếu index / không khớp → None (fail-open). Không bao giờ raise vì hash VIP.
"""

from __future__ import annotations

import base64
import hashlib
import json
from functools import lru_cache
from pathlib import Path

from services.academic_context import academic_context


ROOT = Path(__file__).resolve().parents[1] / "data" / "reviewed_question_visuals"


def visual_identity(question, subject, grade):
    """Stable lookup key — prefer explicit/soft IDs over brittle full-stem SHA."""
    subject, grade = academic_context(subject, grade)
    if not isinstance(question, dict):
        question = {}
    for key in ("visual_id", "source_figure_id", "reviewed_visual_id"):
        explicit = question.get(key)
        if isinstance(explicit, str) and explicit.strip():
            return f"id:{subject}:{grade}:{explicit.strip()}"
    source = question.get("source") or question.get("exam_code") or question.get("paper_code") or ""
    if isinstance(source, dict):
        source = source.get("code") or source.get("id") or ""
    source = str(source).strip()
    qnum = question.get("original_number")
    if qnum is None:
        source_id = str(question.get("source_id") or "")
        tail = source_id.rsplit(".", 1)[-1]
        qnum = int(tail) if tail.isdigit() else question.get("q_num") or question.get("number")
    if source and qnum is not None and str(qnum).strip() != "":
        return f"soft:{subject}:{grade}:{source}:{qnum}"
    content = {key: question.get(key) for key in ("q", "opt", "ans", "stmts", "source")}
    content.update(subject=subject, grade=grade)
    return hashlib.sha256(json.dumps(content, ensure_ascii=False, sort_keys=True).encode()).hexdigest()

def clear_reviewed_visual_index_cache():
    _index.cache_clear()


@lru_cache(maxsize=1)
def _index():
    try:
        path = ROOT / "index.json"
        if not path.is_file():
            return {}
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("schema_version") != 1:
            return {}
        figures = data.get("figures", {})
        return figures if isinstance(figures, dict) else {}
    except (OSError, ValueError, TypeError):
        return {}


def reviewed_question_visual(question, subject, grade):
    identity = visual_identity(question, subject, grade)
    record = _index().get(identity)
    if not isinstance(record, dict) or record.get("review_status") != "source_region_reviewed":
        return None
    filename = record.get("file")
    if not isinstance(filename, str) or Path(filename).name != filename:
        return None
    try:
        path = ROOT / filename
        if path.stat().st_size > 4_000_000:
            return None
        data = path.read_bytes()
    except OSError:
        return None
    expected = record.get("sha256")
    if not data.startswith(b"\x89PNG\r\n\x1a\n"):
        return None
    if expected and hashlib.sha256(data).hexdigest() != expected:
        return None
    return {
        "image_base64": "data:image/png;base64," + base64.b64encode(data).decode("ascii"),
        "image_provenance": {
            "figure_only": True,
            "mapping_requires_review": False,
            "content_sha256": identity,
            "source_sha256": record.get("source_sha256", ""),
            "source_url": record.get("source_url", ""),
            "page": record.get("page"),
            "bbox": record.get("bbox"),
            "method": "reviewed_source_figure_restored",
        },
    }


def reviewed_question_specification(question, subject, grade):
    """Return transcribed mathematical constraints, separately from source pixels."""
    record = _index().get(visual_identity(question, subject, grade))
    if not isinstance(record, dict) or record.get("review_status") != "source_region_reviewed":
        return None
    specification = record.get("reconstruction")
    return specification if isinstance(specification, dict) else None
