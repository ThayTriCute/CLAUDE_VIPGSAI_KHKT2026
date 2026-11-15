"""Subject-aware fallback questions, without certifying generated hint content."""
import re

from services.academic_context import canonical_subject, folded

T1_CONTEXT_REVISION = 2026111605


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
    # HD bình dân có công thức $Q=\ldots$ nhiều dấu = — không coi là explain.
    if 'Con đường tư duy' in value or 'thầy chỉ lối' in value:
        pass
    else:
        plain = re.sub(r'\$[^$]*\$', '', value)
        if len(value) > 700 and plain.count('=') >= 3:
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
    """Lấy cụm chủ đề trong stem — không lấy cả khung câu hỏi."""
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
            head = m.group(0)[: m.start(1) - m.start(0)].strip().lower()
            if any(h in head for h in ('mô hình', 'định luật', 'quy tắc', 'khái niệm', 'phản ứng', 'hiện tượng')):
                phrase = re.sub(r'\s+', ' ', m.group(0)).strip(' :;,.')
            if len(phrase) >= 6:
                return phrase[:100]
    cleaned = re.sub(
        r'^(?:phát biểu|ý|câu|đặc điểm|khẳng định|nhận định)\s+nào\s+(?:sau đây\s+)?'
        r'(?:không\s+đúng|đúng|sai)?\s*(?:khi\s+nói\s+về\s+|về\s+)?',
        '', raw, flags=re.I,
    ).strip(' ?？')
    return (cleaned[:90] + ('…' if len(cleaned) > 90 else '')) or _short_stem_quote(stem, 60)


def _stem_givens_line(stem: str) -> str:
    """Số liệu / dữ kiện đề cho — để HD bình dân nói rõ 'đề cho gì'."""
    raw = re.sub(r'\s+', ' ', str(stem or '')).strip()
    bits = []
    for m in re.finditer(
        r'(\d+(?:[.,]\d+)?)\s*(viên|quả|học sinh|người|mol|g|kg|m|cm|s|phút|giờ|%|triệu|'
        r'đỏ|xanh|vàng|đen|trắng)?',
        raw, re.I,
    ):
        chunk = (m.group(0) or '').strip()
        if chunk and chunk not in bits:
            bits.append(chunk)
        if len(bits) >= 6:
            break
    # Cụm "có … và …" ngắn
    pair = re.search(
        r'(?:có|gồm|cho)\s+([^.]{8,70}?(?:và|với)\s+[^.]{3,40})',
        raw, re.I,
    )
    if pair:
        bits.insert(0, re.sub(r'\s+', ' ', pair.group(0)).strip()[:80])
    if not bits:
        return ''
    # Khử trùng lặp gần nhau
    uniq = []
    for b in bits:
        if not any(b in u or u in b for u in uniq):
            uniq.append(b)
    return 'Đề cho: ' + '; '.join(uniq[:4]) + '.'


def _folded_token_hit(fl: str, fk: str) -> bool:
    """Khớp token folded — tránh 'nhiet do' dính 'nhiet doi'."""
    if not fk or len(fk) < 2:
        return False
    if len(fk) <= 5:
        return bool(re.search(r'(?:^|\s)' + re.escape(fk) + r'(?:\s|$)', fl))
    return fk in fl


def _option_theme_hit(plain: str, keys) -> bool:
    """Khớp trụ phương án; bỏ khóa folded rỗng/1 ký tự (λ→'', Δt→'t')."""
    fl = folded(plain)
    for k in keys:
        raw = str(k)
        if raw in plain:
            return True
        fk = folded(raw)
        if _folded_token_hit(fl, fk):
            return True
    return False


def _option_axis_labels(opts, subject: str = '', stem: str = '') -> list:
    """Trụ so sánh từ phương án — theo môn/ngữ liệu, không kèm chữ A–D."""
    subj = canonical_subject(subject or '')
    text = folded(stem)
    physics_mol = subj in ('Vật lý', 'Khoa học tự nhiên') or any(
        k in text for k in ('dong hoc', 'phan tu khi', 'chat khi', 'khi ly tuong')
    )
    physics_heat = subj in ('Vật lý', 'Khoa học tự nhiên') or any(
        k in text for k in ('nong chay', 'hoa hoi', 'nhiet luong', 'nhiet dung')
    )
    rules = []
    if physics_mol:
        rules.extend((
            (('nhiệt độ', 'nhanh', 'tốc độ', 'động năng'), 'quan hệ nhiệt độ–tốc độ/động năng phân tử'),
            (('hỗn loạn', 'mọi phía', 'không ngừng'), 'chuyển động hỗn loạn liên tục'),
            (('gần nhau', 'lực tương tác', 'tương tác rất mạnh', 'tương tác rất yếu'),
             'khoảng cách và lực tương tác giữa phân tử'),
            (('thể tích', 'khoảng cách', 'rất nhỏ so với'), 'kích thước phân tử so với khoảng cách'),
        ))
    if physics_heat:
        rules.extend((
            (('nóng chảy', 'nhiệt nóng chảy', r'\lambda', 'λ', 'lambda'), 'nhiệt nóng chảy / hệ số λ'),
            (('hóa hơi', 'bay hơi', 'nhiệt hóa hơi'), 'nhiệt hóa hơi / hệ số L'),
            ((r'\Delta T', r'\Delta t', 'ΔT', 'Δt', 'delta t', 'nhiệt dung', r'mc\Delta'),
             'đốt nóng có ΔT ($Q=mc\\Delta T$)'),
            (('uit', 'q=uit', 'cường độ dòng', 'hiệu điện thế'), 'nhiệt điện $Q=UIt$'),
        ))
    if subj in ('Hóa học', 'Khoa học tự nhiên') or any(k in text for k in ('benzene', 'ester', 'glucose')):
        rules.extend((
            (('ester', 'xà phòng', 'rcoor'), 'phản ứng ester / xà phòng hóa'),
            (('glucose', 'tollens', 'tráng bạc'), 'nhóm chức carbohydrate / Tollens'),
            (('benzene', 'thế', 'cộng', 'thơm', 'br2', 'hno3'), 'phản ứng thế / cộng của benzene'),
        ))
    if subj == 'Tin học' or 'cpu' in text:
        rules.append((('cpu', 'bộ xử lý', 'ổ cứng', 'bộ nhớ', 'lưu trữ'), 'vai trò CPU / bộ nhớ / lưu trữ'))
    if subj == 'Sinh học' or 'quang hop' in text:
        rules.append((('quang hợp', 'glucose', 'o2', 'ánh sáng', 'lục lạp'), 'điều kiện / sản phẩm quang hợp'))
    if subj == 'Địa lý' or any(k in text for k in ('dong bang', 'vung', 'khi hau', 'dia hinh')):
        rules.extend((
            (('địa hình', 'đồi', 'núi', 'đồng bằng'), 'đặc điểm địa hình'),
            (('sông', 'kênh', 'rạch', 'mạng lưới'), 'mạng lưới sông / kênh rạch'),
            (('khí hậu', 'gió mùa', 'nhiệt đới', 'cận nhiệt'), 'đặc điểm khí hậu'),
            (('khoáng sản', 'dầu', 'khí', 'than'), 'tài nguyên khoáng sản'),
        ))
    if subj == 'Ngữ văn' or any(k in text for k in ('doan van', 'cam nhan', 'hinh anh', 'tu ngu')):
        rules.extend((
            (('không gian', 'cảm nhận', 'không khí', 'bức tranh'), 'cảm nhận không gian / không khí'),
            (('rộng', 'hùng vĩ', 'bao la'), 'không gian rộng / hùng vĩ'),
            (('ẩm', 'gần gũi', 'thơ', 'lất phất'), 'không gian gần gũi / chất thơ'),
            (('khô', 'ồn', 'đô thị'), 'không gian khô / ồn ào'),
        ))
    themes = []
    for opt in opts or []:
        plain = re.sub(r'^[A-Da-d][.):]\s*', '', str(opt)).strip()
        if len(plain) < 4:
            continue
        hit_label = None
        for keys, label in rules:
            if _option_theme_hit(plain, keys):
                hit_label = label
                break
        if hit_label and hit_label not in themes:
            themes.append(hit_label)
        elif not hit_label:
            # Trụ rút gọn từ phương án (không chữ A–D) — bình dân, sát ngữ liệu.
            short = re.sub(r'\s+', ' ', plain)
            short = short[:42] + ('…' if len(short) > 42 else '')
            if short and short not in themes:
                themes.append(f'ý về “{short}”')
    return themes[:4]


def _strip_option_bodies(text: str, opts) -> str:
    """Không để nguyên văn phương án / đáp án lọt vào HD."""
    body = str(text or '')
    for o in opts or []:
        piece = re.sub(r'^[A-D][.):]\s*', '', str(o), flags=re.I).strip()
        if len(piece) > 12 and piece in body:
            body = body.replace(piece, 'phương án tương ứng')
    return body


def _teacher_path_guide(stem: str, opts, subject: str, pack_formula: str = '',
                        pack_prompt: str = '', checklist=None) -> tuple:
    """HD bình dân học vụ: phải làm gì → áp dụng gì → tư duy thế nào. Không lộ đáp."""
    topic = _topic_phrase(stem)
    themes = _option_axis_labels(opts, subject, stem)
    negation = _is_negation_stem(stem)
    subj = canonical_subject(subject or 'Toán học')
    givens = _stem_givens_line(stem)
    checklist = [c for c in (checklist or []) if c][:4]

    if pack_formula:
        formula = pack_formula
    elif checklist:
        formula = (
            f'**{topic}** (SGK {subj}). Checklist cốt lõi: '
            + '; '.join(f'({i}) {c}' for i, c in enumerate(checklist, 1))
            + '.'
        )
    else:
        formula = (
            f'**{topic}** (SGK {subj}). '
            'Em nhắc lại định nghĩa / giả thiết / công thức cốt lõi đúng chủ đề này trong SGK, '
            'rồi dùng làm thước đo để đối chiếu từng ý — chưa gắn chữ A–D.'
        )

    # 1) Hiểu ngữ liệu: đề hỏi gì / cho gì
    if negation:
        step1 = (
            f'Đọc kỹ ngữ liệu: đề đang tìm phát biểu **không đúng** về “{topic}”. '
            'Việc của em là tìm ý **lệch** giả thiết/định nghĩa — không phải tìm ý “hay nhất”.'
        )
    else:
        step1 = (
            f'Đọc kỹ ngữ liệu: đề hỏi gì về “{topic}”? '
            'Gạch yêu cầu (đúng/sai, đặc trưng, nguyên nhân…) trước khi mở phương án.'
        )
    if givens:
        step1 = givens + ' ' + step1

    # 2) Chọn thước đo / công thức
    if checklist:
        step2 = (
            'Lập thước đo từ SGK: ' + '; '.join(checklist)
            + '. Đây là con đường đối chiếu — chưa kết luận hộ.'
        )
    elif pack_prompt and not looks_like_explain_solution(pack_prompt):
        step2 = pack_prompt
    else:
        step2 = (
            f'Nhắc 3–4 ý cốt lõi / công thức SGK của “{topic}” môn {subj}. '
            'Đó là thước đo để đi tiếp — chưa thay số ra kết quả cuối.'
        )

    # 3) Đối chiếu theo trụ phương án
    if themes:
        step3 = (
            'Các phương án đang xoay quanh: ' + '; '.join(themes) + '. '
            'Với từng ý: hỏi “khớp thước đo vừa lập chưa?” rồi ghi khớp/lệch.'
        )
    else:
        step3 = (
            'Lần lượt từng phương án: đối chiếu với thước đo SGK vừa nêu; '
            'ghi rõ ý nào khớp, ý nào lệch — chưa gắn chữ A–D.'
        )

    # 4) Kết — tự chọn, không lộ đáp
    if negation:
        step4 = (
            'Giữ lại ý lệch thước đo (ứng viên “không đúng”). '
            'Em tự chọn — thầy không giải hộ, không chỉ chữ A–D.'
        )
    else:
        step4 = (
            'Giữ lại ý khớp thước đo / đúng yêu cầu ngữ liệu. '
            'Em tự chọn — thầy không giải hộ, không chỉ chữ A–D.'
        )
    return formula, [step1, step2, step3, step4]


def _subject_stem_guide(question, subject) -> tuple:
    """HD Socratic đa môn×lớp: bình dân, sát ngữ liệu, con đường tư duy, không lộ đáp."""
    q = question if isinstance(question, dict) else {}
    stem = str(q.get('q') or '')
    text = folded(stem)
    quote = _short_stem_quote(stem)
    opts = q.get('opt') or q.get('options') or []
    hit = _matched_anchor(subject, stem)
    subj = canonical_subject(subject or 'Toán học')
    conceptual = bool(opts) and any(k in text for k in (
        'phat bieu', 'y nao', 'dac diem nao', 'khang dinh', 'nhan dinh', 'cho rang',
        'khong dung', 'dung khi', 'sai khi', 'cam nhan', 'which of the following',
    ))

    # --- ĐHPT chất khí ---
    if any(k in text for k in (
        'dong hoc phan tu', 'mo hinh dong hoc', 'phan tu khi', 'chat khi',
        'khi ly tuong', 'chuyen dong hon loan',
    )):
        formula = (
            '**Mô hình động học phân tử chất khí** (SGK Vật lý) — thước đo 4 giả thiết: '
            '(1) phân tử chuyển động hỗn loạn, liên tục mọi hướng; '
            '(2) khoảng cách trung bình $\\gg$ kích thước phân tử; '
            '(3) lực tương tác giữa phân tử khí rất yếu (khí lý tưởng ≈ bỏ qua); '
            '(4) nhiệt độ liên hệ động năng trung bình / tốc độ chuyển động nhiệt. '
            'Khi cần phương trình trạng thái: $pV=nRT$.'
        )
        return _teacher_path_guide(
            stem, opts, subj,
            pack_formula=formula,
            checklist=[
                'chuyển động hỗn loạn',
                'khoảng cách $\\gg$ kích thước',
                'lực tương tác rất yếu',
                'nhiệt độ ↔ động năng/tốc độ',
            ],
        )

    # --- Vật lý nhiệt / chuyển thể ---
    if any(k in text for k in (
        'nong chay', 'lam nong chay', 'hoa hoi', 'bay hoi', 'nhiet luong',
        'nhiet dung', 'lam nong',
    )) or (subj == 'Vật lý' and 'nhiet' in text and 'dong hoc' not in text):
        melting = 'nong chay' in text
        vapor = 'hoa hoi' in text or 'bay hoi' in text
        if melting and not vapor:
            formula = (
                'Ngữ liệu hỏi **nóng chảy hoàn toàn** khối lượng $m$ ở nhiệt độ nóng chảy '
                '(chuyển thể: nhiệt độ không đổi). '
                'Công thức hướng đi: nóng chảy $Q=\\lambda m$. '
                'Đừng nhầm với đốt nóng $Q=mc\\Delta T$ (có $\\Delta T$), hóa hơi $Q=Lm$, nhiệt điện $Q=UIt$.'
            )
            return formula, [
                f'Việc 1 — hiểu đề: “{_short_stem_quote(stem, 88)}”. Đề đang hỏi nhiệt lượng kiểu gì?',
                'Việc 2 — phân loại: có $\\Delta T$ không? Có dòng điện không? Hay chuyển thể nóng chảy ở nhiệt độ không đổi?',
                'Việc 3 — chọn dạng $Q$ tỉ lệ $m$ với hệ số nóng chảy (phân biệt ký hiệu với hóa hơi) — tự đối chiếu phương án, chưa chọn hộ.',
            ]
        if vapor and not melting:
            formula = (
                'Ngữ liệu hỏi **hóa hơi / bay hơi**: chuyển thể, nhiệt độ không đổi, $Q$ tỉ lệ $m$. '
                'Hướng đi: $Q=Lm$. Phân biệt nóng chảy $Q=\\lambda m$, đốt nóng $Q=mc\\Delta T$, điện $Q=UIt$.'
            )
            return formula, [
                f'Việc 1 — bám ngữ liệu: {quote}.',
                'Việc 2 — xác nhận đang hóa hơi (không phải nóng chảy hay đốt nóng có $\\Delta T$).',
                'Việc 3 — áp $Q$ tỉ lệ $m$ với hệ số hóa hơi SGK; tự tính/đối chiếu phương án.',
            ]
        formula = (
            'Ba nhánh nhiệt lượng SGK: đốt nóng $Q=mc\\Delta T$; '
            'chuyển thể (nóng chảy $Q=\\lambda m$ / hóa hơi $Q=Lm$); nhiệt điện $Q=UIt$.'
        )
        return formula, [
            f'Việc 1 — đọc yêu cầu: {quote}.',
            'Việc 2 — phân loại hiện tượng đúng câu hỏi trước khi nhìn phương án.',
            'Việc 3 — khớp công thức với đúng loại hiện tượng — em tự chọn, chưa gắn A–D.',
        ]

    # --- Hóa: benzene / phản ứng thế ---
    if 'benzene' in text or 'benzen' in text or (
        'phan ung the' in text and subj in ('Hóa học', 'Khoa học tự nhiên')
    ):
        formula = (
            '**Benzene** (SGK Hóa): vòng thơm ưu tiên phản ứng **thế** '
            '(giữ khung thơm; thường cần xúc tác). '
            'Phản ứng cộng vào vòng khó hơn anken bão hòa thường — đó là thước đo khi đề hỏi đúng/sai.'
        )
        return _teacher_path_guide(
            stem, opts, 'Hóa học',
            pack_formula=formula,
            checklist=['ưu tiên thế (giữ thơm)', 'cộng khó hơn anken', 'điều kiện xúc tác đặc trưng'],
        )

    # --- Địa: ĐBSCL / vùng ---
    if subj == 'Địa lý' and any(k in text for k in ('dong bang song cuu long', 'dbscl', 'cuu long')):
        formula = (
            '**Đồng bằng sông Cửu Long** (SGK Địa): thước đo đặc trưng vùng — '
            'địa hình thấp phẳng; mạng lưới sông/kênh rạch dày; khí hậu nhiệt đới gió mùa '
            '(mưa nhiều); tài nguyên gắn phù sa / thủy sản / dầu khí ven biển — '
            'không lấy đặc điểm đồi núi chiếm ưu thế như trung du miền núi.'
        )
        return _teacher_path_guide(
            stem, opts, subj,
            pack_formula=formula,
            checklist=['địa hình thấp/phẳng', 'sông–kênh rạch dày', 'khí hậu nhiệt đới gió mùa', 'tài nguyên phù vùng'],
        )

    # --- Neo SGK khớp stem ---
    if hit.get('concept'):
        # Tránh neo "nghị luận" khi stem là đọc hiểu cảm nhận đoạn văn
        bad_nghi_luan = (
            'nghị luận' in folded(hit.get('concept', ''))
            and any(k in text for k in ('cam nhan', 'doan van sau', 'hinh anh', 'tu ngu', 'khong gian'))
            and 'nghi luan' not in text
        )
        if not bad_nghi_luan:
            line = _formula_lines_for_stem(hit.get('formula', ''), stem)
            formula = f"{hit['concept']}. " + (line if line else '')
            formula = formula.strip() or hit['concept']
            if conceptual or opts:
                return _teacher_path_guide(
                    stem, opts, subj,
                    pack_formula=formula,
                    pack_prompt=hit.get('prompt') or '',
                )
            prompt = hit.get('prompt') or ''
            givens = _stem_givens_line(stem)
            return formula, [
                (givens + ' ' if givens else '') + f'Việc 1 — hiểu yêu cầu: {quote}.',
                prompt if prompt and not looks_like_explain_solution(prompt) else
                'Việc 2 — chọn định nghĩa/công thức khớp đúng hiện tượng hoặc đại lượng câu hỏi — chưa thay số ra kết quả cuối.',
                'Việc 3 — đối chiếu từng phương án với điều kiện ngữ liệu; loại ý lệch — em tự chọn.',
            ]

    # --- Ngữ văn đọc hiểu cảm nhận ---
    if subj == 'Ngữ văn' or any(k in text for k in ('cam nhan', 'doan van sau', 'mua phun', 'hinh anh')):
        lit_topic = _topic_phrase(stem)
        formula = (
            f'**Đọc hiểu ngữ liệu** về “{lit_topic}”: '
            'bám từ ngữ / hình ảnh trong đoạn → nêu cảm nhận / đặc điểm không gian–không khí '
            'mà câu chữ gợi ra (không suy diễn ngoài đoạn).'
        )
        return _teacher_path_guide(
            stem, opts, 'Ngữ văn',
            pack_formula=formula,
            checklist=['bám từ ngữ/hình ảnh trong đoạn', 'nêu cảm nhận khớp sắc thái câu chữ', 'loại ý lệch ngữ liệu'],
        )

    # --- Câu khái niệm có phương án ---
    if conceptual or (opts and len(opts) >= 2):
        return _teacher_path_guide(stem, opts, subj)

    # --- Fallback: vẫn phải có đường đi sát chủ đề ---
    topic = _topic_phrase(stem)
    givens = _stem_givens_line(stem)
    return (
        f'Chủ đề ngữ liệu: **{topic}** (SGK {subj}). '
        'Nhắc định nghĩa/công thức khớp đúng chủ đề đó rồi dùng làm thước đo.',
        [
            ((givens + ' ') if givens else '') + f'Việc 1 — gạch yêu cầu gắn với “{topic}”.',
            f'Việc 2 — viết 2–3 đặc trưng/công thức cốt lõi của “{topic}” — chưa ra kết quả cuối.',
            'Việc 3 — đối chiếu lập luận với ngữ liệu; em tự chọn, thầy không gắn chữ A–D giúp.',
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
    if 'xac suat' in text or 'xác suất' in low:
        formula = r'Xác suất cổ điển: $P(A)=\dfrac{n(A)}{n(\Omega)}$. (Có điều kiện thì $P(A|B)=\dfrac{P(AB)}{P(B)}$.)'
        givens = _stem_givens_line(stem)
        return formula, [
            (givens + ' ' if givens else '') + 'Việc 1 — xác định không gian mẫu $\\Omega$ và biến cố $A$ đúng như đề hỏi (chưa chia).',
            r'Việc 2 — đếm $n(\Omega)$ và $n(A)$ từ số liệu đề; viết rõ trước khi thay vào công thức.',
            r'Việc 3 — thay vào $P(A)=n(A)/n(\Omega)$, tự tính rồi đối chiếu phương án — không lấy sẵn phân số ở đáp.',
        ]
    if canonical_subject(subject) == 'Toán học':
        asked = math_context_question(stem)
        hit = _matched_anchor(subject, stem)
        givens = _stem_givens_line(stem)
        if expr != 'hàm trong câu':
            formula = f'Công thức áp vào đúng {expr} trong ngữ liệu câu hỏi.'
        elif hit.get('formula'):
            formula = _formula_lines_for_stem(hit['formula'], stem) or hit.get('concept') or 'Chọn đúng công thức của yêu cầu câu này.'
        else:
            formula = 'Chọn đúng công thức của yêu cầu câu này theo SGK.'
        steps = [
            ((givens + ' ') if givens else '') + (
                f'Việc 1 — gạch điều kiện và hệ số trong {expr}.'
                if expr != 'hàm trong câu'
                else f'Việc 1 — gạch yêu cầu trong câu: {_short_stem_quote(stem)}.'
            ),
            'Việc 2 — viết công thức tổng quát khớp yêu cầu, rồi mới thay đúng số liệu đề (chưa ra kết quả cuối nếu chưa tính).',
            'Việc 3 — tự tính; đối chiếu phương án sau khi có kết quả của em — thầy không giải hộ.',
        ]
        if asked:
            steps.append(asked)
        if hard:
            steps.append('Câu khó: tách từng ẩn/tham số; xong một nhánh rồi mới sang nhánh kia.')
        return formula, steps
    # Đa môn / đa lớp: không còn HD chung chung — bám stem + neo SGK.
    formula, steps = _subject_stem_guide(q, subject)
    if hard and len(steps) < 4:
        steps.append(f'Câu khó: mỗi luận điểm một dẫn chứng lấy từ “{_short_stem_quote(stem, 48)}”, rồi mới kết.')
    return formula, steps


def _three_lines(*parts) -> str:
    """Tối đa 3 dòng, lời thầy hỏi — không tiêu đề, không đánh số."""
    lines = []
    for part in parts:
        for line in str(part or '').splitlines():
            line = re.sub(r'\s+', ' ', line).strip()
            if line:
                lines.append(line)
            if len(lines) >= 3:
                return '\n'.join(lines)
    return '\n'.join(lines)


def _plain_midwife(question, subject) -> str:
    """1–2 câu hỏi đỡ đẻ, xưng thầy–em, bám dữ kiện câu. Không chốt đáp."""
    q = question if isinstance(question, dict) else {}
    stem = str(q.get('q') or '')
    low = stem.lower()
    text = folded(stem)
    subj = canonical_subject(subject or 'Toán học')
    topic = _topic_phrase(stem)
    negation = _is_negation_stem(stem)
    expr = _quoted_expr(stem)

    if any(k in text for k in ('dong hoc phan tu', 'mo hinh dong hoc', 'phan tu khi', 'chat khi', 'khi ly tuong')):
        ask = 'không đúng' if negation else 'đúng'
        return _three_lines(
            f'Em ơi, câu này tìm phát biểu {ask} về mô hình động học phân tử chất khí.',
            'Thầy hỏi em: em còn nhớ giả thiết về chuyển động hỗn loạn, quan hệ nhiệt độ với tốc độ, khoảng cách so với kích thước, và lực tương tác không?',
            'Ý nào trái giả thiết em vừa nhớ thì là ý lệch — em tự chỉ ra, thầy không chốt hộ.',
        )

    if 'nong chay' in text and 'hoa hoi' not in text and 'bay hoi' not in text:
        return _three_lines(
            'Em đang tính nhiệt lượng để nóng chảy hoàn toàn một khối lượng $m$, ngay tại nhiệt độ nóng chảy.',
            'Lúc chuyển thể, nhiệt độ có đổi không — nên dạng $Q$ này khác đốt nóng có $\\Delta T$ và khác hóa hơi, khác nhiệt điện chỗ nào?',
            'Em nhớ hệ số nóng chảy rồi tự chọn, thầy không chốt công thức hộ.',
        )
    if 'hoa hoi' in text or 'bay hoi' in text:
        return _three_lines(
            'Em đang tính nhiệt khi hóa hơi, nhiệt độ không đổi và $Q$ tỉ lệ với khối lượng.',
            'Em phân biệt hệ số hóa hơi với nóng chảy và với $Q=mc\\Delta T$ thế nào?',
            'Em tự chọn dạng khớp, thầy không chốt hộ.',
        )

    if any(k in low for k in ('tập xác định', 'txđ')) or 'tap xac dinh' in text:
        inside = re.search(r'\\sqrt\{([^{}]{1,40})\}', stem)
        if inside:
            cond = f'${inside.group(1)}$'
            return _three_lines(
                f'Em tìm tập xác định của {expr}.',
                f'Thầy hỏi em: căn có nghĩa khi {cond} thỏa điều kiện gì?',
                'Em viết thành một khoảng rồi tự đối chiếu, thầy không giải khoảng hộ.',
            )
        return _three_lines(
            f'Em tìm tập xác định của {expr}.',
            'Mẫu thức hoặc biểu thức trong căn cần điều kiện gì thì hàm có nghĩa?',
            'Em tự viết khoảng, thầy không chốt hộ.',
        )

    if 'parabol' in low and any(k in low for k in ('tọa độ đỉnh', 'đỉnh')):
        return _three_lines(
            f'Em tìm tọa độ đỉnh của parabol {expr}.',
            r'Thầy hỏi em: hoành độ đỉnh là $x=-\dfrac{b}{2a}$; em đọc $a$, $b$ từ đúng hàm này rồi thay lại để lấy tung độ thế nào?',
            'Em ghép cặp $(x;y)$ và tự đối chiếu, thầy không chốt hộ.',
        )

    if any(k in text for k in ('gia tri lon nhat', 'gia tri nho nhat', 'gtln', 'gtnn')):
        fn, interval = _function_and_interval(stem)
        left, right = _interval_ends(interval)
        kind = 'lớn nhất' if ('lon nhat' in text or 'gtln' in text) else 'nhỏ nhất'
        if left and right:
            open_iv = f'({left};{right})'
            return _three_lines(
                f'Em tìm giá trị {kind} của hàm bậc hai {fn} trên đoạn {interval}.',
                f'Thầy hỏi em: em so $f({left})$, $f({right})$ với giá trị tại đỉnh $x=-\\dfrac{{b}}{{2a}}$ nếu đỉnh nằm trong ${open_iv}$, rồi lấy số {kind} thế nào?',
                'Em tự so sánh, thầy không ra số hộ.',
            )
        return _three_lines(
            f'Em tìm giá trị {kind} của {fn} trên {interval}.',
            r'Em tính ở hai đầu mút và tại nghiệm $y\'=0$ nằm trong khoảng mở, rồi chọn số nào?',
            'Em tự so, thầy không ra số hộ.',
        )

    if 'lai kep' in text or ('lai suat' in text and 'nam' in text):
        money = re.search(r'(\d+(?:[.,]\d+)?)\s*triệu', stem, re.I)
        pct = re.search(r'(\d+(?:[.,]\d+)?)\s*%', stem)
        years = re.search(r'(\d+)\s*năm', stem, re.I)
        p = money.group(1) if money else 'P'
        r = pct.group(1) if pct else 'r'
        n = years.group(1) if years else 'n'
        return _three_lines(
            f'Em tính số tiền sau {n} năm khi gửi {p} triệu, lãi kép {r}%/năm.',
            r'Thầy hỏi em: em đổi phần trăm sang số thập phân rồi thay vào $A=P(1+r)^{n}$ thế nào?',
            'Em tự tính, thầy không ra số hộ.',
        )

    if 'xac suat' in text or 'xác suất' in low:
        return _three_lines(
            _short_stem_quote(stem, 110).rstrip('…') + '.',
            r'Thầy hỏi em: em đếm $n(\Omega)$ và $n(A)$ từ đúng số trong câu, rồi $P(A)=\dfrac{n(A)}{n(\Omega)}$ ra sao?',
            'Em tự tính, thầy không ra phân số hộ.',
        )

    if any(k in low for k in ('đồ thị của hàm số nào', 'đường cong dưới đây', 'là của hàm số nào')):
        return _three_lines(
            'Em đang xem đường cong này là đồ thị của hàm nào.',
            'Thầy hỏi em: tiệm cận đứng đọc ở đâu trên hình, và thay $x=0$ thì giao trục tung ra sao?',
            'Em loại ý lệch hình, thầy không chọn hộ.',
        )

    if any(k in low for k in ('bảng biến thiên', 'bbt')):
        return _three_lines(
            "Em đọc đúng bảng biến thiên của câu này: dòng $x$, dấu $y'$ và mũi tên $y$.",
            "Khoảng $y'>0$ thì $y$ tăng; $y'<0$ thì $y$ giảm — em đang hỏi khoảng nào hay cực trị?",
            'Em tự kết từ đúng dòng bảng, thầy không chốt hộ.',
        )

    if q.get('mslgn_data') or any(k in low for k in ('ghép nhóm', 'tứ phân vị', 'trung vị', 'mốt')):
        return _three_lines(
            'Em đang tìm số đặc trưng trên đúng bảng tần số ghép nhóm của câu này.',
            r'Thầy hỏi em: em cộng cột tần số ra $n$, rồi nhóm chứa vị trí cần tìm là nhóm nào trước khi thay vào công thức trung vị?',
            'Em tự tính, thầy không ra số hộ.',
        )

    if q.get('stmts'):
        return _three_lines(
            'Em xét từng ý đúng/sai, mỗi ý một điều kiện lấy từ giả thiết chung của câu.',
            'Thầy hỏi em: ý em đang làm dựa vào dữ kiện nào, và em ghi Đúng hay Sai độc lập với ý bên cạnh thế nào?',
            'Em tự ghi, thầy không chốt hộ.',
        )

    if 'benzene' in text or 'benzen' in text:
        return _three_lines(
            'Em đang xét phản ứng của benzene, vòng thơm.',
            'Thầy hỏi em: benzene ưu tiên phản ứng thế hay cộng như anken, và điều kiện xúc tác em nhớ là gì?',
            'Ý nào trái điều đó thì lệch — em tự chỉ ra, thầy không chốt hộ.' if negation else
            'Em đối chiếu từng ý với điều vừa nhớ, thầy không chốt hộ.',
        )

    if subj == 'Địa lý' and any(k in text for k in ('dong bang song cuu long', 'dbscl', 'cuu long')):
        return _three_lines(
            'Em đang nhận định về Đồng bằng sông Cửu Long.',
            'Thầy hỏi em: vùng này địa hình và sông ngòi, khí hậu ra sao so với trung du miền núi?',
            'Em giữ ý khớp đặc trưng vùng, thầy không chọn hộ.',
        )

    if subj == 'Ngữ văn' or any(k in text for k in ('cam nhan', 'doan van sau')):
        return _three_lines(
            f'Em đọc đúng đoạn trong câu rồi nói cảm nhận về {topic}.',
            'Thầy hỏi em: từ ngữ trong đoạn gợi không khí nào — rộng, gần, khô hay ồn — và ý nào lệch câu chữ?',
            'Em tự chọn ý khớp đoạn, thầy không chốt hộ.',
        )

    if 'ester' in text or 'xa phong' in text:
        return _three_lines(
            "Em đang xét xà phòng hóa ester.",
            r'Thầy hỏi em: $RCOOR\'$ tác dụng với $NaOH$ cho muối và ancol nào?',
            'Em viết sản phẩm rồi tự đối chiếu, thầy không chốt hộ.',
        )

    if negation:
        return _three_lines(
            f'Em ơi, câu này tìm ý không đúng về {topic}.',
            f'Thầy hỏi em: em còn nhớ quy luật cốt lõi của {topic} trong SGK {subj} không?',
            'Ý nào trái quy luật đó thì em giữ lại, thầy không chốt hộ.',
        )

    if expr != 'hàm trong câu' and subj == 'Toán học':
        return _three_lines(
            f'Em làm trên đúng {expr} trong câu này.',
            'Thầy hỏi em: công thức nào khớp yêu cầu, và em thay hệ số của hàm này vào trước khi tính thế nào?',
            'Em tự tính rồi đối chiếu, thầy không ra kết quả hộ.',
        )

    return _three_lines(
        f'Em xem câu đang hỏi về {topic}.',
        f'Thầy hỏi em: quy luật hay công thức nào của môn {subj} áp vào đúng chỗ này?',
        'Em nhớ ra rồi tự chốt, thầy không chọn hộ.',
    )


def build_tram3_socratic_guide(question, subject='Toán học', grade_num=12) -> str:
    """HD Socratic Trạm 1 và 3: 1–2 câu thầy hỏi, tối đa 3 dòng. Không lộ đáp, không lấy explain."""
    q = question if isinstance(question, dict) else {}
    if 'q' not in q and q.get('question'):
        q = dict(q)
        q['q'] = q.get('question')
    if 'opt' not in q and q.get('options') is not None:
        q = dict(q)
        q['opt'] = q.get('options')
    opts = q.get('opt') or []
    body = _plain_midwife(q, subject)
    body = _SOLUTION_LEAK.sub('', body)
    stem = str(q.get('q') or '')
    ans = str(q.get('ans') or q.get('correct') or '').strip()
    if ans and len(ans) <= 3 and re.fullmatch(r'[A-Da-d]', ans):
        body = re.sub(rf'(?i)\bđáp án\s*{ans}\b', '', body)
    for o in opts or []:
        piece = re.sub(r'^[A-D][.):]\s*', '', str(o), flags=re.I).strip()
        if len(piece) > 8 and piece in body and piece not in stem:
            body = body.replace(piece, '')
    for banned in ('Ngữ liệu', 'ngữ liệu', 'Việc 1', 'Việc 2', 'Việc 3', 'Trích xuất dữ kiện', 'Đề cho', 'đề cho'):
        body = body.replace(banned, '')
    body = re.sub(r'[ \t]{2,}', ' ', body)
    body = re.sub(r'\n{2,}', '\n', body).strip()
    lines = [ln.strip() for ln in body.splitlines() if ln.strip()][:3]
    return '\n'.join(lines)


# Alias toàn hệ thống (Trạm 1 + Trạm 3).
build_socratic_guide = build_tram3_socratic_guide
