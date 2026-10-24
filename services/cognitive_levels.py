"""Audit claimed cognitive demand; format/position is never evidence of a level."""
from collections import Counter
from copy import deepcopy
import hashlib
import json

from services.academic_context import folded

LEVELS = {
    "nb": "NB", "biet": "NB", "nhan biet": "NB",
    "th": "TH", "hieu": "TH", "thong hieu": "TH",
    "vd": "VD", "van dung": "VD",
    "vdc": "VDC", "van dung cao": "VDC",
}
LEVEL_GUIDANCE = """
MỨC ĐỘ NHẬN THỨC — PHẢI CÓ CĂN CỨ:
- Tham chiếu phụ lục CV 7991: Biết, Hiểu, Vận dụng trong từng dạng câu. Phạm vi kiểm tra định kì thực hiện theo hướng dẫn Sở/nhà trường; không áp cứng cho mọi bài luyện tập hoặc đề tốt nghiệp.
- NB: nhận ra/nhớ lại tri thức, khái niệm, dữ kiện đã học. TH: giải thích, diễn giải, phân loại hoặc liên hệ ý nghĩa trong nội dung đã học. VD: lựa chọn và sử dụng kiến thức/kĩ năng để giải quyết nhiệm vụ. Đối chiếu yêu cầu cần đạt của đúng môn/lớp, không chỉ nhìn động từ.
- VDC là nhãn phân hóa mở rộng trong app; khi đối chiếu khung ba mức có thể xếp trong VD, không tự tuyên bố Bộ bắt buộc một cột VDC riêng.
- Không suy NB từ trắc nghiệm, TH từ Đúng/Sai, VD/VDC từ trả lời ngắn; không suy từ số phép tính, độ dài, số liệu lớn hay thứ tự câu. Một câu Đúng/Sai cần căn cứ riêng cho từng ý.
- Mỗi câu/ý phải khai báo level (NB/TH/VD/VDC), learning_outcome (yêu cầu cần đạt, không bịa mã/trang), cognitive_rationale (vì sao nhiệm vụ cần mức đó), solution_steps (các thao tác tư duy để giải). Nêu rõ điều gì đã cho và điều gì học sinh phải tự chọn/suy luận. Nếu chưa đủ căn cứ thì để level rỗng; không đổi nhãn để đủ tỷ lệ.
- Đây là đề xuất của AI, chưa phải kết quả thẩm định. Tỷ lệ theo điểm phải có ma trận và bản đặc tả được giáo viên duyệt; không đồng nhất tỷ lệ số câu với tỷ lệ điểm. Mức độ nhận thức khác độ khó thống kê đo sau khi học sinh làm bài.
"""


def normalize_level(value):
    return LEVELS.get(folded(str(value or "")).strip(), "")


def annotate_question(question):
    """Retain the source claim, never grant approval based on self-authored fields."""
    result = dict(question)
    claimed = result.get("level_claimed", result.get("level", ""))
    result["level_claimed"] = claimed
    result["level"] = normalize_level(claimed)
    steps = result.get("solution_steps")
    evidence_present = (bool(str(result.get("learning_outcome") or "").strip())
                        and bool(str(result.get("cognitive_rationale") or "").strip())
                        and isinstance(steps, list) and bool(steps)
                        and all(isinstance(s, str) and s.strip() for s in steps))
    payload = {k: result.get(k) for k in ("q", "question", "t", "opt", "options", "ans", "correct", "a", "explain")}
    result["cognitive_audit"] = {
        "level": result["level"],
        "reference_bucket": {"NB": "Biết", "TH": "Hiểu", "VD": "Vận dụng", "VDC": "Vận dụng"}.get(result["level"], "Chưa xác định"),
        "status": "needs_teacher_review", "verified": False,
        "self_reported_evidence_present": evidence_present,
        "issue": "missing_or_ambiguous_level" if not result["level"] else "unreviewed_claim",
        "content_sha256": hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True).encode()).hexdigest(),
    }
    if isinstance(result.get("stmts"), list):
        result["stmts"] = [annotate_question(s) if isinstance(s, dict) else s for s in result["stmts"]]
    return result


def audit_exam_levels(exam):
    """Separate question/statement counts. No invented score percentages or labels."""
    result = deepcopy(exam)
    rows, question_counts, statement_counts = [], Counter(), Counter()
    groups = [(part, result.get(part, [])) for part in ("p1", "p2", "p3", "part_viet")]
    reading = result.get("part_doc_hieu")
    groups.append(("part_doc_hieu", reading.get("questions", []) if isinstance(reading, dict) else reading or []))
    for part, questions in groups:
        if not isinstance(questions, list):
            continue
        for i, question in enumerate(questions):
            if not isinstance(question, dict):
                continue
            q = annotate_question(question)
            # The delivery audit is sidecar metadata; leave source questions/answers intact.
            question_counts[q["level"] or "UNSPECIFIED"] += 1
            rows.append({"part": part, "question": i + 1, "claim": q["level_claimed"], **q["cognitive_audit"]})
            for j, stmt in enumerate(q.get("stmts", [])):
                if isinstance(stmt, dict):
                    statement_counts[stmt["level"] or "UNSPECIFIED"] += 1
                    rows.append({"part": part, "question": i + 1, "statement": j + 1,
                                 "claim": stmt["level_claimed"], **stmt["cognitive_audit"]})
    result["cognitive_audit"] = {"verified": False, "status": "needs_teacher_review",
        "question_claim_counts": dict(question_counts), "statement_claim_counts": dict(statement_counts),
        "point_matrix_status": "not_computed_without_teacher_point_allocation", "rows": rows,
        "note": "Thống kê nhãn khai báo, không chứng nhận mức độ. VDC là phân hóa mở rộng trong VD khi đối chiếu ba mức. Cần duyệt nội dung, yêu cầu cần đạt, lời giải và phân bổ điểm."}
    return result


def level_caption(question):
    level = normalize_level(question.get("level"))
    return f"{level} — nhãn đề xuất, chưa duyệt" if level else "Chưa xác định mức độ"
