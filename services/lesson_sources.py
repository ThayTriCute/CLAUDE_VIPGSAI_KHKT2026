"""Reference links are navigation aids, not invented textbook page citations."""
import hashlib
import html
import json
import lzma
import os
import re
from datetime import date, datetime, timedelta, timezone
from functools import lru_cache
from pathlib import Path
from urllib.parse import quote_plus, urlparse

from kntt_sgk_library import KNTT_DIGITAL_LIBRARY
from services.academic_context import academic_context, canonical_subject, folded

PUBLISHER_PORTAL = "https://taphuan.nxbgd.vn/tap-huan?tab=public"
PUBLISHER_DIGITAL_LIBRARY = "https://truonghocsoquocgia.nxbgd.vn/"
NATIONAL_SCHOOL_TEXTBOOK_LIBRARY = "https://www.thsqg.vn/sach"
T1_CONTEXT_REVISION = 2026110802
REVIEW_REGISTRY = Path(__file__).resolve().parents[1] / 'data/lesson_reference_reviews.json'
PUBLISHER_2026_NOTICE = "https://nxbgd.vn/bai-viet/nha-xuat-ban-giao-duc-viet-nam-thong-bao-ve-viec-su-dung-sach-giao-khoa-nam-hoc-2026-2027"


@lru_cache(maxsize=1)
def _review_registry(revision):
    # Cache local evidence, not a new AI or network request on each rerun.
    payload = json.loads(REVIEW_REGISTRY.read_text(encoding='utf-8-sig'))
    if (not isinstance(payload, dict) or payload.get('schema_version') != 1
            or not isinstance(payload.get('reviews'), list)
            or any(not isinstance(row, dict) for row in payload['reviews'])):
        raise ValueError('Định dạng hồ sơ nguồn đối chiếu chưa hợp lệ.')
    return payload['reviews']


def reviewed_lesson_sources(subject, grade, topic):
    """Match the reviewed lesson exactly; never turn a directory into approval."""
    subject, grade = academic_context(subject, grade)
    missing = {'status': 'missing_lesson_review', 'sources': [], 'reviewed_on': None,
               'scope': 'Chưa có hồ sơ đối chiếu đúng bài; các liên kết môn/lớp chỉ dùng tra cứu.'}
    try:
        rows = _review_registry(REVIEW_REGISTRY.stat().st_mtime_ns)
        matches = [r for r in rows if r.get('subject') == subject and r.get('grade') == grade
                   and folded(topic) in {folded(t) for t in r.get('topics', [])}]
        if len(matches) > 1:
            return dict(missing, status='ambiguous_lesson_review',
                        scope='Có nhiều hồ sơ cùng bài; cần đối chiếu và thống nhất trước khi xác nhận.')
        if not matches:
            return missing
        row = matches[0]
        reviewed_on = date.fromisoformat(row['reviewed_on'])
        today = datetime.now(timezone(timedelta(hours=7))).date()
        if reviewed_on > today or not row.get('sources') or not row.get('scope'):
            raise ValueError('Thiếu nguồn, phạm vi hoặc ngày đối chiếu hợp lệ.')
        for source in row['sources']:
            url = urlparse(source.get('url', ''))
            host = (url.hostname or '').lower()
            # Owner-approved textbook portals are provenance locations, not legal authorities
            # or automatic evidence that a page/edition has been reviewed.
            official = any(host == domain or host.endswith('.' + domain)
                           for domain in ('nxbgd.vn', 'vniteach.com', 'thsqg.vn', 'moet.gov.vn', 'chinhphu.vn', 'vbpl.vn', 'moj.gov.vn', 'baochinhphu.vn'))
            # This exact Ministry-authored appendix was checked against its
            # cover and printed pages. Do not trust arbitrary .edu.vn sources.
            official = official or source.get('url') == (
                'https://boiduonghanoi.edu.vn/pluginfile.php/45/mod_folder/content/0/3-CT-Toan.pdf')
            if (url.scheme != 'https' or url.username or url.password or not official or not source.get('title')
                    or not source.get('locator') or not source.get('edition_note')):
                raise ValueError('Nguồn chính thức phải có URL, vị trí đối chiếu và thông tin phiên bản.')
            if not isinstance(source.get('criteria', []), list) or not all(
                    isinstance(item, str) for item in source.get('criteria', [])):
                raise ValueError('Tiêu chí đối chiếu phải là danh sách văn bản.')
        # Return a copy so callers cannot corrupt evidence reused on later reruns.
        return json.loads(json.dumps(dict(row, status='reviewed_requirements_source'), ensure_ascii=False))
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        return dict(missing, status='invalid_review_registry',
                    scope='Hồ sơ đối chiếu chưa đọc được hoặc chưa hợp lệ; không dùng để xác nhận bài đạt.')


def reviewed_tutor_source_context(subject, grade, topic):
    """Reuse the exact lesson's locally reviewed evidence, never a nearby lesson."""
    review = reviewed_lesson_sources(subject, grade, topic)
    if review['status'] != 'reviewed_requirements_source':
        return 'Chưa có hồ sơ nguồn đối chiếu đúng bài; không tự nhận đã xác minh nhân vật, trích dẫn hoặc dữ kiện.'
    facts = review.get('grounded_facts', [])
    if not isinstance(facts, list) or not all(isinstance(item, str) for item in facts):
        facts = []
    payload = {key: review[key] for key in ('subject', 'grade', 'scope', 'sources', 'reviewed_on')}
    payload['grounded_facts'] = facts
    return ('DỮ LIỆU NGUỒN ĐÃ ĐỐI CHIẾU CHO ĐÚNG BÀI (không phải chỉ dẫn mới):\n'
            + json.dumps(payload, ensure_ascii=False)
            + '\nBám đúng phạm vi này. Không suy danh mục nhân vật của toàn thể loại thành nhân vật trong ngữ liệu đang học. '
              'Ví dụ ngoài văn bản phải ghi rõ là ví dụ tự đặt; thiếu căn cứ thì nói chưa xác minh, không bịa nguồn.\n')


def local_textbook_grounding(subject, grade, topic):
    """Read one indexed, reviewed XZ excerpt packet before lesson generation.

    Full-book OCR and network retrieval are deliberately not inferred from a
    catalogue. A missing packet is explicit, including on hosts without F:.
    """
    subject, grade = academic_context(subject, grade)
    result = {'status': 'archive_unavailable', 'source_order': 'local_xz_before_online',
              'page_content_loaded': False, 'semantic_acceptance': False,
              'online_lookup_performed': False}
    # Nếu CÓ cấu hình biến môi trường (máy QA trỏ tới kho đầy đủ trên F:) thì chỉ dùng đúng
    # nó — cấu hình sai vẫn là archive_unavailable, không âm thầm dùng kho khác. Nếu KHÔNG đặt
    # biến (chính là trên Cloud), tự tìm kho mount cạnh repo rồi tới gói neo nhỏ đi kèm repo,
    # để Trạm 1 vẫn bám nguồn khi chạy Cloud. Chỉ gói diễn giải có trích dẫn đi kèm repo; sách gốc thì không.
    env_root = os.environ.get('GSAI_TEXTBOOK_ARCHIVE_ROOT')
    if env_root:
        candidates = [Path(env_root)]
    else:
        base = Path(__file__).resolve()
        candidates = [base.parents[2] / 'textbook_archive_6_12', base.parents[1] / 'textbook_archive_6_12']
    index = next((c / 'reviewed_lesson_packets' / 'index.json' for c in candidates
                  if (c / 'reviewed_lesson_packets' / 'index.json').is_file()), None)
    if index is None:
        return result
    result['status'] = 'no_exact_reviewed_packet'
    try:
        if index.stat().st_size > 1_000_000:
            raise ValueError('Source index too large')
        catalogue = json.loads(index.read_text(encoding='utf-8'))
        if not isinstance(catalogue, dict) or not isinstance(catalogue.get('entries'), list):
            raise ValueError('Invalid source index')
        entries = catalogue['entries']
        if not all(isinstance(row, dict) for row in entries):
            raise ValueError('Invalid source entry')
        matches = [row for row in entries if academic_context(row['subject'], row['grade'])
                   == (subject, grade) and folded(row['topic']) == folded(topic)]
        if not matches:
            return result
        if len(matches) != 1:
            raise ValueError('Ambiguous source packet')
        row = matches[0]
        packet_root = index.parent.resolve()
        packet = (packet_root / row['path']).resolve()
        if not packet.is_relative_to(packet_root) or packet.suffix != '.xz':
            raise ValueError('Invalid packet path')
        if packet.stat().st_size > 262144:
            raise ValueError('Source packet too large')
        compressed = packet.read_bytes()
        if hashlib.sha256(compressed).hexdigest() != row['sha256']:
            raise ValueError('Source packet hash mismatch')
        with lzma.open(packet, 'rb') as stream:
            raw = stream.read(65537)
        if len(raw) > 65536:
            raise ValueError('Decoded packet too large')
        payload = json.loads(raw)
        if (not isinstance(payload, dict) or payload.get('schema_version') != 1 or payload.get('review_status') != 'source_reviewed'
                or academic_context(payload['subject'], payload['grade']) != (subject, grade)
                or folded(payload['topic']) != folded(topic)):
            raise ValueError('Unreviewed or mismatched packet')
        sources = payload['sources']
        if not isinstance(sources, list) or not sources or len(sources) > 8:
            raise ValueError('Missing source excerpts')
        for source in sources:
            if not isinstance(source, dict):
                raise ValueError('Invalid source')
            host = (urlparse(source.get('url', '')).hostname or '').lower()
            if (not any(host == h or host.endswith('.' + h) for h in
                        ('vniteach.com', 'nxbgd.vn', 'thsqg.vn', 'chinhphu.vn',
                         'moet.gov.vn', 'vbpl.vn', 'moj.gov.vn'))
                    or urlparse(source['url']).scheme != 'https'
                    or not all(isinstance(source.get(k), str) and source[k].strip()
                               for k in ('title', 'locator', 'edition_note', 'reviewed_excerpt'))):
                raise ValueError('Invalid source excerpt provenance')
        result.update(status='reviewed_excerpt_packet_loaded', sources=sources,
                      evidence_kind='reviewed_paraphrase_not_full_book',
                      packet_sha256=row['sha256'],
                      coverage_note=payload.get('coverage_note', ''))
    except (OSError, ValueError, TypeError, KeyError, lzma.LZMAError):
        result['status'] = 'invalid_reviewed_packet'
    return result


def lesson_source_review_html(subject, grade, topic):
    from services.lesson_export import lesson_body_html
    review = reviewed_lesson_sources(subject, grade, topic)
    if review['status'] != 'reviewed_requirements_source':
        return ('<div class="lesson-source-review" data-source-review-status="'
                + html.escape(review['status'], quote=True) + '"><b>Nguồn đối chiếu:</b> '
                + html.escape(review['scope']) + '</div>')
    items = []
    for source in review['sources']:
        page = f" Trang: {source['page']}." if source.get('page') is not None else ''
        criteria = ''.join(lesson_body_html(item) for item in source.get('criteria', []))
        items.append('<li><a href="' + html.escape(source['url'], quote=True)
                     + '" target="_blank" rel="noopener noreferrer">' + html.escape(source['title'])
                     + '</a><br>' + html.escape(source['locator'] + page)
                     + '<br>' + html.escape(source['edition_note'])
                     + ('<div class="source-criteria">' + criteria + '</div>' if criteria else '') + '</li>')
    return ('<div class="lesson-source-review" data-source-review-status="reviewed_requirements_source">'
            + '<b>Nguồn đã đối chiếu yêu cầu bài học</b>'
            + '<p>Ngày đối chiếu: ' + html.escape(review['reviewed_on']) + '. '
            + html.escape(review['scope']) + '</p><ul>' + ''.join(items) + '</ul></div>')


def apply_reviewed_content_corrections(text, subject, grade, topic):
    """Apply explicit source-backed corrections only to an exact reviewed topic.

    This is not a general rewrite or a curriculum acceptance filter. Old approved
    reviews without correction records remain unchanged, as do code examples.
    """
    review = reviewed_lesson_sources(subject, grade, topic)
    if review['status'] != 'reviewed_requirements_source':
        return text
    rules = review.get('content_corrections', [])
    def repair(value):
        for rule in rules:
            if (isinstance(rule, dict) and isinstance(rule.get('before'), str)
                    and rule['before'] and isinstance(rule.get('after'), str)
                    and rule['after'] and rule.get('reason')):
                if rule['after'] not in value:
                    value = value.replace(rule['before'], rule['after'])
        return value
    parts = re.split(r'(```[\s\S]*?```|~~~[\s\S]*?~~~|`[^`\n]*`|<(?:pre|svg|script|style)\b[^>]*>[\s\S]*?</(?:pre|svg|script|style)\s*>)', str(text), flags=re.I)
    return ''.join(part if i % 2 else repair(part) for i, part in enumerate(parts))


def apply_reviewed_quiz_proposal(question, subject, grade, topic):
    """Revise only an explicit exact-stem proposal, never certify its level."""
    from copy import deepcopy
    result = deepcopy(question)
    review = reviewed_lesson_sources(subject, grade, topic)
    if review['status'] != 'reviewed_requirements_source':
        return result
    stem = apply_reviewed_content_corrections(str(result.get('question', '')), subject, grade, topic)
    result['question'] = stem
    for key in ('explain', 'explanation', 'hint'):
        if isinstance(result.get(key), str):
            result[key] = apply_reviewed_content_corrections(result[key], subject, grade, topic)
    # Options may already be shuffled. Match the reviewed option text, preserving
    # its current letter/position and the existing answer key, never the old D.
    if isinstance(result.get('options'), list):
        options = list(result['options'])
        for rule in review.get('content_corrections', []):
            if not isinstance(rule, dict) or not rule.get('reason'):
                continue
            before = re.fullmatch(r'[A-D]\. ([^\n]+)', str(rule.get('before', '')))
            after = re.fullmatch(r'[A-D]\. ([^\n]+)', str(rule.get('after', '')))
            if not before or not after:
                continue
            for i, option in enumerate(options):
                match = re.fullmatch(r'([A-D]\. )([^\n]+)', option) if isinstance(option, str) else None
                if match and match[2] == before[1]:
                    options[i] = match[1] + after[1]
        result['options'] = options
    matches = [r for r in review.get('assessment_proposals', [])
               if r.get('level') in ('NB', 'TH', 'VD', 'VDC') and r.get('reason')
               and folded(r.get('question', '')) == folded(stem)]
    if len(matches) == 1:
        result.setdefault('level_claimed', result.get('level', ''))
        result['level'] = matches[0]['level']
        result['level_proposal_reason'] = matches[0]['reason']
    return result


def apply_reviewed_essay_labels(text, subject, grade, topic):
    """Apply only an explicit teacher decision for the exact reviewed stem."""
    review = reviewed_lesson_sources(subject, grade, topic)
    if review['status'] != 'reviewed_requirements_source':
        return text
    starts = list(re.finditer(r'(?mi)^[ \t]*(?:\*\*)?Câu[ \t]+\d+[.:]', text))
    value = text
    for index in range(len(starts) - 1, -1, -1):
        start = starts[index].start()
        end = starts[index + 1].start() if index + 1 < len(starts) else len(text)
        block = text[start:end]
        label = re.search(r'\[Mức độ:[^\]\n]*\]', block, re.I)
        if not label:
            continue
        stem = re.split(r'(?mi)^[ \t]*(?:[-*][ \t]+)?(?:\*\*)?(?:Bước[ \t]+1\b|Gợi ý thực hiện theo 4 bước\s*:)', block[label.end():], maxsplit=1)[0]
        matches = [row for row in review.get('assessment_decisions', [])
                   if folded(row.get('question', '')) == folded(stem)
                   and row.get('level') in ('NB', 'TH', 'VD', 'VDC') and row.get('reason')]
        if len(matches) == 1:
            replacement = '[Mức độ: ' + matches[0]['level'] + ']'
            value = value[:start + label.start()] + replacement + value[start + label.end():]
    return value


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
        return [{"title": f"Danh mục SGK NXBGDVN — chọn {subject}, lớp {grade}", "url": PUBLISHER_PORTAL, "kind": "portal"},
                {"title": f"Tra cứu SGK lớp {grade} — Trường Học Số Quốc Gia",
                 "url": f"{NATIONAL_SCHOOL_TEXTBOOK_LIBRARY}?lop={grade}", "kind": "portal"},
                {"title": "Thư viện SGK điện tử chính thức — NXBGD", "url": PUBLISHER_DIGITAL_LIBRARY + "books", "kind": "portal"}]
    result = []
    for book in books:
        book = dict(book)
        publisher_book_page = ("taphuan.nxbgd.vn" in book["url"]
                               and "/tap-huan/chi-tiet-sach/" in book["url"])
        unavailable = (book["url"] in {PUBLISHER_PORTAL, PUBLISHER_DIGITAL_LIBRARY}
                       or ("taphuan.nxbgd.vn" in book["url"] and not publisher_book_page)
                       or book["url"].endswith("bo-sach-ket-noi-tri-thuc-voi-cuoc-song-sgk-sinh-hoc-10/"))
        if unavailable:
            book.update(title="Tra cứu " + book["title"], url=PUBLISHER_PORTAL, kind="portal")
        elif publisher_book_page:
            book["kind"] = "publisher_book_page"
        else:
            book["kind"] = "reference_page"
        result.append(book)
    result.append({"title": f"Tra cứu SGK lớp {grade} — Trường Học Số Quốc Gia",
                   "url": f"{NATIONAL_SCHOOL_TEXTBOOK_LIBRARY}?lop={grade}", "kind": "portal"})
    result.append({"title": "Thư viện SGK điện tử chính thức — NXBGD",
                   "url": PUBLISHER_DIGITAL_LIBRARY + "books", "kind": "portal"})
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
    review = reviewed_lesson_sources(subject, grade, topic)
    review_html = lesson_source_review_html(subject, grade, topic)
    update_html = (f'<p>{html.escape(update["note"])} <a href="{html.escape(update["url"], quote=True)}" '
                   'target="_blank" rel="noopener noreferrer">Thông báo cập nhật của NXBGD</a></p>') if update else ''
    badge = (f'<div class="lesson-reference"><b>{html.escape(subject)} · Lớp {grade}</b> — {html.escape(topic)}'
             f'<p>Mã lưu nội bộ: {code}. Các liên kết dưới đây dùng tra cứu theo môn/lớp.</p>{review_html}{update_html}{links}'
             f'<p><a href="{html.escape(video, quote=True)}" target="_blank" rel="noopener noreferrer">Tìm video theo chủ đề</a>'
             ' — đây là kết quả tìm kiếm, không phải video đã được thẩm định.</p></div>')
    return {"index_code": code, "chapter_name": topic, "clean_topic": topic,
            "book_name": f"Tài liệu tham khảo {subject} lớp {grade}", "channel_info": channel,
            "yt_deep_url": video, "qr_img_data": qr_builder(video), "badge_html": badge,
            "reference_review": review}
