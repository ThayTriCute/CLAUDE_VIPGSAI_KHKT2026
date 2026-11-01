"""Versioned references and conservative checks, not an academic certification."""
from copy import deepcopy
from datetime import date, datetime, timedelta, timezone
import hashlib
import html
import json
import re
from pathlib import Path

from services.academic_context import academic_context, canonical_subject, folded, normalize_grade, validate_exam_context
from qa_runtime import normalize_bool

POLICY_DATE = "2026-10-24"
T1_CONTEXT_REVISION = 2026110101
REGISTRY = Path(__file__).resolve().parents[1] / "data/legal_references.json"


def policy_evaluation_date():
    """Vietnam issue day; separate from the last source-review snapshot."""
    return datetime.now(timezone(timedelta(hours=7))).date().isoformat()


def legal_references(on_date=None, include_upcoming=False):
    today = date.fromisoformat(on_date or policy_evaluation_date())
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
    from services.lesson_sources import textbook_update_notice
    book_update = textbook_update_notice(subject, grade)
    edition_guidance = (book_update['note'] + ' Nguồn thông báo: ' + book_update['url']
                        + ' Không tuyên bố đã đọc bản chỉnh sửa nếu chưa có nội dung sách trong ngữ cảnh.') if book_update else ''
    evaluation_day = policy_evaluation_date()
    refs = legal_references(evaluation_day)
    codes = "; ".join(r["code"] for r in refs if r["scope"] in {"curriculum", "textbook", "assessment"})
    profile = assessment_profile(subject, grade)
    hint_guidance = ("Tiếng Anh — hint từ vựng: không dịch nghĩa hoặc diễn giải riêng phương án đúng, "
                     "không cho từ đồng nghĩa của đáp án hay loại sẵn phương án. Hỏi học sinh tự nhận diện "
                     "mục đích, quan hệ nghĩa hoặc dấu hiệu trong câu trước khi so sánh các lựa chọn. "
                     "Định nghĩa/dịch nghĩa và kết luận đáp án chỉ đặt trong explain sau nộp bài."
                     if subject == "Tiếng Anh" else "")
    return f"""\n[NGỮ CẢNH CHƯƠNG TRÌNH — ngày áp dụng {evaluation_day}; ngày rà soát nguồn {POLICY_DATE}]
Trạm {station}; môn {subject}; lớp {grade}; chủ đề {topic}; định hướng {pathway or 'chưa khai báo'}.
{hint_guidance}
Chương trình GDPT 2018 đọc cùng các sửa đổi còn áp dụng: {codes}.
Sử dụng Kết nối tri thức với cuộc sống, đối chiếu đính chính/cập nhật NXBGD; bộ sách thống nhất từ năm học 2026–2027 theo QĐ 3588 ngày 26/12/2025.
{edition_guidance}
{profile['label']}. {profile['note']}
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
    return text


def question_groups(exam):
    for part in ("p1", "p2", "p3", "part_viet"):
        if isinstance(exam.get(part), list):
            yield part, exam[part]
    reading = exam.get("part_doc_hieu")
    if isinstance(reading, dict) and isinstance(reading.get("questions"), list):
        yield "part_doc_hieu", reading["questions"]


def prepare_exam_for_delivery(exam, subject, grade, duration=45, custom_request=""):
    """Preserve academic payload; do not call heuristic answer/diagram healers."""
    subject, grade = validate_exam_context(exam, subject, grade)
    from services.request_scope import explicit_request_scope, question_scope_issue
    request_scope = explicit_request_scope(subject, custom_request)
    result = deepcopy(exam)
    validate_exam_structure(result, subject)
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
            if question_scope_issue(question, request_scope):
                raise ValueError("Câu hỏi chưa khớp yêu cầu chỉ hàm bậc ba; cần thay đúng phạm vi trước khi xuất đề.")
            texts.extend(str(question.get(k, "")) for k in ("q", "explain"))
    check_current_facts("\n".join(texts))
    payload = {k: result[k] for k in ("p1", "p2", "p3", "part_doc_hieu", "part_viet") if k in result}
    result["curriculum_audit"] = {
        "policy_checked_at": POLICY_DATE, "policy_evaluated_on": policy_evaluation_date(), "textbook": "Kết nối tri thức với cuộc sống",
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


def matrix_html(subject, grade):
    profile = assessment_profile(subject, grade)
    counts = profile["counts"]
    return (f"<div><b>{html.escape(subject)} · Lớp {grade}</b><p>{html.escape(profile['label'])}</p>"
            f"<p>Số câu luyện tập mặc định (I / II / III): {counts[0]} / {counts[1]} / {counts[2]}; "
            f"{profile['minutes']} phút. Có thể điều chỉnh.</p><p>{html.escape(profile['note'])}</p>"
            "<p>Yêu cầu cần đạt và tỷ lệ mức độ nhận thức phải được giáo viên duyệt theo nội dung đã dạy.</p></div>")


def lesson_prompt(subject, grade, topic):
    from services.cognitive_levels import LEVEL_GUIDANCE
    visual_guidance = ""
    if canonical_subject(subject) == "Toán học":
        visual_guidance = (
            "\nBảng biến thiên: chỉ khi nội dung bài thực sự cần và có đủ dữ kiện, "
            "trình bày bảng Markdown với các hàng x, y′, y (bậc hai có thể x, y), "
            "đủ mốc, dấu đạo hàm, giá trị hoặc giới hạn và mũi tên theo đúng hàm đang xét; "
            "không thay bảng bằng đoạn văn xét dấu. Giữ các cột tương ứng để công cụ dựng bảng hiện có xử lý. "
            "Không tự bịa giới hạn, điểm gián đoạn hoặc thêm bảng giải tích cho bài không cần.\n"
            "Khi khảo sát ba dạng SGK, phải giữ đúng dạng không suy biến: bậc ba có a≠0; "
            "y=(ax+b)/(cx+d) có c≠0 và ad−bc≠0; "
            "y=(ax²+bx+c)/(dx+e) có a≠0, d≠0 và ae²−bde+cd²≠0. "
            "Nếu hệ số không thỏa, nêu rõ hàm không thuộc dạng đang xét; "
            "không dùng hàm hằng, mẫu hằng hoặc điểm khuyết làm ví dụ đạt của dạng phân thức này.\n"
            "Trước khi lập bảng hoặc đồ thị, kiểm tập xác định, nghiệm đạo hàm, dấu từng khoảng, "
            "cực trị, giới hạn và tiệm cận; thiếu dữ kiện thì nêu rõ, không tự bổ sung số liệu. "
            "Bảng ba hàng x, y′, y dùng cột xen kẽ mốc và khoảng: hàng x để trống ô khoảng; "
            "hàng y′ ghi dấu ở ô khoảng và 0 đúng mốc nghiệm; hàng y ghi giá trị ở mốc, "
            "mũi tên ↗ hoặc ↘ ở khoảng. Không chép các số -2, 0, 4, 1 từ ảnh mẫu. "
            "Đồ thị cần trục Ox/Oy, gốc O, khung nhìn chứa các đặc điểm quan trọng, "
            "tách nhánh tại điểm không xác định; tiệm cận nét đứt, nhãn không đè đường cong. "
            "Đồ thị và bảng phải cùng hàm số, cùng cực trị và giới hạn; "
            "không dùng hình ví dụ khác thay hình của bài. "
            "Biểu diễn giao Ox/Oy nếu có, cực trị và tâm đối xứng; dóng nét đứt tới hai trục "
            "(điểm nằm trên trục thì hình chiếu trùng điểm). Giữ phân số, căn thức và tọa độ vô tỉ "
            "ở dạng chính xác, không đổi thành số thập phân làm tròn. Nghiệm không có biểu thức "
            "ngắn được ký hiệu và định nghĩa chính xác theo thứ tự nghiệm của phương trình; "
            "không dùng ký hiệu chưa định nghĩa. Nhãn không đè trục, đường cong, nét dóng hoặc "
            "nhãn khác; tọa độ dài dùng chú giải rõ ràng. Áp dụng thống nhất trong bài và infographic.\n"

        )
    if canonical_subject(subject) == "Ngữ văn":
        visual_guidance += (
            "\nPhần 3 Ngữ văn: chọn nhiệm vụ theo mục tiêu đọc, viết, nói và nghe hoặc tiếng Việt "
            "của bài đang học. Với nghị luận, Bước 2 hỏi học sinh tự đề xuất luận điểm, tìm dẫn chứng "
            "và sắp xếp ý; với tự sự, tìm sự việc và trình tự kể; với đọc hiểu, tìm chi tiết trong "
            "ngữ liệu và giải thích cách hiểu. Không áp luận điểm nghị luận cho mọi thể loại, "
            "không nêu sẵn kết luận, không viết hộ hoặc áp đặt một cách cảm nhận duy nhất.\n"
        )
    if canonical_subject(subject) == "Ngữ văn":
        visual_guidance += (
            "\nDạy viết theo đúng thể loại: với kể trải nghiệm, học sinh tự chọn sự việc, tìm ý, "
            "lập dàn ý, viết bài hoàn chỉnh rồi đọc sửa theo tiêu chí ngôi thứ nhất nhất quán "
            "(em hoặc tôi đều được), trình tự hợp lý, chi tiết, cảm xúc, ý nghĩa, liên kết và chính tả. "
            "Trải nghiệm bình dị vẫn có giá trị; không bắt buộc cao trào hoặc biến cố kịch tính. "
            "Nếu mục tiêu bài là viết một bài văn, cần có hoạt động tạo bài viết hoàn chỉnh "
            "và tự sửa theo tiêu chí thể loại, không chỉ dàn ý và đoạn rời. Bài đọc hiểu hoặc "
            "tiếng Việt không bị buộc chuyển thành hai bài tập viết cả bài văn. "
            "Không yêu cầu luận điểm/dẫn chứng nghị luận cho bài kể chuyện.\n"
        )
    if canonical_subject(subject) == "Tin học" and re.search(
            r"\b(?:html|css|web)\b|trang mạng", folded(topic)):
        visual_guidance += (
            "\nHTML: phân biệt ngữ nghĩa tiêu đề cấp 1, đoạn văn và ngắt dòng với cách hiển thị. "
            "Nếu hỏi kích thước chữ hoặc khoảng cách đoạn, phải nêu điều kiện CSS mặc định/chưa tùy chỉnh. "
            "Thẻ rỗng như br không có thẻ đóng; không yêu cầu mọi thẻ đều có thẻ đóng. "
            "Bài sửa lỗi cần hỏi học sinh tự phát hiện và đề xuất cách sửa, không liệt kê sẵn toàn bộ bản sửa.\n"
        )
    visual_guidance += (
        "\nKhông gán VDC chỉ vì bài dài, nhiều bước, viết đoạn văn hoặc sửa cú pháp cơ bản. "
        "Chọn mức độ theo thao tác tư duy và yêu cầu cần đạt; chưa đủ căn cứ thì để trống nhãn.\n"
    )
    return policy_prompt(subject, grade, 1, topic) + LEVEL_GUIDANCE + visual_guidance + r"""
Soạn bài học với ba tiêu đề chính: '### PHẦN 1: BÀI HỌC', '### PHẦN 2: TRẮC NGHIỆM KHÁCH QUAN SOCRATIC', '### PHẦN 3: BÀI TẬP TỰ LUẬN'.
Phần 1: khởi động, hình thành kiến thức, ví dụ có lời giải phù hợp lớp, luyện tập và vận dụng; đặc trưng thể loại/môn học phải được giữ.
Phần 2: đúng 3 câu trắc nghiệm, mỗi câu có 4 phương án A/B/C/D và duy nhất một đáp án. Ghi CORRECT: cho đáp án nội bộ, EXPLAIN: cho giải thích nội bộ, HINT: cho gợi mở Socratic theo riêng ngữ cảnh câu hỏi. HINT chỉ dẫn dắt học sinh tự nghĩ; không giải hộ hoặc tiết lộ đáp án. Không dùng EXPLAIN thay HINT.
Phần 3: đúng 2 câu tự luận, mỗi câu hướng dẫn đủ bốn bước Pólya bằng tiếng Việt: Bước 1: Tìm hiểu đề; Bước 2: Lập kế hoạch; Bước 3: Thực hiện kế hoạch; Bước 4: Kiểm tra và nhìn lại. Chỉ đặt câu hỏi hoặc hướng dẫn để học sinh tự thực hiện, không giải hộ, không đưa đáp án. Phần 1 vẫn được giải thích lý thuyết và có ví dụ minh họa; không áp quy tắc giấu lời giải của Socratic sang Phần 1.
Mỗi câu Phần 2 và Phần 3 mở đầu 'Câu n. [Mức độ: NB/TH/VD/VDC]' (chọn một nhãn, hoặc để rỗng nếu chưa đủ căn cứ). Tiếp theo là nội dung câu, các dòng OUTCOME: yêu cầu cần đạt; COGNITIVE_REASON: căn cứ phân loại; COGNITIVE_STEPS: ["thao tác tư duy 1", "thao tác tư duy 2"]. Đây là đề xuất cần giáo viên duyệt, không mặc định tất cả câu là vận dụng.
Công thức đặt trong $...$ hoặc $$...$$; hóa học dùng \ce{...}, đơn vị và chỉ số đúng bản chất. Không bọc công thức bằng backtick, không tự thay omega thành vô cực.
Chỉ tạo hình/bảng khi có đủ dữ kiện của bài, không chèn bảng mẫu hoặc số liệu không có căn cứ. Nội dung ngắn gọn, đầy đủ, không tự gắn nhãn đã được Bộ kiểm duyệt.
"""


def lesson_generation_request(subject, grade, topic):
    """Promote existing policy/level instructions without duplicating their text."""
    from services.cognitive_levels import LEVEL_GUIDANCE
    prefix = policy_prompt(subject, grade, 1, topic) + LEVEL_GUIDANCE
    system = policy_prompt(subject, grade, 1) + LEVEL_GUIDANCE
    full = lesson_prompt(subject, grade, topic)
    if not full.startswith(prefix):
        raise ValueError("Lesson instruction boundary changed; review request builder.")
    return system, json.dumps({"lesson_topic": str(topic)}, ensure_ascii=False) + "\n" + full[len(prefix):]


def exam_generation_request(subject, grade, topics, counts, code, custom="", pathway=""):
    """Keep custom requests/schema in user content; no new API call or retry."""
    from services.cognitive_levels import LEVEL_GUIDANCE
    # Materialize once so callers may supply an iterable without losing topics.
    topics = list(topics)
    prefix = policy_prompt(subject, grade, 3, "; ".join(topics), pathway) + LEVEL_GUIDANCE
    system = policy_prompt(subject, grade, 3) + LEVEL_GUIDANCE
    full = exam_prompt(subject, grade, topics, counts, code, custom, pathway)
    if not full.startswith(prefix):
        raise ValueError("Exam instruction boundary changed; review request builder.")
    context = json.dumps({"selected_topics": topics, "pathway": str(pathway)}, ensure_ascii=False)
    return system, context + "\n" + full[len(prefix):]


def exam_prompt(subject, grade, topics, counts, code, custom="", pathway=""):
    from services.web_question_contract import WEB_QUESTION_INSTRUCTION
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
    evidence_schema = {"level": "", "learning_outcome": "", "cognitive_rationale": "", "solution_steps": [],
                       "hint": "Câu hỏi gợi mở theo riêng ngữ cảnh câu này; không giải hộ hoặc đưa đáp án"}
    for key in ("p1", "p2", "p3", "part_viet"):
        for question in schema.get(key, []):
            question.update(evidence_schema)
            for stmt in question.get("stmts", []):
                stmt.update(evidence_schema)
    for question in schema.get("part_doc_hieu", {}).get("questions", []):
        question.update(evidence_schema)
    from services.request_scope import explicit_request_scope, request_scope_prompt
    return (policy_prompt(subject, grade, 3, "; ".join(topics), pathway) + LEVEL_GUIDANCE + request_scope_prompt(explicit_request_scope(subject, custom)) + "\n"
            + "\nTrường hint là gợi mở Socratic độc lập; explain và ans dành cho giải thích/chấm bài, không dùng thay hint. Không tiết lộ đáp án hoặc giải hộ trong hint."
            + structure + WEB_QUESTION_INSTRUCTION + "\nYêu cầu tùy biến trong phạm vi môn/lớp đã chọn: " + str(custom)
            + "\nTự giải và đối chiếu đáp án với giả thiết; thiếu hình thì không đặt câu yêu cầu đọc hình đó. Không sao chép nguồn thiếu bằng chứng hoặc tự nhận là đề thật."
            + "\nChỉ xuất JSON hợp lệ theo schema sau (mở rộng số câu theo cấu hình):\n" + json.dumps(schema, ensure_ascii=False))
