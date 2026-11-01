"""Reference links are navigation aids, not invented textbook page citations."""
import hashlib
import html
from urllib.parse import quote_plus

from kntt_sgk_library import KNTT_DIGITAL_LIBRARY
from services.academic_context import academic_context, canonical_subject

PUBLISHER_PORTAL = "https://truonghocsoquocgia.nxbgd.vn/"
T1_CONTEXT_REVISION = 2026110101
PUBLISHER_2026_NOTICE = "https://nxbgd.vn/bai-viet/nha-xuat-ban-giao-duc-viet-nam-thong-bao-ve-viec-su-dung-sach-giao-khoa-nam-hoc-2026-2027"


def textbook_update_notice(subject, grade):
    """Publisher's 29 April notice; navigation is not page-level verification."""
    subject, grade = academic_context(subject, grade)
    affected = ((subject == "Lịch sử & Địa lý" and grade <= 9)
                or (grade == 10 and subject in {"Lịch sử", "Giáo dục kinh tế và pháp luật"})
                or (subject == "Địa lý" and grade == 12))
    if not affected:
        return None
    return {"url": PUBLISHER_2026_NOTICE, "checked_at": "2026-11-01",
            "note": "Môn/lớp này thuộc danh mục SGK chỉnh sửa năm 2026 theo thông báo NXBGD ngày 29/04/2026. "
                    "Cần đối chiếu bản chỉnh sửa và nội dung cập nhật tại NXBGD; bản cùng tên in từ 2025 trở về trước "
                    "chỉ dùng tham khảo. Liên kết sách bên dưới chưa xác minh là bản chỉnh sửa 2026."}


def books_for(subject, grade):
    subject, grade = academic_context(subject, grade)
    rows = KNTT_DIGITAL_LIBRARY.get(str(grade), {})
    books = next((books for key, books in rows.items() if canonical_subject(key) == subject), [])
    if not books:
        return [{"title": f"Tra cứu SGK {subject} lớp {grade} tại NXBGD", "url": PUBLISHER_PORTAL, "kind": "portal"}]
    result = []
    for book in books:
        book = dict(book)
        unavailable = book["url"] == PUBLISHER_PORTAL or "taphuan.nxbgd.vn" in book["url"] or book["url"].endswith("bo-sach-ket-noi-tri-thuc-voi-cuoc-song-sgk-sinh-hoc-10/")
        if unavailable:
            book.update(title="Tra cứu " + book["title"], url=PUBLISHER_PORTAL, kind="portal")
        else:
            book["kind"] = "reference_page"
        result.append(book)
    return result


def lesson_references(subject, grade, topic, channels, qr_builder):
    subject, grade = academic_context(subject, grade)
    topic = str(topic or subject).strip()
    channel = channels.get(subject, {"channel_name": "VTV7", "tag": "GD", "search_prefix": subject})
    code = "GSAI-" + hashlib.sha256(f"{subject}|{grade}|{topic}".encode()).hexdigest()[:12].upper()
    video = "https://www.youtube.com/results?search_query=" + quote_plus(f"{subject} lớp {grade} Kết nối tri thức {topic}")
    books = books_for(subject, grade)
    links = " · ".join(f'<a href="{html.escape(b["url"], quote=True)}" target="_blank" rel="noopener noreferrer">{html.escape(b["title"])}</a>' for b in books)
    update = textbook_update_notice(subject, grade)
    update_html = (f'<p>{html.escape(update["note"])} <a href="{html.escape(update["url"], quote=True)}" '
                   'target="_blank" rel="noopener noreferrer">Thông báo cập nhật của NXBGD</a></p>') if update else ''
    badge = (f'<div class="lesson-reference"><b>{html.escape(subject)} · Lớp {grade}</b> — {html.escape(topic)}'
             f'<p>Mã lưu nội bộ: {code}. Liên kết tra cứu theo môn/lớp; chưa xác minh bài/trang SGK cụ thể.</p>{update_html}{links}'
             f'<p><a href="{html.escape(video, quote=True)}" target="_blank" rel="noopener noreferrer">Tìm video theo chủ đề</a>'
             ' — đây là kết quả tìm kiếm, không phải video đã được thẩm định.</p></div>')
    return {"index_code": code, "chapter_name": topic, "clean_topic": topic,
            "book_name": f"Tài liệu tham khảo {subject} lớp {grade}", "channel_info": channel,
            "yt_deep_url": video, "qr_img_data": qr_builder(video), "badge_html": badge}
