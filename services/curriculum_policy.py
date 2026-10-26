"""Versioned references and conservative checks, not an academic certification."""
from copy import deepcopy
from datetime import date, datetime
from zoneinfo import ZoneInfo
import hashlib
import html
import json
import re
from pathlib import Path

from services.academic_context import academic_context, canonical_subject, folded, normalize_grade, validate_exam_context
from qa_runtime import normalize_bool

POLICY_DATE = "2026-10-24"
REGISTRY = Path(__file__).resolve().parents[1] / "data/legal_references.json"


def legal_references(on_date=None, include_upcoming=False):
    # Source audit date is provenance, not the date used to apply a law.
    today = date.fromisoformat(on_date) if on_date else datetime.now(ZoneInfo('Asia/Ho_Chi_Minh')).date()
    rows = json.loads(REGISTRY.read_text(encoding="utf-8"))["documents"]
    return [r for r in rows if r.get("status") != "draft"
            and (include_upcoming or date.fromisoformat(r["effective_from"]) <= today)
            and (not r.get("effective_until") or today < date.fromisoformat(r["effective_until"]))]


def assessment_profile(subject, grade):
    subject, grade = academic_context(subject, grade)
    if grade < 12:
        counts = (0, 0, 0) if subject == "Ngữ văn" else (20, 0, 0) if subject == "Tiếng Anh" else (12, 2, 2)
        return {"counts": counts, "minutes": 45, "weights": (4.0, 4.0, 2.0), "scope": "practice",
                "label": "Luyện tập theo lớp; số câu và thời lượng do người dạy chọn, không phải định dạng thi tốt nghiệp",
                "note": "Đánh giá ở trường theo TT 22/2021 và hướng dẫn áp dụng; không có một ma trận tốt nghiệp chung cho lớp 6–11."}
    if subject == "Ngữ văn":
        counts, minutes, weights = (0, 0, 0), 120, (4.0, 6.0, 0.0)
    elif subject == "Tiếng Anh":
        counts, minutes, weights = (40, 0, 0), 50, (10.0, 0.0, 0.0)
    elif subject == "Toán học":
        counts, minutes, weights = (12, 4, 6), 90, (3.0, 4.0, 3.0)
    elif subject in {"Vật lý", "Hóa học", "Sinh học", "Địa lý"}:
        counts, minutes, weights = (18, 4, 6), 50, (4.5, 4.0, 1.5)
    else:
        counts, minutes, weights = (24, 4, 0), 50, (6.0, 4.0, 0.0)
    note = "Chỉ tham chiếu cấu trúc QĐ 764 ngày 08/03/2024; đề tạo trong app là đề luyện tập, chưa được Bộ thẩm định."
    if subject == "Tin học":
        note += " Đề gốc có 6 câu Đ/S: 2 chung, 2 Khoa học máy tính, 2 Tin học ứng dụng; thí sinh làm 4 câu theo định hướng. App tạo 4 câu cho định hướng đã chọn."
    if subject == "Công nghệ":
        note += " Phải chọn định hướng Công nghiệp hoặc Nông nghiệp trước khi ra đề."
    return {"counts": counts, "minutes": minutes, "weights": weights, "scope": "graduation_reference",
            "label": "Luyện tập lớp 12, tham chiếu cấu trúc thi tốt nghiệp", "note": note}


def policy_prompt(subject, grade, station, topic="", pathway=""):
    subject, grade = academic_context(subject, grade)
    refs = legal_references()
    codes = "; ".join(r["code"] for r in refs if r["scope"] in {"curriculum", "textbook", "assessment"})
    profile = assessment_profile(subject, grade)
    from services.academic_scope import academic_scope_instruction
    scope_instruction = academic_scope_instruction(subject, grade, topic)
    return f"""\n[NGỮ CẢNH CHƯƠNG TRÌNH — rà soát nguồn ngày {POLICY_DATE}]
Trạm {station}; môn {subject}; lớp {grade}; chủ đề {topic}; định hướng {pathway or 'chưa khai báo'}.
Chương trình GDPT 2018 đọc cùng các sửa đổi còn áp dụng: {codes}.
Sử dụng Kết nối tri thức với cuộc sống, đối chiếu đính chính/cập nhật NXBGD; bộ sách thống nhất từ năm học 2026–2027 theo QĐ 3588 ngày 26/12/2025.
{profile['label']}. {profile['note']}
{scope_instruction}
Không có nội dung SGK hoặc văn bản gốc trong ngữ cảnh thì KHÔNG tuyên bố đã đọc/đối chiếu từng trang, không bịa số trang, trích dẫn, tác giả, URL hay xác nhận của Bộ.
Chỉ dùng nội dung đúng yêu cầu cần đạt của môn/lớp; danh sách chủ đề gợi ý của app không phải mục lục SGK đã kiểm định. Yêu cầu tùy biến không được đổi môn/lớp hoặc tự miễn kiểm tra chương trình.
Ngữ văn: dạy học có thể dùng văn bản KNTT đã học; đánh giá cuối học kì/cuối năm/cuối cấp tránh dùng lại văn bản đã học trong SGK theo CV 3175. Không được bịa tác giả/trích đoạn rồi gán cho tác phẩm có thật. Không áp yêu cầu này thành lệnh cấm mọi ngữ liệu SGK ở Trạm 1.
TT 17/2025 cập nhật Lịch sử và Địa lí, Lịch sử 10, Địa lí và GDCD/GDKT&PL theo phụ lục tương ứng. Số liệu hiện hành phải có mốc năm và nguồn; không trình bày 63/64 tỉnh thành như cơ cấu hiện tại, không tự sửa số liệu lịch sử thành số liệu hiện tại.
Không tự đổi dữ kiện/đáp án hoặc bù bảng/đồ thị bằng mẫu để làm câu hỏi có vẻ hợp lệ. Thiếu bằng chứng thì ghi rõ cần giáo viên đối chiếu.
Phân bố độ khó theo yêu cầu cần đạt và kế hoạch kiểm tra; không gọi một tỷ lệ NB/TH/VD/VDC tự chọn là tỷ lệ bắt buộc của Bộ.
Không dùng dự thảo như văn bản đang hiệu lực. Không có căn cứ để nói mọi hàm bậc bốn bị cấm trong toàn bộ CT 2018.
"""


def check_current_facts(text):
    """Reject a narrow current-geography contradiction, preserving historical data."""
    for sentence in re.split(r"[\n.!?]", str(text)):
        value = folded(sentence)
        old_count = re.search(r"\b(?:63|64)\s+tinh(?:\s+thanh)?\b", value)
        current = any(x in value for x in ("hien nay", "hien tai", "nuoc ta co", "viet nam co"))
        historical = any(x in value for x in ("truoc nam 2025", "truoc sap nhap", "truoc sap xep", "nam 2024", "nam 2023", "nam 2022"))
        if old_count and current and not historical:
            raise ValueError("Số tỉnh/thành đang được mô tả là hiện hành nhưng dùng dữ liệu cũ; cần đối chiếu nguồn và mốc thời gian.")


def validate_lesson_policy(text, subject, grade):
    subject, grade = academic_context(subject, grade)
    for line in str(text).splitlines()[:8]:
        clean = line.strip().lstrip("#* ")
        declared_subject = re.match(r"Môn(?: học)?\s*:\s*([^|;·]+)", clean, re.I)
        if declared_subject and canonical_subject(declared_subject[1].strip().rstrip("*")) != subject:
            raise ValueError("Bài học tự khai báo khác môn đang chọn; cần sinh lại hoặc sửa nguồn.")
        declared_grade = re.search(r"(?:lớp|khối)\s*:?\s*(\d{1,2})\b", clean, re.I)
        if declared_grade and (line.lstrip().startswith("#") or re.match(r"(?:khối lớp|lớp|khối)\s*:", clean, re.I)):
            if normalize_grade(declared_grade[1]) != grade:
                raise ValueError("Tiêu đề bài học khai báo khác lớp đang chọn.")
    check_current_facts(text)
    from services.math_publication import validate_math_text
    validate_math_text(text)
    return text


def question_groups(exam):
    for part in ("p1", "p2", "p3", "part_viet"):
        if isinstance(exam.get(part), list):
            yield part, exam[part]
    reading = exam.get("part_doc_hieu")
    if isinstance(reading, dict) and isinstance(reading.get("questions"), list):
        yield "part_doc_hieu", reading["questions"]


def prepare_exam_for_delivery(exam, subject, grade, duration=45, topics=(), custom=""):
    """Preserve academic payload; do not call heuristic answer/diagram healers."""
    subject, grade = validate_exam_context(exam, subject, grade)
    result = deepcopy(exam)
    validate_exam_structure(result, subject)
    from services.math_publication import validate_exam_math
    validate_exam_math(result)
    declared_book = folded(result.get("textbook") or result.get("textbook_series") or "")
    if "canh dieu" in declared_book or "chan troi sang tao" in declared_book:
        raise ValueError("Đề khai báo bộ sách khác KNTT; cần đối chiếu và chọn lại nguồn.")
    result.update(subject=subject, grade=grade)
    result.setdefault("duration", duration)
    texts = [result.get("title", "")]
    for _, questions in question_groups(result):
        for question in questions:
            if not isinstance(question, dict):
                raise ValueError("Câu hỏi không đúng cấu trúc; cần sửa dữ liệu nguồn.")
            validate_exam_context({"p1": [question]}, subject, grade)
            from services.academic_scope import check_exam_question_scope
            check_exam_question_scope(question, subject, grade, topics, custom)
            texts.extend(str(question.get(k, "")) for k in ("q", "explain"))
    check_current_facts("\n".join(texts))
    payload = {k: result[k] for k in ("p1", "p2", "p3", "part_doc_hieu", "part_viet") if k in result}
    result["curriculum_audit"] = {
        "policy_checked_at": POLICY_DATE, "textbook": "Kết nối tri thức với cuộc sống",
        "status": "needs_teacher_review", "academic_verified": False,
        "source_sha256": hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True).encode()).hexdigest(),
        "note": "Đã kiểm tra ngữ cảnh khai báo và một số mâu thuẫn xác định; chưa xác minh từng yêu cầu cần đạt/trang SGK/nguồn gốc."}
    from services.cognitive_levels import audit_exam_levels
    return audit_exam_levels(result)


def validate_exam_structure(exam, subject, counts=None):
    """Reject missing keys instead of inventing A, True, zero or a statement."""
    if not isinstance(exam, dict):
        raise ValueError("Đề thi phải là JSON object.")
    if subject == "Ngữ văn":
        reading = exam.get("part_doc_hieu") or {}
        if not isinstance(reading, dict) or not reading.get("text") or not reading.get("questions") or not exam.get("part_viet"):
            raise ValueError("Đề Ngữ văn thiếu ngữ liệu, câu hỏi đọc hiểu hoặc đề viết.")
    elif not any(exam.get(p) for p in ("p1", "p2", "p3")):
        raise ValueError("Đề thi không có câu hỏi.")
    if counts is not None:
        for part, expected in zip(("p1", "p2", "p3"), counts):
            if not isinstance(exam.get(part, []), list) or len(exam.get(part, [])) != expected:
                raise ValueError(f"Phần {part} chưa đúng {expected} câu theo cấu hình; không tự cắt hoặc bù câu khác.")
    for part, questions in question_groups(exam):
        for q in questions:
            if not isinstance(q, dict) or not isinstance(q.get("q"), str) or not q["q"].strip():
                raise ValueError("Câu hỏi thiếu nội dung.")
            if part == "p1":
                opts = q.get("opt")
                answer = str(q.get("ans", "")).strip()
                if not isinstance(opts, list) or len(opts) != 4 or not all(str(o).strip() for o in opts):
                    raise ValueError("Câu trắc nghiệm phải có đúng 4 phương án có nội dung.")
                if not answer or (answer.upper() not in {"A", "B", "C", "D"} and answer not in opts):
                    raise ValueError("Thiếu đáp án trắc nghiệm hợp lệ; không tự gán A.")
            elif part == "p2":
                stmts = q.get("stmts")
                if not isinstance(stmts, list) or len(stmts) != 4:
                    raise ValueError("Câu Đúng/Sai phải có đúng 4 mệnh đề.")
                for stmt in stmts:
                    if not isinstance(stmt, dict) or not str(stmt.get("t", "")).strip() or normalize_bool(stmt.get("a", stmt.get("ans"))) is None:
                        raise ValueError("Mệnh đề thiếu nội dung/đáp án xác định; không tự gán Đúng.")
            elif part == "p3" and (q.get("ans") is None or not str(q.get("ans", "")).strip()):
                raise ValueError("Thiếu đáp số trả lời ngắn; không tự gán 0.")
    return exam


def practice_initial_source(bank_exam, subject, grade, counts, allow_ai):
    """Choose an initial source, not certify its academic content or publish it."""
    subject, grade = academic_context(subject, grade)
    if isinstance(bank_exam, dict) and bank_exam:
        try:
            validate_exam_context(bank_exam, subject, grade)
            validate_exam_structure(bank_exam, subject, None if subject == "Ngữ văn" else counts)
        except (ValueError, TypeError):
            pass
        else:
            return "bank"
    return "ai" if allow_ai else "unavailable"


def matrix_html(subject, grade):
    profile = assessment_profile(subject, grade)
    counts = profile["counts"]
    return (f"<div><b>{html.escape(subject)} · Lớp {grade}</b><p>{html.escape(profile['label'])}</p>"
            f"<p>Số câu luyện tập mặc định (I / II / III): {counts[0]} / {counts[1]} / {counts[2]}; "
            f"{profile['minutes']} phút. Có thể điều chỉnh.</p><p>{html.escape(profile['note'])}</p>"
            "<p>Yêu cầu cần đạt và tỷ lệ mức độ nhận thức phải được giáo viên duyệt theo nội dung đã dạy.</p></div>")


def lesson_prompt(subject, grade, topic):
    from services.cognitive_levels import LEVEL_GUIDANCE
    return policy_prompt(subject, grade, 1, topic) + LEVEL_GUIDANCE + r"""
Soạn bài học với ba tiêu đề chính: '### PHẦN 1: BÀI HỌC', '### PHẦN 2: TRẮC NGHIỆM KHÁCH QUAN SOCRATIC', '### PHẦN 3: BÀI TẬP TỰ LUẬN'.
Phần 1: khởi động, hình thành kiến thức, ví dụ có lời giải phù hợp lớp, luyện tập và vận dụng; đặc trưng thể loại/môn học phải được giữ.
Phần 2: sinh CHÍNH XÁC 3 câu trắc nghiệm, đánh số Câu 1., Câu 2., Câu 3.; mỗi câu có đúng 4 phương án A./B./C./D. trên 4 dòng riêng. Ghi một dòng khóa chấm riêng 'ĐÁP ÁN: A/B/C/D' (chọn đúng một chữ), không đặt đáp án trong câu hỏi hay phương án. Sau khóa chấm, bắt buộc dòng 'GỢI MỞ SOCRATIC: ...?' là MỘT câu hỏi tiếng Việt, bám dữ kiện/khái niệm cụ thể của chính câu đó, gợi để học sinh tự làm bước tiếp theo. Không dùng một câu nhắc chung cho cả ba câu; không nhắc chữ cái phương án, không nêu kết quả, không tính toán thay học sinh. Nếu có 'GIẢI THÍCH:', đây là trường nội bộ riêng, tuyệt đối không dùng nó làm gợi mở cho học sinh.
Phần 3: sinh CHÍNH XÁC 2 bài tập tự làm, đánh số Câu 1. và Câu 2.; viết đầy đủ đề bài trước. Sau mỗi đề, bắt buộc đủ bốn tiêu đề trên các dòng riêng 'Bước 1: Tìm hiểu đề', 'Bước 2: Lập kế hoạch', 'Bước 3: Thực hiện kế hoạch', 'Bước 4: Kiểm tra và nhìn lại'. Dòng dưới mỗi bước chỉ đặt MỘT câu hỏi gợi mở BẰNG TIẾNG VIỆT, gắn với đúng đối tượng/đại lượng/chi tiết trong đề, để học sinh tự tư duy. Tuyệt đối không giải chi tiết, không biến đổi/tính toán thay học sinh, không viết đáp án hoặc đáp số. Quy tắc tiếng Việt áp dụng cả khi dạy môn Tiếng Anh: ngữ liệu/đề bài có thể bằng tiếng Anh, nhưng tiêu đề và câu hỏi hướng dẫn bốn bước phải bằng tiếng Việt.
Phân biệt rõ: Phần 1 được có ví dụ minh họa có lời giải để hình thành kiến thức; Phần 2 và Phần 3 là bài tập học sinh tự làm, không dùng lại lời giải ví dụ để giải hộ. Các trường OUTCOME/COGNITIVE_REASON/COGNITIVE_STEPS chỉ phục vụ đối soát nội bộ, viết trên dòng riêng, không đưa lời giải vào hướng dẫn cho học sinh.
Mỗi câu Phần 2 và Phần 3 mở đầu 'Câu n. [Mức độ: NB/TH/VD/VDC]' (chọn một nhãn, hoặc để rỗng nếu chưa đủ căn cứ). Tiếp theo là nội dung câu, các dòng OUTCOME: yêu cầu cần đạt; COGNITIVE_REASON: căn cứ phân loại; COGNITIVE_STEPS: ["thao tác tư duy 1", "thao tác tư duy 2"]. Đây là đề xuất cần giáo viên duyệt, không mặc định tất cả câu là vận dụng.
Công thức đặt trong $...$ hoặc $$...$$; hóa học dùng \ce{...}, đơn vị và chỉ số đúng bản chất. Không bọc công thức bằng backtick, không tự thay omega thành vô cực.
Chỉ tạo hình/bảng khi có đủ dữ kiện của bài, không chèn bảng mẫu hoặc số liệu không có căn cứ. Với ba câu trắc nghiệm trong đầu ra văn bản này, ưu tiên câu tự đủ dữ kiện bằng văn bản/công thức: phải ghi đầy đủ hàm số và dữ kiện, không viết 'như hình bên', 'bảng biến thiên sau' khi không kèm hình/bảng đọc được. Có thể hỏi về cách lập bảng biến thiên khi đã cho đủ công thức; đây không phải bảng dữ liệu đầu vào bị thiếu. Ghi nhãn ĐÁP ÁN và GỢI MỞ SOCRATIC bằng chữ thường định dạng văn bản, không bọc cả nhãn bằng Markdown. Mỗi tiêu đề Bước 1–4 trên dòng riêng và câu hỏi hướng dẫn ở dòng tiếp theo. Nội dung ngắn gọn, đầy đủ, không tự gắn nhãn đã được Bộ kiểm duyệt.
"""


def exam_prompt(subject, grade, topics, counts, code, custom="", pathway=""):
    from services.cognitive_levels import LEVEL_GUIDANCE
    subject, grade = academic_context(subject, grade)
    if subject == "Ngữ văn":
        schema = {"code": str(code), "subject": subject, "grade": grade,
                  "part_doc_hieu": {"text": "Ngữ liệu mới có nguồn thật; nếu tự sáng tác ghi rõ tự sáng tác", "author": "", "source": "",
                                     "questions": [{"q": "Câu đọc hiểu", "ans": "Hướng dẫn chấm", "point": 1.0, "explain": "Gợi ý"}]},
                  "part_viet": [{"q": "Đề viết theo lớp", "ans": "Rubric chấm", "point": 6.0, "explain": "Gợi ý"}]}
        structure = "Đọc hiểu và Viết, rubric tổng 10 điểm; ở lớp 12 tham chiếu 4/6. Số câu, độ dài văn bản và yêu cầu viết phải phù hợp lớp, không áp bài viết lớp 12 cho THCS."
    else:
        schema = {"code": str(code), "subject": subject, "grade": grade,
                  "p1": [{"q": "Câu hỏi", "opt": ["A. ...", "B. ...", "C. ...", "D. ..."], "ans": "B", "topic": "Chủ đề", "explain": "Gợi ý phương pháp"}],
                  "p2": [{"q": "Ngữ liệu", "stmts": [{"t": "Mệnh đề", "a": True}], "topic": "Chủ đề", "explain": "Gợi ý"}],
                  "p3": [{"q": "Câu trả lời ngắn", "ans": "2.5", "topic": "Chủ đề", "explain": "Gợi ý"}]}
        structure = f"Sinh đúng số câu p1/p2/p3 = {tuple(counts)}. Phần có 0 câu phải là []. Mỗi câu p2 có đúng 4 mệnh đề boolean. p3 có đáp số, đơn vị và quy tắc làm tròn rõ ràng. Tiếng Anh: câu hỏi, đoạn đọc và phương án bằng tiếng Anh; giải thích có thể bằng tiếng Việt."
    evidence_schema = {"level": "", "learning_outcome": "", "cognitive_rationale": "", "solution_steps": []}
    for key in ("p1", "p2", "p3", "part_viet"):
        for question in schema.get(key, []):
            question.update(evidence_schema)
            question["socratic_hint"] = "Một câu hỏi tiếng Việt gợi mở theo dữ kiện riêng của câu này; không giải hộ, không chỉ phương án hoặc kết quả"
            for stmt in question.get("stmts", []):
                stmt.update(evidence_schema)
    for question in schema.get("part_doc_hieu", {}).get("questions", []):
        question.update(evidence_schema)
        question["socratic_hint"] = "Câu hỏi gợi mở riêng theo ngữ liệu, không viết hộ câu trả lời"
    return (policy_prompt(subject, grade, 3, "; ".join(topics), pathway) + LEVEL_GUIDANCE + "\n"
            + structure + "\nYêu cầu tùy biến trong phạm vi môn/lớp đã chọn: " + str(custom)
            + "\nTự giải và đối chiếu đáp án với giả thiết; thiếu hình thì không đặt câu yêu cầu đọc hình đó. Không sao chép nguồn thiếu bằng chứng hoặc tự nhận là đề thật."
            + "\nChỉ xuất JSON hợp lệ theo schema sau (mở rộng số câu theo cấu hình):\n" + json.dumps(schema, ensure_ascii=False))
