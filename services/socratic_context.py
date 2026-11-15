"""Subject-aware fallback questions, without certifying generated hint content."""
import re

from services.academic_context import canonical_subject, folded

T1_CONTEXT_REVISION = 2026111603


def complete_verified_quote_reference(reply, references):
    """Complete supplied provenance only for a full matching quote and author.

    No invented quotation or attribution, and no AI retry for missing formatting.
    Code examples do not count as a quotation in the teaching prose.
    """
    from services.philosophy_rotation import GUIDANCE
    marker = GUIDANCE.splitlines()[0]
    parts = re.split(r'(```[\s\S]*?```|~~~[\s\S]*?~~~|`[^`\n]*`)', str(reply or ''))
    text = ''.join(part if i % 2 else re.sub(
        r'(?m)^[ \t]*(?:#+[ \t]*)?(?:\*\*)?' + re.escape(marker) + r'(?:\*\*)?[ \t]*(?:\n|$)', '', part)
        for i, part in enumerate(parts))
    prose = re.sub(r'```[\s\S]*?```|~~~[\s\S]*?~~~|`[^`\n]*`', '', text)
    normalized = folded(prose)
    for reference in references:
        quote, author = reference.get('quote', ''), reference.get('author', '')
        url, locator = reference.get('source_url', ''), reference.get('source_locator', '')
        if (reference.get('source_verified') is True and quote and author and locator
                and url.startswith('https://') and folded(quote) in normalized
                and folded(author) in normalized):
            # A whole-book URL alone is not the supplied quote's location.
            # References inside code are examples, not teaching provenance.
            if url not in prose or folded(locator) not in normalized:
                text += '\n\nNguồn đối chiếu: [' + str(author) + ' — ' + str(locator) + '](' + url + ').'
            note = reference.get('translation_note', '')
            if note and note not in text:
                text += '\n\n' + note
    return text


def label_verified_quote_translation(reply, references):
    """Attach supplied provenance only when quote, author and URL all match."""
    text = str(reply or '')
    normalized = folded(text)
    for reference in references:
        quote = reference.get('quote', '')
        author = reference.get('author', '')
        url = reference.get('source_url', '')
        note = reference.get('translation_note', '')
        if (reference.get('source_verified') is True and quote and author and url and note
                and folded(quote) in normalized and folded(author) in normalized and url in text
                and note not in text):
            text += '\n\n' + note
    return text


def repair_reviewed_station1_closing(reply, student_message, subject, grade, closing=False):
    """Fix a reproduced contradictory recap; preserve the full moral lesson."""
    text = str(reply or '')
    if not closing:
        return text
    student = re.sub(r'[\s${}\\]', '', str(student_message))
    first = re.split(r'\n\s*\n', text, maxsplit=1)[0]
    if (subject == 'Toán học' and int(grade) == 12
            and '3x^2' in student and 'khong doi dau' in folded(student_message)
            and 'phan tich su doi dau' in folded(first)):
        text = text.replace(first,
            'Thầy ghi nhận em đã tự kiểm tra dấu đạo hàm ở hai phía điểm xét và trình bày lập luận của mình. '
            'Việc đối chiếu kết quả thay vì chỉ nhớ công thức là thói quen học tập đáng khuyến khích.', 1)
    # This precise English quotation was checked against MIT Book VI. Label
    # the accompanying Vietnamese gloss, without inventing another citation.
    if ('Marcus Aurelius' in text and 'meditations.6.six.html' in text
            and 'I seek the truth by which no man was ever injured' in text):
        text = text.replace('(Tôi tìm kiếm sự thật, điều chưa từng làm hại ai',
                            '(Diễn nghĩa tiếng Việt từ bản dịch tiếng Anh của George Long: Tôi tìm kiếm sự thật, điều chưa từng làm hại ai')
    if 'Marcus Aurelius' in text and 'Meditations' in text and 'George Long' in text:
        text = text.replace('theo bản dịch của George Long',
                            'diễn nghĩa tiếng Việt từ bản dịch tiếng Anh của George Long')
        if 'meditations.6.six.html' not in text:
            text = text.replace('tham khảo tại classics.mit.edu',
                'nguồn: [Internet Classics Archive — Book VI](https://classics.mit.edu/Antoninus/meditations.6.six.html)')
    return text


def is_post_closure_thanks(message, closed=False, history=None):
    """Only a social acknowledgement after a successful lesson closing."""
    # Recover only from a clearly completed moral closing in this chat,
    # never from a welcome message or the student's thanks alone.
    recorded_closing = any(
        item.get('role') == 'assistant'
        and 'thay chuc' in folded(item.get('content', ''))
        and 'tram 2' in folded(item.get('content', ''))
        and any(marker in folded(item.get('content', ''))
                for marker in ('internet classics archive', 'classics.mit.edu'))
        for item in (history or []) if isinstance(item, dict))
    if not closed and not recorded_closing:
        return False
    value = folded(str(message or ''))
    words = re.findall(r'[a-z]+', value)
    allowed = set('da vang em con cam on thay co rat nhieu a nhe nha nhe lam xin chan thanh biet tri an thank you thanks teacher so much'.split())
    gratitude = 'cam on' in ' '.join(words) or 'thank' in words or 'thanks' in words
    return gratitude and bool(words) and set(words) <= allowed


def _names_unique_chemical_answer(hint, options, correct_answer, question):
    """Block a named element cue unique to the correct formula, not given data."""
    letter = str(correct_answer).strip().upper()
    if not options or letter not in ('A', 'B', 'C', 'D') or len(options) != 4:
        return False
    index = ord(letter)-ord('A')
    aliases = {'Na': ('natri', 'sodium'), 'K': ('kali', 'potassium'),
               'Ca': ('canxi', 'calcium', 'nước vôi'), 'Ba': ('bari', 'barium'),
               'Al': ('nhôm', 'aluminium', 'aluminum'), 'Mg': ('magnesium', 'magie', 'magiê'),
               'Cu': ('kim loại đồng', 'copper'), 'Fe': ('kim loại sắt', 'iron')}
    def contains_symbol(text, symbol):
        return bool(re.search(r'(?<![A-Za-z])'+symbol+r'(?=$|[A-Z0-9(){}^+\-\s$])', str(text)))
    h, q = folded(hint), folded(question)
    for symbol, names in aliases.items():
        if (not contains_symbol(options[index], symbol) or contains_symbol(question, symbol)
                or any(contains_symbol(o, symbol) for i,o in enumerate(options) if i != index)):
            continue
        for name in names:
            cue = r'\b'+re.escape(folded(name))+r'\b'
            if re.search(cue, h) and not re.search(cue, q):
                return True
    return False


def math_context_question(question):
    """Small context-specific fallback library; no calculation or answer content."""
    text = folded(question)
    if 'truc tung' in text and any(term in text for term in ('cat truc tung', 'giao diem', 'tung do')):
        return ('Một điểm nằm trên trục tung thì hoành độ có đặc điểm gì? '
                'Từ đó, em sẽ dùng hàm số đã cho để xác định tung độ như thế nào?')
    has_parameter = 'tham so' in text
    monotonic = any(term in text for term in ('dong bien', 'nghich bien'))
    real_text = folded(re.sub(r'\\(?:mathbb|mathbf|mathrm)\s*(?:\{[Rr]\}|[Rr])|ℝ', 'R', str(question)))
    real_line = bool(re.search(r'\btren\s+(?:tap\s+)?r\b', real_text)) or 'tren toan bo truc so' in text
    if has_parameter and monotonic and real_line:
        tail = (' Khi đã tìm được miền tham số, em sẽ lọc và đếm các giá trị nguyên như thế nào?'
                if 'nguyen' in text else ' Em sẽ suy ra điều kiện của tham số như thế nào?')
        return ('Em sẽ tính đạo hàm chứa tham số và đặt điều kiện về dấu nào để tính đơn điệu '
                'đúng với mọi giá trị của biến trên toàn bộ trục số?' + tail)
    if any(term in text for term in ('tap xac dinh', 'txd')) or ('sqrt' in text and 'ham' in text):
        return ('Biểu thức trong căn (và mẫu, logarit nếu có) cần điều kiện gì để có nghĩa? '
                'Em sẽ giải điều kiện đó rồi viết tập nghiệm dưới dạng khoảng như thế nào?')
    if ('toa do dinh' in text or 'dinh' in text) and 'parabol' in text:
        return ('Hoành độ đỉnh parabol tính từ hệ số a và b như thế nào? '
                'Khi đã có hoành độ, em thay vào hàm số để tìm tung độ ra sao?')
    for kind in ('tieu', 'dai'):
        if 'toa do diem cuc ' + kind in text:
            label = 'cực tiểu' if kind == 'tieu' else 'cực đại'
            return (f'Em cần nhận ra sự đổi dấu nào của đạo hàm để tìm hoành độ điểm {label}? '
                    'Sau đó, em sẽ dùng hàm số ban đầu như thế nào để xác định đủ hai tọa độ?')
    return None


_QUESTIONS = {
    'Ngữ văn': 'Em cần tìm chi tiết, từ ngữ hoặc bằng chứng nào trong ngữ liệu để trả lời đúng yêu cầu?',
    'Tiếng Anh': 'Em nhận thấy dấu hiệu nào về nghĩa, cấu trúc câu hoặc ngữ cảnh trước khi đối chiếu các phương án?',
    'Lịch sử': 'Em cần xác định mốc thời gian, bối cảnh và bằng chứng lịch sử nào liên quan đến yêu cầu?',
    'Địa lý': 'Em cần đọc thông tin nào từ bản đồ, bảng số liệu hoặc ngữ liệu địa lí để đối chiếu yêu cầu?',
    'Lịch sử & Địa lý': 'Em cần xác định bối cảnh thời gian, không gian và bằng chứng nào trong ngữ liệu?',
    'Vật lý': 'Em cần nhận diện hiện tượng, các đại lượng và điều kiện áp dụng mối quan hệ vật lí nào?',
    'Hóa học': 'Em cần xác định chất, điều kiện hoặc bằng chứng phản ứng nào trước khi đối chiếu các phương án?',
    'Sinh học': 'Em cần xác định cấp độ tổ chức, quá trình hoặc bằng chứng sinh học nào trong câu hỏi?',
    'Khoa học tự nhiên': 'Em cần nhận diện hiện tượng, dữ kiện và mối quan hệ khoa học nào trong câu hỏi?',
    'Tin học': 'Em cần xác định đầu vào, đầu ra hoặc quy tắc hoạt động nào trong tình huống được nêu?',
    'Công nghệ': 'Em cần xác định chức năng, điều kiện sử dụng và tiêu chí nào của giải pháp công nghệ?',
    'Giáo dục công dân': 'Em cần đối chiếu hành vi, hoàn cảnh và nguyên tắc ứng xử nào trong tình huống?',
    'Giáo dục kinh tế và pháp luật': 'Em cần xác định chủ thể, quan hệ kinh tế hoặc quyền và nghĩa vụ nào trong tình huống?',
}


def guiding_question(hint, options=None, correct_answer='', question_text=''):
    """Prefer a separate guiding question; never substitute the EXPLAIN field.

    Explicit answer markers and verbatim alternatives are rejected here. This
    is a structural check, not proof that every paraphrase is non-revealing.
    Rejection changes only the hint, never blocks the lesson or calls AI again.
    """
    value = str(hint or '').strip()
    marked_answer = re.search(
        r'(?i)(?:\b(?:chọn|đáp án|đáp số|answer|choose|option)\s*(?:đúng\s*)?(?:là|is|:)?\s*[A-D]\b'
        r'|\b[A-D]\s*(?:là\s*)?(?:đúng|correct)\b)', value)
    alternatives = [re.sub(r'^[A-D][.):]\s*', '', str(o), flags=re.I).strip().casefold()
                    for o in options or []]
    answer = str(correct_answer or '').strip().casefold()
    if len(answer) > 3:
        alternatives.append(answer)
    repeats_answer = any(len(o) > 3 and o in value.casefold() for o in alternatives)
    # A standalone numeric equality can disclose a result. Preserve equations
    # already supplied by the question, and coefficients in symbolic formulas.
    numeric_equality = re.compile(r"\b(?:[a-zA-Z]|[fgh]\s*\(\s*x\s*\))\s*=\s*[+-]?\d+(?:[.,]\d+)?(?:\s*/\s*\d+)?(?![\d.,/])(?=\s*(?:[$,;?)}]|(?:có|co|đúng|dung)\b|$))")
    normalize = lambda text: re.sub(r'[\s${}\\]', '', str(text)).casefold()
    source = normalize(question_text)
    new_result = any(normalize(match[0]) not in source for match in numeric_equality.finditer(value))
    if value and len(value) <= 800 and value.endswith('?') and not marked_answer and not repeats_answer and not new_result:
        return value
    return None


def english_reading_question(question):
    """Guide evidence selection from the final reading task, never quote its answer."""
    text = str(question or '')
    if not re.search(r'(?i)\b(?:read\b.{0,50}\b(?:passage|text)|according to (?:the )?(?:passage|text))\b', text):
        return None
    tasks = re.findall(r'(?i)\b(what|where|when|who|why|how)\b[^?]{0,300}\?', text)
    if not tasks:
        return None
    kind = tasks[-1].lower()
    targets = {'what': 'hoạt động, sự việc hoặc thông tin được hỏi',
               'where': 'địa điểm được hỏi', 'when': 'thời điểm được hỏi',
               'who': 'nhân vật được hỏi', 'why': 'nguyên nhân được hỏi',
               'how': 'cách thức hoặc mức độ được hỏi'}
    return (f'Câu hỏi cuối đoạn đọc yêu cầu em xác định {targets[kind]}. '
            'Em sẽ tìm chi tiết nào trong đoạn và kiểm tra đúng chủ thể, hoàn cảnh '
            'trước khi đối chiếu các phương án?')


def computing_context_question(question):
    """Small task-specific prompts; no numerical result or answer alternative."""
    text = folded(question)
    if ('html' in text and 'noi dung' in text and ('hien thi' in text or 'nhin thay' in text)
            and ('trinh duyet' in text or 'trang' in text)):
        return ('Em sẽ phân biệt phần thông tin về tài liệu với phần nội dung người đọc nhìn thấy '
                'theo tiêu chí nào, rồi đối chiếu vai trò của từng phương án ra sao?')
    if 'danh sach' in text and any(term in text for term in ('thu tu', 'danh so')):
        return ('Danh sách trong yêu cầu cần thể hiện mối quan hệ nào giữa các mục? '
                'Em sẽ phân biệt phần tử bao ngoài với từng mục và đối chiếu vai trò của các thẻ ra sao?')
    if 'cpu' in text:
        return ('Em sẽ phân biệt vai trò của CPU với bộ nhớ và thiết bị vào, ra '
                'theo tiêu chí nào trước khi đối chiếu từng phát biểu?')
    if 'dung luong' in text and any(term in text for term in ('the nho', 'tep', 'buc anh')):
        if re.search(r'bao nhieu\s+(?:the nho|thiet bi|o dia)', text):
            return ('Tổng dung lượng cần lưu và dung lượng mỗi thiết bị đã cùng đơn vị chưa? '
                    'Đề đã nêu điều kiện chia tệp giữa các thiết bị chưa? '
                    'Em sẽ xác định số thiết bị cần dùng và xử lý phần dư như thế nào?')
        return ('Dung lượng lưu trữ và dung lượng mỗi tệp đã cùng đơn vị chưa? '
                'Em sẽ dùng quan hệ nào để tìm số tệp chứa được và xử lý phần dư?')
    if 'thiet bi so' in text and any(term in text for term in ('ket noi', 'cong')):
        return ('Với từng nhận định, em có thể đối chiếu thiết bị và cổng kết nối thực tế nào? '
                'Các từ khẳng định tuyệt đối có đúng trong mọi trường hợp không?')
    return None


def subject_socratic_hint(hint, subject, options=None, correct_answer='', question_text=''):
    subject = canonical_subject(subject)
    if subject in ('Hóa học', 'Khoa học tự nhiên') and _names_unique_chemical_answer(hint, options, correct_answer, question_text):
        if any(term in folded(question_text) for term in ('base tan', 'kiem', 'tinh tan')):
            return 'Em sẽ dùng tiêu chí nào và tra bảng tính tan ra sao để tự phân biệt từng chất trong các phương án?'
        return _QUESTIONS[subject]
    question = guiding_question(hint, options, correct_answer, question_text)
    if subject == 'Tin học':
        contextual = computing_context_question(question_text)
        # Live CPU hint repeated the identifying metaphor from the correct option.
        # Replace only that observed cue, not every valid supplied computing hint.
        cpu_metaphor = 'cpu' in folded(question_text) and 'bo nao' in folded(hint)
        key = str(correct_answer).strip().upper()
        html_name_cue = (
            'danh sach' in folded(question_text) and options and len(options) == 4
            and key in ('A', 'B', 'C', 'D')
            and re.search(r'<\s*ol\b', str(options[ord(key) - ord('A')]), re.I)
            and re.search(r'\border(?:ed)?\b', folded(hint))
            and not re.search(r'\border(?:ed)?\b|\bol\b', folded(question_text))
        )
        generic_computing_hint = folded(hint) == folded(_QUESTIONS.get(subject, ''))
        if contextual and (not question or cpu_metaphor or html_name_cue or generic_computing_hint):
            return contextual
    if question:
        return question
    if subject == 'Tiếng Anh':
        contextual = english_reading_question(question_text)
        if contextual:
            return contextual
    return _QUESTIONS.get(subject, 'Em cần xác định dữ kiện và yêu cầu nào trước khi tự đối chiếu các phương án?')


_SOLUTION_LEAK = re.compile(
    r'(?i)(?:\bđáp\s*án\b|\bđáp\s*số\b|\bvậy\s*chọn\b|\bchọn\s*phương\s*án\b|'
    r'\blời\s*giải\b|\bgiải\s*:|\bkết\s*luận\s*:|\bdo\s*đó\s*[A-D]\b|'
    r'\bsuy\s*ra\s*[A-D]\b|\bphương\s*án\s*[A-D]\s*(?:đúng|là)|\b[A-D]\s*là\s*đáp)'
)

_GENERIC_HINTS = {
    folded('Áp dụng trực tiếp định nghĩa và tính chất cốt lõi trong SGK Kết Nối Tri Thức. Phân tích loại trừ các phương án nhiễu theo suy luận logic.'),
    folded('Bám sát thể loại, ngữ cảnh tác phẩm và các phương thức biểu đạt trong SGK Kết Nối Tri Thức để phân tích.'),
    folded('Xác định rõ vấn đề nghị luận, các luận điểm chính, dẫn chứng xác thực và rút ra bài học sâu sắc.'),
}


def looks_like_explain_solution(text) -> bool:
    """True khi chuỗi giống lời giải/explain — không được dùng làm HD Socratic."""
    value = str(text or '').strip()
    if not value:
        return False
    if _SOLUTION_LEAK.search(value):
        return True
    if len(value) > 700 and value.count('=') >= 3:
        return True
    if re.search(r'(?i)\b(?:vậy|do đó|suy ra)\b.{0,40}\b(?:đúng|sai|chọn)\b', value):
        return True
    return False


def _question_given_facts(question) -> list:
    """Trích dữ kiện đề cho (số liệu/hệ số/bảng) — không tính kết quả."""
    facts = []
    stem = str((question or {}).get('q') or '')
    # Số và phân số xuất hiện trong đề (giữ tối đa 8 để gọn).
    nums = re.findall(r'-?\d+(?:[.,]\d+)?(?:\s*/\s*\d+)?', stem)
    uniq = []
    for n in nums:
        if n not in uniq:
            uniq.append(n)
        if len(uniq) >= 8:
            break
    if uniq:
        facts.append('Các số liệu xuất hiện trong đề: ' + ', '.join(f'`{n}`' for n in uniq) + '.')

    f = (question or {}).get('f')
    if isinstance(f, dict) and f.get('type'):
        coeffs = []
        for key in ('a', 'b', 'c', 'd', 'e'):
            if key in f and f[key] is not None:
                coeffs.append(f'{key}={f[key]}')
        kind = str(f.get('type'))
        label = {
            'func_1_1': 'phân thức bậc 1/1',
            'func_2_1': 'phân thức bậc 2/1',
            'func_3': 'hàm bậc ba',
            'cubic': 'hàm bậc ba',
            'parabola': 'parabol',
            'func_2': 'bậc hai',
        }.get(kind, kind)
        if coeffs:
            facts.append(f'Ngữ liệu gắn dạng **{label}** với hệ số ({", ".join(coeffs)}) — em dùng để đối chiếu tiệm cận/giao điểm, không phải đáp án.')
        else:
            facts.append(f'Ngữ liệu gắn dạng **{label}** — đối chiếu đặc trưng đồ thị với phương án.')

    mslgn = (question or {}).get('mslgn_data')
    if isinstance(mslgn, dict):
        groups, freq = mslgn.get('groups') or [], mslgn.get('freq') or []
        if groups and freq and len(groups) == len(freq):
            pairs = [f'{g} (tần số {fr})' for g, fr in zip(groups[:6], freq[:6])]
            facts.append('Bảng ghép nhóm đề cho: ' + '; '.join(pairs) + '.')

    stmts = (question or {}).get('stmts') or []
    if isinstance(stmts, list) and stmts:
        facts.append(f'Phần Đúng/Sai có **{len(stmts)}** mệnh đề — xét độc lập từng ý, không suy từ ý này sang ý kia.')

    bbt = str((question or {}).get('bbt') or '').strip()
    if bbt and bbt.lower() not in {'null', 'none', '{}'}:
        facts.append('Đề kèm bảng biến thiên — đọc dòng $x$, dấu $y\'$ và mũi tên $y$ trước khi kết luận.')

    if any(k in stem.lower() for k in ('đồ thị', 'đường cong', 'hình vẽ', 'hình bên')):
        facts.append('Đề có hình/đồ thị — ưu tiên đọc tiệm cận, giao trục, chiều nhánh; đối chiếu từng phương án.')

    return facts


def _matched_anchor(subject, question_text) -> dict:
    """Neo SGK khớp stem: ưu tiên cụm từ dài hơn (vd 'nóng chảy' > 'nhiệt độ')."""
    try:
        from data.socratic_anchors import SOCRATIC_KNOWLEDGE_ANCHORS
    except Exception:
        return {}
    subj = canonical_subject(subject or 'Toán học')
    text = folded(question_text)
    best, best_score = None, 0
    for item in SOCRATIC_KNOWLEDGE_ANCHORS.get(subj, []) or []:
        score = 0
        for kw in item.get('keywords') or []:
            fk = folded(kw)
            if fk and fk in text:
                score += max(1, len(fk.split()))
        if score > best_score:
            best_score, best = score, item
    if not best or best_score <= 0:
        return {}
    return {
        'concept': str(best.get('concept') or ''),
        'formula': str(best.get('formula') or ''),
        'prompt': str(best.get('prompt') or ''),
        'score': best_score,
    }


def _matched_anchor_formula(subject, question_text) -> tuple:
    hit = _matched_anchor(subject, question_text)
    return hit.get('concept', ''), hit.get('formula', '')


def _short_stem_quote(stem: str, max_len: int = 72) -> str:
    """Trích khúc ngữ liệu ngắn để HD bám câu hỏi — không lấy phương án."""
    raw = re.sub(r'\s+', ' ', str(stem or '')).strip()
    raw = re.sub(r'\$[^$]{0,80}\$', lambda m: m.group(0), raw)
    if len(raw) <= max_len:
        return raw or 'ngữ liệu câu hỏi'
    cut = raw[:max_len]
    if ' ' in cut:
        cut = cut.rsplit(' ', 1)[0]
    return cut.rstrip(' ,;:') + '…'


def _formula_lines_for_stem(formula: str, stem: str) -> str:
    """Chọn dòng công thức neo khớp hiện tượng trong stem; không chọn hộ phương án."""
    lines = [ln.strip(' -•\t') for ln in str(formula or '').splitlines() if ln.strip()]
    if not lines:
        return ''
    text = folded(stem)
    scored = []
    for ln in lines:
        fl = folded(ln)
        score = sum(1 for mark in (
            'nong chay', 'hoa hoi', 'delta', 'dong dien', 'clapeyron', 'dao dong',
            'song', 'ester', 'glucose', 'doc hieu', 'nghi luan',
        ) if mark in fl and (mark in text or mark in ('delta', 'clapeyron', 'dong dien')))
        # Boost if stem phenomenon words appear in this line
        for mark in ('nong chay', 'hoa hoi', 'lam nong', 'nhiet luong', 'delta t', 'uit'):
            if mark in text and mark.replace(' ', '') in fl.replace(' ', ''):
                score += 2
        scored.append((score, ln))
    scored.sort(key=lambda p: (-p[0], -len(p[1])))
    top = [ln for sc, ln in scored if sc > 0][:2]
    if not top:
        top = lines[:2]
    return ' '.join(top)


def _is_negation_stem(stem: str) -> bool:
    text = folded(stem)
    return any(k in text for k in (
        'khong dung', 'khong phai', 'sai khi', 'sai ve', 'ngoai tru',
        'except', 'which is not', 'not true', 'not correct', 'incorrect',
    ))


def _topic_phrase(stem: str) -> str:
    """Lấy cụm chủ đề trong stem (sau 'về/khi nói về/của/trong') — không lấy cả câu hỏi."""
    raw = re.sub(r'\s+', ' ', str(stem or '')).strip()
    patterns = (
        r'(?:khi nói về|khi nói tới|về mặt|thuộc về)\s+([^?？\.…]{6,90})',
        r'(?:mô hình|định luật|quy tắc|khái niệm|phản ứng|hiện tượng)\s+([^?？\.…]{6,80})',
        r'(?:^|[.?!]\s*)(?:về)\s+([^?？\.…]{6,90})',
    )
    for pat in patterns:
        m = re.search(pat, raw, re.I)
        if m:
            phrase = re.sub(r'\s+', ' ', m.group(1)).strip(' :;,.')
            # Giữ tiền tố mô hình/định luật nếu stem có
            head = m.group(0)[: m.start(1) - m.start(0)].strip().lower()
            if any(h in head for h in ('mô hình', 'định luật', 'quy tắc', 'khái niệm', 'phản ứng', 'hiện tượng')):
                phrase = re.sub(r'\s+', ' ', m.group(0)).strip(' :;,.')
            if len(phrase) >= 6:
                return phrase[:100]
    # Fallback: bỏ khung "Phát biểu nào/Ý nào"
    cleaned = re.sub(
        r'^(?:phát biểu|ý|câu|đặc điểm|khẳng định)\s+nào\s+(?:sau đây\s+)?'
        r'(?:không\s+đúng|đúng|sai)?\s*(?:khi\s+nói\s+về\s+|về\s+)?',
        '', raw, flags=re.I,
    ).strip(' ?？')
    return (cleaned[:90] + ('…' if len(cleaned) > 90 else '')) or _short_stem_quote(stem, 60)


def _option_theme_hit(plain: str, keys) -> bool:
    """Khớp trụ phương án; bỏ khóa folded rỗng/1 ký tự (λ→'', Δt→'t')."""
    fl = folded(plain)
    for k in keys:
        raw = str(k)
        if raw in plain:  # ký hiệu/Unicode còn nguyên (λ, Δt, …)
            return True
        fk = folded(raw)
        if len(fk) < 2:
            continue
        if fk in fl:
            return True
    return False


def _option_theme_cues(opts) -> list:
    """Trụ so sánh lấy từ nội dung phương án — không kèm chữ A–D, không chọn đáp."""
    themes = []
    rules = (
        (('nhiệt độ', 'nhanh', 'tốc độ', 'động năng'), 'quan hệ nhiệt độ–tốc độ/động năng phân tử'),
        (('hỗn loạn', 'mọi phía', 'không ngừng', 'brown'), 'chuyển động hỗn loạn liên tục'),
        (('gần nhau', 'lực tương tác', 'hút', 'đẩy', 'tương tác rất mạnh'), 'khoảng cách và lực tương tác giữa phân tử'),
        (('thể tích', 'khoảng cách', 'rất nhỏ so với'), 'kích thước phân tử so với khoảng cách'),
        (('nóng chảy', 'nhiệt nóng chảy', r'\lambda', 'λ', 'lambda'), 'nhiệt nóng chảy / hệ số λ'),
        (('hóa hơi', 'bay hơi', 'nhiệt hóa hơi'), 'nhiệt hóa hơi / hệ số L'),
        ((r'\Delta T', r'\Delta t', 'ΔT', 'Δt', 'delta t', 'nhiệt dung', r'mc\Delta', 'q=mc'),
         'đốt nóng có ΔT ($Q=mc\\Delta T$)'),
        (('uit', 'q=uit', 'cường độ dòng', 'hiệu điện thế'), 'nhiệt điện $Q=UIt$'),
        (('ester', 'xà phòng', 'rcoor'), 'phản ứng ester / xà phòng hóa'),
        (('glucose', 'tollens', 'tráng bạc'), 'nhóm chức và phản ứng đặc trưng carbohydrate'),
        (('cpu', 'bộ xử lý', 'ổ cứng', 'bộ nhớ'), 'vai trò CPU / bộ nhớ / thiết bị lưu trữ'),
        (('quang hợp', 'glucose', 'o2', 'ánh sáng'), 'điều kiện và sản phẩm quang hợp'),
    )
    for opt in opts or []:
        plain = re.sub(r'^[A-Da-d][.):]\s*', '', str(opt)).strip()
        if len(plain) < 4:
            continue
        for keys, label in rules:
            if _option_theme_hit(plain, keys) and label not in themes:
                themes.append(label)
    return themes[:5]


def _strip_option_bodies(text: str, opts) -> str:
    """Không để nguyên văn phương án / đáp án lọt vào HD."""
    body = str(text or '')
    for o in opts or []:
        piece = re.sub(r'^[A-D][.):]\s*', '', str(o), flags=re.I).strip()
        if len(piece) > 12 and piece in body:
            body = body.replace(piece, 'phương án tương ứng')
    return body


def _conceptual_mc_guide(stem: str, opts, subject: str, pack_formula: str = '', pack_prompt: str = '') -> tuple:
    """Câu khái niệm / phát biểu: Maieutics kiểu F VIP — hỏi đỡ đẻ, neo SGK, không lộ đáp."""
    topic = _topic_phrase(stem)
    themes = _option_theme_cues(opts)
    negation = _is_negation_stem(stem)
    subj = canonical_subject(subject or 'Toán học')
    if pack_formula:
        formula = pack_formula
    else:
        formula = (
            f'**{topic}** (SGK {subj}): nhắc 3–4 giả thiết/định nghĩa cốt lõi và công thức liên quan '
            r'(nếu có, ví dụ $pV=nRT$ với khí). Chưa gắn chữ A–D.'
        )
    if negation:
        step1 = (
            f'Đề hỏi phát biểu **không đúng** về “{topic}”. '
            'Em tách yêu cầu: đang tìm ý **lệch** giả thiết mô hình — không phải tìm ý đúng nhất.'
        )
    else:
        step1 = (
            f'Với “{topic}”, em xác định đề đang hỏi đặc trưng nào? '
            'Ghi rõ tiêu chí đúng/sai trước khi mở từng phương án.'
        )
    if themes:
        # F VIP computing_context style: hỏi tiêu chí phân biệt theo từng trụ phương án.
        step2 = (
            'Các phương án đang xoay quanh: ' + '; '.join(themes) + '. '
            'Em sẽ nhắc giả thiết/công thức SGK cho **từng trụ** theo tiêu chí nào '
            'trước khi đối chiếu từng phát biểu?'
        )
    elif pack_prompt:
        step2 = pack_prompt
    else:
        step2 = (
            f'Em gọi tên 3–4 giả thiết cốt lõi của “{topic}” môn {subj} '
            'theo tiêu chí nào, rồi mới đối chiếu từng phát biểu?'
        )
    if negation:
        step3 = (
            'Với mỗi phát biểu: hỏi “khớp hay lệch giả thiết vừa nhắc?”. '
            'Giữ lại ứng viên lệch — em tự kết luận, chưa gắn chữ A–D giúp.'
        )
    else:
        step3 = (
            'Với mỗi phát biểu: hỏi “khớp giả thiết/công thức vừa nhắc chưa?”. '
            'Em tự chọn phương án khớp ngữ liệu — chưa gắn chữ A–D giúp.'
        )
    return formula, [step1, step2, step3]


def _subject_stem_guide(question, subject) -> tuple:
    """HD Socratic đa môn: bám stem + trụ phương án + neo SGK. Đỡ đẻ ý tưởng, không lộ đáp."""
    q = question if isinstance(question, dict) else {}
    stem = str(q.get('q') or '')
    low = stem.lower()
    text = folded(stem)
    quote = _short_stem_quote(stem)
    opts = q.get('opt') or q.get('options') or []
    hit = _matched_anchor(subject, stem)
    subj = canonical_subject(subject or 'Toán học')
    conceptual = bool(opts) and any(k in text for k in (
        'phat bieu', 'y nao', 'dac diem nao', 'khang dinh', 'cho rang',
        'khong dung', 'dung khi', 'sai khi', 'which of the following',
    ))

    # --- Mô hình động học phân tử chất khí (F VIP: đỡ đẻ misconception, không lộ đáp) ---
    if any(k in text for k in (
        'dong hoc phan tu', 'mo hinh dong hoc', 'phan tu khi', 'chat khi',
        'khi ly tuong', 'chuyen dong hon loan',
    )):
        formula = (
            '**Mô hình động học phân tử chất khí** (SGK Vật lý): '
            '(1) phân tử chuyển động hỗn loạn, liên tục mọi hướng; '
            '(2) khoảng cách trung bình $\\gg$ kích thước phân tử; '
            '(3) lực tương tác giữa các phân tử khí rất yếu '
            '(khí lý tưởng: xem như không đáng kể); '
            '(4) nhiệt độ liên hệ động năng trung bình / tốc độ chuyển động nhiệt. '
            'Công thức trạng thái khi cần: $pV=nRT$.'
        )
        prompt = (
            'Em sẽ phân biệt bốn trụ của mô hình — chuyển động hỗn loạn; nhiệt độ–tốc độ; '
            'khoảng cách & lực tương tác; kích thước so với khoảng cách — '
            'theo tiêu chí nào trước khi đối chiếu từng phát biểu?'
        )
        return _conceptual_mc_guide(stem, opts, subj, pack_formula=formula, pack_prompt=prompt)

    # --- Vật lý nhiệt / chuyển thể ---
    if any(k in text for k in (
        'nong chay', 'lam nong chay', 'hoa hoi', 'bay hoi', 'nhiet luong',
        'nhiet dung', 'lam nong',
    )) or (subj == 'Vật lý' and 'nhiet' in text and 'dong hoc' not in text):
        melting = 'nong chay' in text
        vapor = 'hoa hoi' in text or 'bay hoi' in text
        if melting and not vapor:
            formula = (
                'Câu hỏi về **nóng chảy hoàn toàn** khối lượng $m$ ở nhiệt độ nóng chảy '
                '(nhiệt độ không đổi khi chuyển thể). '
                'Phân biệt với $Q=mc\\Delta T$ (có $\\Delta T$) và $Q=UIt$ (dòng điện); '
                'nóng chảy / hóa hơi dùng hệ số chuyển thể khác nhau trong SGK.'
            )
            return formula, [
                f'Gạch yêu cầu đúng câu này: “{_short_stem_quote(stem, 88)}”.',
                'Hỏi: đây là đốt nóng có $\\Delta T$, chuyển thể ở nhiệt độ không đổi, hay nhiệt điện?',
                'Với chuyển thể nóng chảy, $Q$ tỉ lệ với $m$; đối chiếu ký hiệu hệ số nóng chảy vs hóa hơi — em tự chọn công thức khớp, chưa chốt phương án hộ.',
            ]
        if vapor and not melting:
            formula = (
                'Câu hỏi về **hóa hơi** / bay hơi: nhiệt chuyển thể ở nhiệt độ không đổi, tỉ lệ với $m$. '
                'Phân biệt với nóng chảy và với $Q=mc\\Delta T$, $Q=UIt$.'
            )
            return formula, [
                f'Bám đúng ngữ liệu: {quote}.',
                'Xác định đang hóa hơi (không phải nóng chảy hay đốt nóng có $\\Delta T$).',
                'Chọn dạng $Q$ tỉ lệ $m$ với hệ số hóa hơi trong SGK — tự đối chiếu phương án.',
            ]
        formula = (
            'Nhiệt lượng: đốt nóng $Q=mc\\Delta T$; chuyển thể (nóng chảy / hóa hơi) tỉ lệ $m$ ở nhiệt độ không đổi; '
            'nhiệt điện $Q=UIt$. Chọn đúng loại hiện tượng câu hỏi.'
        )
        return formula, [
            f'Đọc lại yêu cầu: {quote}.',
            'Phân loại hiện tượng trước khi nhìn phương án.',
            'Đối chiếu từng công thức với đúng loại hiện tượng — chưa chọn hộ.',
        ]

    # --- Neo SGK khớp stem ---
    if hit.get('concept'):
        line = _formula_lines_for_stem(hit.get('formula', ''), stem)
        formula = f"{hit['concept']}. " + (line if line else '')
        formula = formula.strip() or hit['concept']
        if conceptual or opts:
            return _conceptual_mc_guide(
                stem, opts, subj,
                pack_formula=formula,
                pack_prompt=hit.get('prompt') or '',
            )
        prompt = hit.get('prompt') or ''
        return formula, [
            f'Bám đúng câu hỏi: {quote}.',
            prompt if prompt and not looks_like_explain_solution(prompt) else
            'Chọn định nghĩa/công thức khớp hiện tượng hoặc đại lượng câu hỏi — chưa thay số hộ.',
            'Đối chiếu từng phương án với điều kiện trong ngữ liệu; loại công thức lệch hiện tượng.',
        ]

    # --- Câu khái niệm có phương án: luôn dùng trụ so sánh, không nhắc lại nguyên câu hỏi ---
    if conceptual or (opts and len(opts) >= 2):
        return _conceptual_mc_guide(stem, opts, subj)

    # --- Fallback cuối: vẫn phải có chủ đề stem, không generic trống ---
    topic = _topic_phrase(stem)
    return (
        f'Chủ đề ngữ liệu: **{topic}**. Nhắc định nghĩa/công thức SGK môn {subj} khớp đúng chủ đề đó.',
        [
            f'Gạch yêu cầu cần tìm gắn với “{topic}”.',
            f'Viết 2–3 đặc trưng/công thức cốt lõi của “{topic}” — chưa kết luận hộ.',
            'Đối chiếu lập luận với ngữ liệu; em tự chọn, chưa gắn chữ A–D giúp.',
        ],
    )


def _step_prompts(question, subject) -> list:
    stem = str((question or {}).get('q') or '')
    low = stem.lower()
    steps = []
    if any(k in low for k in ('đồ thị của hàm số nào', 'đường cong dưới đây', 'là của hàm số nào')):
        steps = [
            'Đọc từ hình: tiệm cận đứng (nếu có) và tiệm cận ngang/xiên.',
            'Với từng phương án, thay $x=0$ (hoặc điểm nằm trên hình) để đối chiếu giao trục — loại phương án lệch hình.',
            'Đối chiếu bậc tử/mẫu với dạng tiệm cận quan sát được; **không** chọn đáp án giúp — em tự loại trừ.',
        ]
    elif any(k in low for k in ('bảng biến thiên', 'bbt')):
        steps = [
            'Xác định dòng đang hỏi (khoảng đồng/nghịch biến, cực trị, hay tiệm cận).',
            'Đối chiếu dấu $y\'$ / mũi tên $y$ với đúng khoảng hoặc điểm trên bảng.',
            'Phân biệt hoành độ cực trị ($x$) và giá trị cực trị ($y$) trước khi kết luận.',
        ]
    elif (question or {}).get('mslgn_data') or any(k in low for k in ('ghép nhóm', 'tứ phân vị', 'trung vị', 'mốt')):
        steps = [
            'Tính cỡ mẫu $n=\\sum n_i$ từ đúng cột tần số đề cho.',
            'Cộng dồn tần số để tìm nhóm chứa đại lượng cần (ví dụ vị trí $n/2$, $n/4$, $3n/4$).',
            'Thay đúng $u_m$, $n_m$, $C$ vào công thức SGK — tự tính, không nhìn đáp án.',
        ]
    elif (question or {}).get('stmts'):
        steps = [
            'Viết lại giả thiết chung một lần; xét riêng từng mệnh đề a)–d).',
            'Với mỗi ý: nêu điều kiện cần/đủ hoặc thay số liệu đề vào — ghi Đúng/Sai độc lập.',
            'Không suy “vì a đúng nên b đúng”; mỗi ý một lập luận.',
        ]
    elif any(k in low for k in ('tập xác định', 'txđ')):
        steps = [
            'Xác định điều kiện có nghĩa: căn bậc hai thì biểu thức trong căn $\\ge 0$; mẫu thức $\\ne 0$.',
            'Giải điều kiện đó thành một tập và viết dạng khoảng — chưa kết luận phương án.',
            'Đối chiếu từng phương án với tập vừa tìm; tự loại phương án lệch.',
        ]
    elif 'parabol' in low and any(k in low for k in ('tọa độ đỉnh', 'đỉnh')):
        steps = [
            'Viết $y=ax^2+bx+c$ và đọc $a$, $b$ từ đúng hàm trong câu.',
            'Hoành độ đỉnh $x=-\\dfrac{b}{2a}$; thay hoành độ đó vào hàm để lấy tung độ — tự tính.',
            'Đối chiếu cặp $(x;y)$ với các phương án; không chọn hộ.',
        ]
    elif any(k in low for k in ('giá trị lớn nhất', 'giá trị nhỏ nhất', 'gtln', 'gtnn', 'max', 'min')):
        steps = [
            'Xác định đoạn/tập đang xét từ đề (hai đầu mút và điều kiện ẩn).',
            'Tính $f\'$, tìm nghiệm trong khoảng mở; so sánh $f$ tại các điểm tới hạn và đầu mút.',
            'Chọn GTLN/GTNN theo định nghĩa — không dừng ở cực trị nội nếu đầu mút lớn hơn.',
        ]
    else:
        subj = canonical_subject(subject or 'Toán học')
        if subj == 'Toán học':
            steps = [
                'Gạch chân dữ kiện số/điểm/điều kiện trong câu hỏi này (không dùng dữ kiện câu khác).',
                'Chọn công thức/định lý khớp yêu cầu; viết dạng tổng quát rồi mới thay số liệu đề.',
                'Tự tính và đối chiếu phương án; nếu trắc nghiệm thì loại trừ phương án mâu thuẫn dữ kiện.',
            ]
        else:
            steps = [
                'Tách dữ kiện đề cho khỏi yêu cầu cần tìm.',
                'Đối chiếu khái niệm/định luật/công thức liên quan trong SGK với đúng ngữ liệu câu này.',
                'Lập luận từng bước; không nhảy cóc sang đáp án.',
            ]
    return steps


def _interval_ends(interval: str) -> tuple:
    """Hai đầu mút đúng như đề ghi. Không suy nghiệm đạo hàm."""
    match = re.search(
        r'(-?\d+(?:[.,]\d+)?)\s*;\s*(-?\d+(?:[.,]\d+)?)',
        interval or '',
    )
    if not match:
        return '', ''
    return match.group(1), match.group(2)


def _function_and_interval(stem: str) -> tuple:
    """Hàm và đoạn đúng trong câu GTLN/GTNN. Không lấy đoạn mẫu [a;b]."""
    spans = [s.strip() for s in re.findall(r'\$([^$]{1,160})\$', stem or '') if s.strip()]
    fn = ''
    interval = ''
    for span in spans:
        if re.search(r'(?:y|f)\s*(?:\([^)]*\))?\s*=', span, re.I) and not fn:
            fn = '$' + span + '$'
        if re.search(r'[\[\(]\s*-?\d', span) and ';' in span and not interval:
            interval = '$' + re.sub(r'\s+', '', span) + '$'
    if not fn:
        match = re.search(
            r'((?:y|f)\s*(?:\([^)]*\))?\s*=\s*.+?)(?:\s+trên\b|\s+trong\b|$)',
            stem or '', re.I,
        )
        if match:
            fn = '$' + re.sub(r'\s+', ' ', match.group(1).strip()) + '$'
    if not interval:
        match = re.search(r'(\[\s*-?\d[^[\]]{0,16};\s*-?\d[^[\]]{0,12}\])', stem or '')
        if match:
            interval = re.sub(r'\s+', '', match.group(1))
    return fn or 'hàm trong câu', interval or 'đoạn trong câu'


def _quoted_expr(stem: str) -> str:
    """Khúc toán trong câu hỏi — đúng ngữ liệu, không phải phương án."""
    spans = [s.strip() for s in re.findall(r'\$([^$]{1,160})\$', stem or '') if s.strip()]
    if spans:
        best = max(spans, key=lambda s: (('=' in s or '\\' in s), len(s)))
        return '$' + best + '$'
    m = re.search(r'((?:y|f)\s*(?:\([^)]*\))?\s*=\s*[^:;.\n]{1,80})', stem or '', re.I)
    if m:
        return '$' + m.group(1).strip() + '$'
    return 'hàm trong câu'


def _is_hard_question(question, stem: str) -> bool:
    q = question if isinstance(question, dict) else {}
    level = folded(str(q.get('level') or ''))
    if any(mark in level for mark in ('vd', 'vdc')):
        return True
    text = folded(stem)
    hard = (
        'tham so', 'chung minh', 'gia tri lon nhat', 'gia tri nho nhat',
        'gtln', 'gtnn', 'bang bien thien', 'do thi cua ham so nao',
        'toa do dinh', 'tich phan', 'the tich', 'xac suat', 'parabol',
    )
    if any(mark in text for mark in hard):
        return True
    stmts = q.get('stmts') or []
    return isinstance(stmts, list) and len(stmts) >= 4


def _guide_plan(question, subject) -> tuple:
    """(công thức, các bước). Bám ngữ liệu. Câu khó thì nhiều bước hơn. Không ra đáp số."""
    q = question if isinstance(question, dict) else {}
    stem = str(q.get('q') or '')
    low = stem.lower()
    text = folded(stem)
    expr = _quoted_expr(stem)
    hard = _is_hard_question(q, stem)
    if any(k in low for k in ('tập xác định', 'txđ')) or 'tap xac dinh' in text:
        inside = re.search(r'\\sqrt\{([^{}]{1,40})\}', stem)
        if inside:
            formula = f'Với {expr}: căn có nghĩa khi ${inside.group(1)}\\ge 0$.'
        elif '\\frac' in stem or '/' in stem:
            formula = f'Với {expr}: mẫu thức khác 0.'
        else:
            formula = f'Với {expr}: viết điều kiện để biểu thức có nghĩa.'
        steps = [
            f'Đặt điều kiện có nghĩa của đúng {expr} — chưa giải.',
            'Giải điều kiện đó thành một tập, viết dạng khoảng.',
            'Đối chiếu tập vừa tìm với từng phương án; tự chọn khoảng khớp.',
        ]
        if hard:
            steps.insert(2, 'Nếu có tham số, giữ tham số trong điều kiện; chưa chốt giá trị.')
        return formula, steps
    if 'parabol' in low and any(k in low for k in ('tọa độ đỉnh', 'đỉnh')):
        formula = f'Với {expr}: hoành độ đỉnh $x=-\\dfrac{{b}}{{2a}}$.'
        return formula, [
            f'Từ {expr}, ghi $a$ và $b$ — chưa tính $x$.',
            'Tính hoành độ bằng công thức trên.',
            'Thay hoành độ đó vào đúng hàm này để lấy tung độ.',
            'Ghép cặp $(x;y)$ rồi mới đối chiếu phương án.',
        ]
    if any(k in low for k in ('đồ thị của hàm số nào', 'đường cong dưới đây', 'là của hàm số nào')):
        formula = 'Tiệm cận đứng: mẫu $=0$. Giao trục tung: thay $x=0$.'
        steps = [
            'Trên đúng hình câu này, đọc hoành độ tiệm cận đứng.',
            'Đọc tung độ giao trục tung.',
            'Loại phương án lệch một trong hai điểm đó.',
        ]
        if hard:
            steps.append('Nếu còn hai phương án, đối chiếu bậc tử/mẫu với tiệm cận xiên hoặc nhánh.')
        return formula, steps
    if any(k in low for k in ('bảng biến thiên', 'bbt')):
        formula = "Đọc dòng $x$, dấu $y'$ và mũi tên $y$ trên đúng bảng của câu."
        return formula, [
            'Xác định câu hỏi dòng nào: khoảng biến thiên, cực trị, hay tiệm cận.',
            "Khoảng có $y'>0$ thì $y$ tăng; $y'<0$ thì $y$ giảm.",
            'Hoành độ cực trị là $x$ nơi $y\'$ đổi dấu; giá trị cực trị là $y$ tại đó.',
            'Chưa kết luận trước khi đối chiếu đúng dòng bảng.',
        ]
    if q.get('mslgn_data') or any(k in low for k in ('ghép nhóm', 'tứ phân vị', 'trung vị', 'mốt')):
        formula = r'Trung vị: $M_e=u_m+\dfrac{\frac{n}{2}-C}{n_m}\cdot(u_{m+1}-u_m)$.'
        return formula, [
            'Cộng đúng cột tần số của bảng này để ra $n$.',
            'Tìm nhóm chứa vị trí $n/2$; đó là nhóm $m$.',
            'Lấy $u_m$, $n_m$, $C$ của nhóm đó trên bảng — chưa thay số có sẵn ở phương án.',
            'Thay vào công thức rồi tự tính.',
        ]
    if q.get('stmts'):
        formula = 'Mỗi ý Đúng/Sai một điều kiện riêng, lấy từ giả thiết chung của câu.'
        steps = [
            'Viết lại giả thiết chung một lần.',
            'Với ý đang xét: nêu điều kiện rồi đối chiếu dữ kiện câu — ghi Đúng hoặc Sai.',
            'Không suy ý sau từ ý trước.',
        ]
        if hard:
            steps.append('Ý vận dụng: thay đúng số liệu đề vào công thức, chưa lấy kết quả in sẵn.')
        return formula, steps
    if 'lai kep' in text or ('lai suat' in text and 'nam' in text):
        money = re.search(r'(\d+(?:[.,]\d+)?)\s*triệu', stem, re.I)
        pct = re.search(r'(\d+(?:[.,]\d+)?)\s*%', stem)
        years = re.search(r'(\d+)\s*năm', stem, re.I)
        p = money.group(1) if money else 'P'
        r = pct.group(1) if pct else 'r'
        n = years.group(1) if years else 'n'
        formula = r'Lãi kép: $A=P(1+r)^{n}$. $r$ là lãi một năm viết dạng số thập phân.'
        return formula, [
            f'Đọc đúng câu này: vốn {p} triệu, lãi suất {r}%/năm, thời hạn {n} năm. Đổi {r}% sang số thập phân — chưa nhân.',
            r'Thay ba số đó vào $A=P(1+r)^{n}$.',
            'Tính và làm tròn đúng đơn vị câu hỏi. Tự ra số, chưa lấy đáp án in sẵn.',
        ]
    if any(k in text for k in ('gia tri lon nhat', 'gia tri nho nhat', 'gtln', 'gtnn')):
        fn, interval = _function_and_interval(stem)
        pick = 'số lớn nhất' if ('lon nhat' in text or 'gtln' in text) else 'số nhỏ nhất'
        label = 'GTLN' if pick == 'số lớn nhất' else 'GTNN'
        kind = 'giá trị lớn nhất' if pick == 'số lớn nhất' else 'giá trị nhỏ nhất'
        left, right = _interval_ends(interval)
        stem_compact = re.sub(r'\s+', '', stem)
        quadratic = (
            'ham so bac hai' in text
            or 'bac hai' in text
            or (
                bool(re.search(r'x\^\{?2\}?|x²', stem_compact, re.I))
                and bool(re.search(r'(?:y|f)\s*(?:\([^)]*\))?\s*=', stem, re.I))
            )
        )
        vertex_hint = (
            f"Với hàm bậc hai {fn}, hoành độ đỉnh $x=-\\dfrac{{b}}{{2a}}$ cũng là ứng viên "
            f"(cùng vai trò nghiệm $y'=0$) — chưa thay số, chưa lấy {label}."
        )
        if left and right:
            formula = (
                f'Trên {interval}, {label} của {fn} là {kind} trong các $f({left})$, $f({right})$ '
                f"và $f$ tại nghiệm của $y'=0$ nằm trong $({left};{right})$."
            )
            steps = [
                f"Tính đạo hàm $y'$ của đúng {fn}. Chưa giải nghiệm.",
                f"Giải $y'=0$ nhưng chưa thay vào $y$. Chỉ giữ nghiệm nằm trong $({left};{right})$.",
                f'Tính $y$ tại ${left}$, tại ${right}$ và tại nghiệm nằm trong khoảng mở.',
                f'So sánh các giá trị đó để tự chọn {pick}.',
            ]
            if quadratic:
                steps.insert(1, vertex_hint)
            return formula, steps
        formula = (
            f'Trên {interval}, {label} của {fn} là {kind} trong các giá trị '
            f"tại hai đầu mút và tại nghiệm của $y'=0$ nằm trong khoảng mở."
        )
        steps = [
            f"Tính đạo hàm $y'$ của đúng {fn}. Chưa giải nghiệm.",
            f"Giải $y'=0$ nhưng chưa thay vào $y$. Chỉ giữ nghiệm nằm trong khoảng mở của {interval}.",
            f'Tính $y$ tại hai đầu mút của {interval} và tại nghiệm vừa giữ.',
            f'So sánh các giá trị đó để tự chọn {pick}.',
        ]
        if quadratic:
            steps.insert(1, vertex_hint)
        return formula, steps
    if canonical_subject(subject) == 'Toán học':
        asked = math_context_question(stem)
        # Neo Toán nếu có; vẫn ưu tiên biểu thức trong câu.
        hit = _matched_anchor(subject, stem)
        if expr != 'hàm trong câu':
            formula = f'Công thức áp vào đúng {expr}.'
        elif hit.get('formula'):
            formula = _formula_lines_for_stem(hit['formula'], stem) or hit.get('concept') or 'Chọn đúng công thức của yêu cầu câu này.'
        else:
            formula = 'Chọn đúng công thức của yêu cầu câu này.'
        steps = [
            f'Gạch điều kiện và hệ số trong {expr}.' if expr != 'hàm trong câu' else f'Gạch yêu cầu trong câu: {_short_stem_quote(stem)}.',
            'Viết công thức tổng quát, rồi mới thay số của câu.',
            'Tự tính; đối chiếu phương án sau khi có kết quả của em.',
        ]
        if asked:
            steps.append(asked)
        if hard:
            steps.append('Tách từng ẩn hoặc tham số; làm xong một nhánh rồi mới sang nhánh kia.')
        return formula, steps
    # Đa môn / đa lớp: không còn HD chung chung — bám stem + neo SGK.
    formula, steps = _subject_stem_guide(q, subject)
    if hard and len(steps) < 4:
        steps.append(f'Câu khó: mỗi luận điểm một dẫn chứng lấy từ “{_short_stem_quote(stem, 48)}”, rồi mới kết.')
    return formula, steps


def build_tram3_socratic_guide(question, subject='Toán học', grade_num=12) -> str:
    """HD Socratic dùng chung Trạm 1 & 3: hướng đi + công thức bám ngữ liệu. Không lộ đáp án, không lấy explain."""
    q = question if isinstance(question, dict) else {}
    # Chuẩn hóa khóa Trạm 1 (question/options/correct) ↔ Trạm 3 (q/opt/ans).
    if 'q' not in q and q.get('question'):
        q = dict(q)
        q['q'] = q.get('question')
    if 'opt' not in q and q.get('options') is not None:
        q = dict(q)
        q['opt'] = q.get('options')
    opts = q.get('opt') or []
    # explain / ans chỉ để lọc rò rỉ — không đưa vào HD.
    formula, steps = _guide_plan(q, subject)
    # Loại bước giống lời giải / chọn đáp.
    clean_steps = []
    for step in steps:
        if looks_like_explain_solution(step):
            continue
        clean_steps.append(step)
    steps = clean_steps or steps[:3]
    shown = steps if _is_hard_question(q, str(q.get('q') or '')) else steps[:3]
    body = '**Công thức / hướng:** ' + formula + '\n\n' + '\n'.join(
        f'{i}. {step}' for i, step in enumerate(shown, 1)
    )
    body = _SOLUTION_LEAK.sub('', body)
    stem = str(q.get('q') or '')
    # Không để nguyên văn phương án / đáp án lọt vào HD.
    ans = str(q.get('ans') or q.get('correct') or '').strip()
    if ans and len(ans) <= 3 and re.fullmatch(r'[A-Da-d]', ans):
        body = re.sub(rf'(?i)\bđáp án\s*{ans}\b', 'đáp án tương ứng', body)
    for o in opts or []:
        piece = re.sub(r'^[A-D][.):]\s*', '', str(o), flags=re.I).strip()
        if len(piece) > 8 and piece in body and piece not in stem:
            body = body.replace(piece, 'phương án tương ứng')
    # Cấm HD generic cũ / echo-stem còn sót (ảnh anh: “Hướng đi từ đúng ngữ liệu…”).
    generic_marks = (
        'Bám đúng ngữ liệu câu này — chi tiết, số liệu hoặc điều kiện đề cho',
        'Hướng đi từ đúng ngữ liệu:',
        'Đối chiếu khái niệm đúng môn với đúng ngữ liệu này',
    )
    if any(m in body for m in generic_marks):
        formula2, steps2 = _subject_stem_guide(q, subject)
        body = '**Công thức / hướng:** ' + formula2 + '\n\n' + '\n'.join(
            f'{i}. {step}' for i, step in enumerate(steps2[:3], 1)
        )
        body = _strip_option_bodies(body, opts)
    return body.strip()


# Alias toàn hệ thống (Trạm 1 + Trạm 3).
build_socratic_guide = build_tram3_socratic_guide
