"""Subject-aware fallback questions, without certifying generated hint content."""
import re

from services.academic_context import canonical_subject, folded

T1_CONTEXT_REVISION = 2026110901


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


def _matched_anchor_formula(subject, question_text) -> tuple:
    try:
        from data.socratic_anchors import SOCRATIC_KNOWLEDGE_ANCHORS
    except Exception:
        return '', ''
    subj = canonical_subject(subject or 'Toán học')
    text = folded(question_text)
    best = None
    best_hits = 0
    for item in SOCRATIC_KNOWLEDGE_ANCHORS.get(subj, []) or []:
        hits = sum(1 for kw in item.get('keywords') or [] if folded(kw) in text)
        if hits > best_hits:
            best_hits = hits
            best = item
    if not best or best_hits <= 0:
        return '', ''
    return str(best.get('concept') or ''), str(best.get('formula') or '')


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


def build_tram3_socratic_guide(question, subject='Toán học', grade_num=12) -> str:
    """HD Socratic theo từng câu đề Trạm 3 — tách biệt tuyệt đối với field ``explain``.

    - Không đọc/ghép ``explain`` / ``explanation``.
    - Bám số liệu, hệ số, bảng của đúng câu hỏi.
    - Chỉ công thức liên quan + bước tư duy + câu hỏi định hướng; không giải hộ, không lộ đáp án.
    """
    q = question if isinstance(question, dict) else {}
    # Cấm dùng explain làm nguồn HD.
    raw = str(q.get('socratic_hint') or q.get('hint') or '').strip()
    if looks_like_explain_solution(raw) or folded(raw) in _GENERIC_HINTS:
        raw = ''

    opts = q.get('opt') or []
    ans = q.get('ans') or ''
    stem = str(q.get('q') or '')

    kept = ''
    if raw:
        kept = guiding_question(raw, opts, ans, stem) or ''
        if not kept and raw.endswith('?') and not looks_like_explain_solution(raw):
            kept = raw
        if kept and looks_like_explain_solution(kept):
            kept = ''

    facts = _question_given_facts(q)
    concept, formula = _matched_anchor_formula(subject, stem)
    steps = _step_prompts(q, subject)

    blocks = [
        '*(**HD Socratic** = gợi bước tư duy & công thức liên quan. '
        'Khác hẳn phần **explain** / lời giải tham khảo. Hệ thống không giải hộ — em tự tính.)*'
    ]
    if facts:
        blocks.append('**Dữ kiện bám sát câu này:**\n' + '\n'.join(f'- {f}' for f in facts))
    if concept or formula:
        piece = f'**Điểm tựa kiến thức:** {concept}' if concept else '**Điểm tựa kiến thức / công thức liên quan:**'
        if formula:
            piece += '\n' + formula
        blocks.append(piece)
    if steps:
        # Scrub từng bước (tránh regex đụng nhãn khung HD).
        scrubbed_steps = []
        for s in steps:
            scrubbed_steps.append(_SOLUTION_LEAK.sub('[…]', s))
        blocks.append(
            '**Các bước tư duy (em tự làm):**\n'
            + '\n'.join(f'{i}. {s}' for i, s in enumerate(scrubbed_steps, 1))
        )

    closing = kept
    if not closing:
        if canonical_subject(subject) != 'Toán học':
            closing = subject_socratic_hint('', subject, opts, ans, stem)
        else:
            closing = math_context_question(stem) or (
                'Với đúng các dữ kiện trên, em sẽ bắt đầu từ đại lượng nào và kiểm tra điều kiện nào trước khi kết luận?'
            )
    closing = _SOLUTION_LEAK.sub('[…]', str(closing or '').strip())
    if closing and not closing.endswith('?'):
        closing = closing.rstrip('.') + '?'
    blocks.append('**Câu hỏi định hướng:** ' + closing)

    text = '\n\n'.join(blocks)
    # Không để nguyên văn đáp án dài / phương án đúng lọt vào HD.
    for o in opts or []:
        body = re.sub(r'^[A-D][.):]\s*', '', str(o), flags=re.I).strip()
        if len(body) > 8 and body in text and body not in stem:
            text = text.replace(body, 'phương án tương ứng')
    return text
