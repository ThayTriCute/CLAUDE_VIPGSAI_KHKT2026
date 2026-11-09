"""Trạm 1: giữ đúng môn/lớp cho minh họa mẫu và cho ngữ cảnh học sinh nhập.

Hình mẫu trong precision_visual_engine là sơ đồ khái quát cố định, không lấy dữ
kiện từ bài. Chỉ chèn khi đúng môn, đúng lớp theo CT GDPT 2018/KNTT và đúng nội
dung đặc thù; không bù hình bằng tọa độ tự đặt. Đây là kiểm soát phạm vi hiển
thị, không phải chứng nhận nội dung bài học đã được thẩm định.
"""
import re

from services.academic_context import academic_context, folded, subjects_for_grade

T1_CONTEXT_REVISION = 2026110920

GENERIC_NOTE = 'Hình minh họa khái quát, không lấy số liệu từ bài; đối chiếu SGK khi học.'

# key: (môn, các lớp có nội dung tương ứng trong CT2018/KNTT, mẫu nhận diện, chú thích)
# Phạm vi lớp: Khí lí tưởng, Từ trường (lực từ, quy tắc bàn tay trái), Vật lí hạt nhân
# thuộc Vật lí 12; điều chế/thu ethylene thuộc Hóa học 11; pin Daniell thuộc Hóa học 12;
# phả hệ thuộc Sinh học 12 (Di truyền học người); chuỗi/lưới thức ăn thuộc KHTN 8
# (Hệ sinh thái) và Sinh học 12 (Sinh thái học).
_ILLUSTRATIONS = (
    ('pv', {'Vật lý': {12}},
     r'đẳng\s*(?:áp|tích|nhiệt)|khí\s+l[íý]\s+tưởng|đồ\s+thị\s+p\s*[-–]\s*v\b',
     '🔬 Sơ đồ khái quát các quá trình biến đổi trạng thái khí trên hệ p–V'),
    ('magnetic', {'Vật lý': {12}},
     r'lực\s+từ|bàn\s+tay\s+trái|cảm\s+ứng\s+từ',
     '🧲 Quy tắc bàn tay trái và chiều lực từ'),
    ('nuclear', {'Vật lý': {12}},
     r'phóng\s+xạ|chu\s+k[ìỳ]\s+bán\s+rã',
     '⚛️ Đồ thị khái quát định luật phóng xạ N(t)'),
    ('daniell', {'Hóa học': {12}}, r'daniell',
     '🔋 Sơ đồ pin điện hóa Zn–Cu (pin Daniell)'),
    ('pedigree', {'Sinh học': {12}}, r'phả\s+hệ',
     '🧬 Sơ đồ phả hệ khái quát (kí hiệu nam/nữ, bình thường/bị bệnh)'),
    ('food_web', {'Sinh học': {12}, 'Khoa học tự nhiên': {8}},
     r'lưới\s+thức\s+ăn|chuỗi\s+thức\s+ăn',
     '🌿 Sơ đồ khái quát lưới thức ăn trong quần xã'),
)
# Cùng mẫu với precision_visual_engine.parse_oxyz_tetrahedron_points để hình khớp dữ kiện.
_POINT = r'([A-Z])\s*\(\s*(-?\d+(?:\.\d+)?)\s*[;,]\s*(-?\d+(?:\.\d+)?)\s*[;,]\s*(-?\d+(?:\.\d+)?)\s*\)'


def lesson_illustrations(text, subject, grade):
    """Return ordered illustration keys allowed for this exact subject/grade/content.

    Oxyz figures need explicit coordinates written in the lesson; generic
    keywords alone never produce a figure with invented points.
    """
    try:
        subject, grade = academic_context(subject, grade)
    except ValueError:
        return []
    value = str(text or '')
    lower = value.lower()
    keys = [key for key, scope, pattern, _ in _ILLUSTRATIONS
            if grade in scope.get(subject, ()) and re.search(pattern, lower)]
    if (subject == 'Hóa học' and grade == 11
            and re.search(r'c\s*_?\{?2\}?\s*h\s*_?\{?4\}?|\b(?:ethylene|ethene|etilen)\b', lower)
            and 'đẩy nước' in lower and any(k in lower for k in ('đun nóng', 'đèn cồn'))):
        keys.insert(0, 'gas_c2h4')
    if subject == 'Toán học' and grade == 12:
        points = {}
        for name, *xyz in re.findall(_POINT, value):
            points[name] = tuple(float(v) for v in xyz)  # engine giữ điểm cuối cùng cùng tên
        flight = re.search(r'đường\s+bay|thiết\s+bị\s+bay|trạm\s+phát\s+sóng', lower)
        if flight and {'M', 'N'} <= set(points):
            keys.append('oxyz_flight')
        elif not flight and _axial_tetrahedron(points) and re.search(
                r'oxyz|tọa\s+độ\s+không\s+gian|hệ\s+trục|mặt\s+cầu|tứ\s+diện', lower):
            keys.append('oxyz_tetra')
    return keys


def _axial_tetrahedron(points):
    """The engine draws only O.ABC with A∈Ox, B∈Oy, C∈Oz; refuse other solids."""
    try:
        a, b, c = points['A'], points['B'], points['C']
    except KeyError:
        return False
    if points.get('O', (0.0, 0.0, 0.0)) != (0.0, 0.0, 0.0):
        return False
    return (a[1] == a[2] == 0 and b[0] == b[2] == 0 and c[0] == c[1] == 0
            and a[0] != 0 and b[1] != 0 and c[2] != 0)


def illustration_caption(key):
    if key in ('oxyz_tetra', 'oxyz_flight'):
        return '📐 Hình không gian Oxyz dựng từ tọa độ trong bài'
    if key == 'gas_c2h4':
        return '🧪 Sơ đồ khái quát điều chế và thu khí ethylene bằng phương pháp đẩy nước'
    return next(caption for k, _, _, caption in _ILLUSTRATIONS if k == key)


def illustration_note(key):
    return 'Tọa độ lấy đúng từ đề bài; kiểm tra lại khi chép hình.' if key.startswith('oxyz') else GENERIC_NOTE


# --- Ngữ cảnh học sinh nhập: lớp/môn được nêu rõ trong tên bài -------------------
_BOOK_ALIASES = (
    ('lich su va dia li', 'Lịch sử & Địa lý'), ('lich su va dia ly', 'Lịch sử & Địa lý'),
    ('lich su dia li', 'Lịch sử & Địa lý'), ('lich su dia ly', 'Lịch sử & Địa lý'),
    ('giao duc kinh te va phap luat', 'Giáo dục kinh tế và pháp luật'),
    ('gdkt pl', 'Giáo dục kinh tế và pháp luật'), ('gdktpl', 'Giáo dục kinh tế và pháp luật'),
    ('ktpl', 'Giáo dục kinh tế và pháp luật'),
    ('giao duc cong dan', 'Giáo dục công dân'), ('gdcd', 'Giáo dục công dân'),
    ('khoa hoc tu nhien', 'Khoa học tự nhiên'), ('khtn', 'Khoa học tự nhiên'),
    ('toan hoc', 'Toán học'), ('toan', 'Toán học'),
    ('vat li', 'Vật lý'), ('vat ly', 'Vật lý'),
    ('hoa hoc', 'Hóa học'), ('hoa', 'Hóa học'),
    ('sinh hoc', 'Sinh học'), ('sinh', 'Sinh học'),
    ('ngu van', 'Ngữ văn'), ('tieng anh', 'Tiếng Anh'),
    ('lich su', 'Lịch sử'), ('dia li', 'Địa lý'), ('dia ly', 'Địa lý'),
    ('tin hoc', 'Tin học'), ('cong nghe', 'Công nghệ'),
)
_ALIAS_RE = '|'.join(re.escape(a) for a, _ in _BOOK_ALIASES)
_NOT_GRADE = r'(?!\s*(?:diem|d|cau|phut|tuoi|gio|ngay|thang|trang|tiet)\b)'
_BOOK_RE = re.compile(r'(?<![a-z0-9])(' + _ALIAS_RE + r')\s+(\d{1,2})(?![0-9])' + _NOT_GRADE)
_GRADE_RE = re.compile(r'(?<![a-z0-9])(?:lop|khoi)\s*(\d{1,2})(?![0-9])')


def _band_subject(subject, grade):
    """Map a named book to the subject offered at that grade (CT2018 cấp học)."""
    if grade <= 9:
        subject = {'Lịch sử': 'Lịch sử & Địa lý', 'Địa lý': 'Lịch sử & Địa lý',
                   'Vật lý': 'Khoa học tự nhiên', 'Hóa học': 'Khoa học tự nhiên',
                   'Sinh học': 'Khoa học tự nhiên',
                   'Giáo dục kinh tế và pháp luật': 'Giáo dục công dân'}.get(subject, subject)
    else:
        subject = {'Giáo dục công dân': 'Giáo dục kinh tế và pháp luật'}.get(subject, subject)
    return subject if subject in subjects_for_grade(grade) else None


def topic_context_mentions(topic):
    """Ordered (subject or None, grade) explicitly written in a lesson request."""
    text = folded(topic)
    found = []
    for match in _GRADE_RE.finditer(text):
        grade = int(match[1])
        if 6 <= grade <= 12:
            found.append((match.start(), None, grade))
    names = dict(_BOOK_ALIASES)
    for match in _BOOK_RE.finditer(text):
        grade = int(match[2])
        if not 6 <= grade <= 12:
            continue
        if match[1] == 'sinh' and text[:match.start()].endswith('hoc '):
            continue  # "học sinh 12 tuổi" không phải sách Sinh học 12
        named = _band_subject(names[match[1]], grade)
        if named:  # tên sách không có ở cấp học đó (vd. "KHTN 11") thì không suy lớp
            found.append((match.start(), named, grade))
    return [(subject, grade) for _, subject, grade in sorted(found, key=lambda row: row[0])]


def topic_context_conflict(topic, subject, grade):
    """Grade conflict blocks generation; another named book is only a notice.

    "lớp N"/"khối N" or the selected subject's own book ("Toán 12") decide the
    grade. A different subject's book ("Vật lí 12" in a Toán lesson) may be an
    interdisciplinary link, so it never changes or blocks the selected grade.
    """
    subject, grade = academic_context(subject, grade)
    mentions = topic_context_mentions(topic)
    own = [g for s, g in mentions if s is None or s == subject]
    other = [(s, g) for s, g in mentions if s is not None and s != subject]
    conflict_grade = own[0] if own and grade not in own else None
    other_book = other[0] if other and not any(s == subject for s, _ in mentions) else None
    return {'grade': conflict_grade, 'other_book': other_book}


# --- Ba phần bài học do AI sinh: không cắt nhầm ở dòng "Phần 2 (khổ 2–3)" -------
_PART_RE = re.compile(r'(?im)^[ \t]*(?:#{1,6}[ \t]*)?(?:\*\*|__)?[ \t]*PHẦN[ \t]*([23])(?!\d)[^\n]*$')
_PART_TITLES = {2: re.compile(r'trắc\s*nghiệm', re.I), 3: re.compile(r'tự\s*luận|bài\s*tập', re.I)}


def _part_rank(match, part):
    """0: tiêu đề đúng tên phần; 1: tiêu đề Markdown/in đậm/IN HOA; 2: dòng thường."""
    line = match.group(0).strip()
    if _PART_TITLES[part].search(line):
        return 0
    if line.startswith(('#', '**', '__')) or line.startswith('PHẦN'):
        return 1
    return 2


def lesson_part_spans(text):
    """Vị trí tiêu đề PHẦN 2/PHẦN 3 của bài Trạm 1: {n: (đầu dòng tiêu đề, đầu nội dung)}.

    Bài Ngữ văn/Lịch sử thường có dòng bố cục "Phần 2 (khổ 2–3): ..." trong Phần 1;
    dòng đó không phải tiêu đề phần luyện tập nên không được cắt bài hoặc làm mất
    câu hỏi. Ưu tiên tiêu đề có tên phần, rồi tiêu đề định dạng, cuối cùng mới tới
    dòng thường (giữ hành vi cũ khi bài không có tiêu đề rõ hơn).
    """
    value = str(text or '')
    found = {2: [], 3: []}
    for match in _PART_RE.finditer(value):
        found[int(match[1])].append(match)
    spans = {}
    for part in (2, 3):
        after = spans.get(2, (0, 0))[1]
        candidates = [m for m in found[part] if m.start() >= after]
        if candidates:
            best = min(candidates, key=lambda m: (_part_rank(m, part), m.start()))
            spans[part] = (best.start(), best.end())
    return spans


def lesson_parts(text):
    """(Phần 1, Phần 2, Phần 3) theo lesson_part_spans; phần thiếu là chuỗi rỗng."""
    value = str(text or '')
    spans = lesson_part_spans(value)
    p2, p3 = spans.get(2), spans.get(3)
    first = min([s[0] for s in (p2, p3) if s] or [len(value)])
    part1 = value[:first]
    part2 = value[p2[1]:(p3[0] if p3 else len(value))] if p2 else ''
    part3 = value[p3[1]:] if p3 else ''
    return part1, part2, part3
