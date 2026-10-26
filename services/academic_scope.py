"""Narrow, sourced scope checks; never a certificate for all AI knowledge."""
import re

from services.academic_context import academic_context, folded


class AcademicScopeError(ValueError):
    pass


MATH12_SURVEY_SOURCE = {
    'document': 'Chương trình môn Toán kèm TT 32/2018/TT-BGDĐT',
    'page': 106,
    'url': 'https://fileth.hcm.shieldix.app/data/hcmedu/thlevanthogv/attachments/2020_5/3cttoan18201918_295202014.pdf',
    'checked_at': '2026-10-26',
    'scope': 'Khảo sát và vẽ đồ thị cơ bản lớp 12',
    'forms': ['cubic', 'linear_over_linear', 'quadratic_over_linear'],
    'note': 'Bản văn bản của Bộ lưu tại trường; không xác nhận mọi bài/trang KNTT hoặc mọi nội dung AI.'}


def academic_scope_instruction(subject, grade, topic=''):
    subject, grade = academic_context(subject, grade)
    context = folded(topic)
    if subject != 'Toán học' or grade != 12 or not any(value in context for value in ('khao sat', 've do thi', 'ham bac ba', 'ham bac 3')):
        return ''
    return ('Phạm vi khảo sát và vẽ đồ thị cơ bản Toán 12, CT môn Toán kèm TT 32/2018, trang 106: '
            'hàm bậc ba, phân thức bậc nhất/bậc nhất và bậc hai/bậc nhất, kèm điều kiện hệ số. '
            'Nếu người dùng chọn riêng hàm bậc ba thì không đổi sang khảo sát bậc bốn/trùng phương. '
            'Quy tắc này không cấm biểu thức bậc bốn trong nội dung nguyên hàm/tích phân hoặc mọi ngữ cảnh khác. '
            'Nguồn văn bản: ' + MATH12_SURVEY_SOURCE['url'] + '. Không tự nhận đã đối chiếu từng trang KNTT.')


def three_basic_survey_instruction(subject, grade, topic):
    """Lesson-only coverage guidance; never inject lesson layout into exams."""
    coverage = ''
    if three_basic_survey_requested(subject, grade, topic):
        coverage = (
            '\nYêu cầu người dùng là CẢ BA DẠNG: phần lý thuyết phải có ba mục phân biệt, '
            'mỗi mục có dạng tổng quát, điều kiện hệ số và một ví dụ số cụ thể được khảo sát; '
            'không chỉ liệt kê tên hoặc dồn các dạng còn thiếu xuống bài tập tự làm. '
            'Ba dạng là bậc ba (hệ số bậc ba khác 0), phân thức 1/1 '
            '(mẫu có bậc 1, định thức khác 0), phân thức 2/1 '
            '(tử bậc 2, mẫu bậc 1, tử không chia hết cho mẫu). '
            'Mỗi ví dụ cần tập xác định, đạo hàm/xét dấu, đơn điệu/cực trị, '
            'giới hạn/tiệm cận nếu có, BBT và dữ kiện vẽ đồ thị nhất quán. '
            'Ví dụ có lời giải chỉ ở Phần 1; giữ đúng ba MCQ và hai tự luận gợi mở ở Phần 2–3. '
            'Nguồn đã mở: Toán 12 tập một KNTT, Bài 4, trang 26–28 trên cổng NXBGD '
            'https://truonghocsoquocgia.nxbgd.vn/book/393beba7-0dc1-45a9-ac53-3254cffa1344/read '
            '(đối chiếu ngày 27/10/2026; không suy ngày tạo trang thành năm tái bản). '
            'Đây là tóm tắt phạm vi đã đối chiếu, không phải toàn văn SGK/SGV hoặc chứng nhận mọi ví dụ.')
    return coverage


def three_basic_survey_requested(subject, grade, topic):
    """Only an explicit all-three request activates the coverage check."""
    subject, grade = academic_context(subject, grade)
    context = folded(topic)
    return subject == 'Toán học' and grade == 12 and 'khao sat' in context and bool(
        re.search(r'\b(?:ba|3)\s+(?:dang\s+)?ham(?:\s+so)?\s+co\s+ban\b', context)
        or re.search(r'\b(?:ca\s+)?(?:ba|3)\s+dang\s+ham\b', context))


def check_three_basic_survey_coverage(theory, subject, grade, topic):
    """Check numeric example presence, not the truth of every worked step.

    Existing bounded parser is reused. Restrict candidate size/alphabet before
    symbolic parsing; never solve or repair coefficients here.
    """
    if not three_basic_survey_requested(subject, grade, topic):
        return theory
    from services.math_publication import segments
    from services.neuro_symbolic_verifier import clean_latex_math_to_sympy_expr, x
    import sympy as sp
    found = set()
    for _, _, formula, _ in segments(str(theory)):
        formula = re.sub(r"\by\s*=\s*f\s*\(\s*x\s*\)\s*=", 'y=', formula)
        for match in re.finditer(r"(?<![\w'])\b(?:y|f\s*\(\s*x\s*\))\s*=\s*([^=;\n]+)", formula):
            candidate = re.split(r'\\(?:quad|qquad|text)\b', match[1])[0].strip().rstrip('.,')
            candidate = candidate.translate(str.maketrans({'²': '^2', '³': '^3', '−': '-'}))
            candidate = re.sub(r'\\(?:left|right)\b', '', candidate).replace(r'\tfrac', r'\frac')
            if len(candidate) > 120 or re.search(r'\d{7,}', candidate):
                continue
            numeric = re.sub(r'\\(?:dfrac|frac|tfrac|left|right)', '', candidate)
            if not re.fullmatch(r'[0-9x.\s+*/^(){}\-]+', numeric):
                continue
            powers = re.findall(r'\^\s*\{?(\d+)', candidate)
            if any(int(power) > 3 for power in powers):
                continue
            expr = clean_latex_math_to_sympy_expr(candidate)
            if expr is None or expr.free_symbols - {x} or not expr.is_rational_function(x):
                continue
            numerator, denominator = sp.fraction(sp.cancel(expr))
            degrees = (sp.degree(numerator, x), sp.degree(denominator, x))
            if degrees == (3, 0):
                found.add('bậc ba')
            elif degrees == (1, 1):
                found.add('phân thức 1/1')
            elif degrees == (2, 1):
                found.add('phân thức 2/1')
    missing = sorted({'bậc ba', 'phân thức 1/1', 'phân thức 2/1'} - found)
    if missing:
        raise AcademicScopeError('Yêu cầu khảo sát cả ba dạng nhưng PHẦN 1 thiếu ví dụ số tường minh: '
                                 + ', '.join(missing) + '. Bổ sung đúng mục lý thuyết; không thay các bài tập tự làm.')
    return theory


def _numeric_polynomial_degree(expression):
    expression = re.sub(r'\s+', '', expression).replace('{', '').replace('}', '')
    if not re.fullmatch(r'[0-9x.+\-^]+', expression):
        return None
    coefficients = {}
    for term in re.findall(r'[+-]?[^+-]+', expression):
        match = re.fullmatch(r'([+-]?)(\d+(?:\.\d+)?)?x(?:\^(\d+))?', term)
        if match:
            sign, number, power = match.groups()
            power = int(power or 1)
            coefficients[power] = coefficients.get(power, 0) + (-1 if sign == '-' else 1) * float(number or 1)
        elif not re.fullmatch(r'[+-]?\d+(?:\.\d+)?', term):
            return None
    return max((power for power, coefficient in coefficients.items() if coefficient), default=0)


def check_requested_scope(text, subject, grade, topics=(), custom=''):
    subject, grade = academic_context(subject, grade)
    if subject != 'Toán học' or grade != 12:
        return text
    topics = [topics] if isinstance(topics, str) else list(topics)
    context = folded(' '.join(map(str, topics)) + ' ' + str(custom))
    explicit_cubic = bool(re.search(r'ham (?:so )?bac (?:ba|3)\b', context))
    basic_survey = any(value in context for value in ('khao sat', 've do thi'))
    # A combined exam also includes integrals, where x^4 may be legitimate.
    mixed = any(value in context for value in ('nguyen ham', 'tich phan'))
    forbidden_four = bool(re.search(r'(?:khong|cam|loai)\s+(?:ra\s+)?(?:cau\s+)?(?:ham\s+)?(?:so\s+)?bac\s+(?:bon|4)\b', context))
    if not ((explicit_cubic or basic_survey) and not mixed or forbidden_four):
        return text
    from services.math_publication import segments
    source = str(text).translate(str.maketrans({'²': '^2', '³': '^3', '⁴': '^4'}))
    formulas = [formula for _, _, formula, _ in segments(source)]
    # Also check plain-text definitions. Keep derivative y'/f'(x) and primitive
    # F(x) distinct from the function being selected for survey.
    formulas.extend(line for line in source.splitlines() if '$' not in line and '\\(' not in line)
    for formula in formulas:
        for match in re.finditer(r"(?<![\w'])\b(?:y|[fgh]\s*\(\s*x\s*\))\s*=\s*([^;$\n]+)", formula):
            expression = re.split(r'\\(?:quad|qquad|text)\b', match[1])[0].strip().rstrip('.,')
            degree = _numeric_polynomial_degree(expression)
            if degree is None:
                powers = [int(power) for power in re.findall(r'x\s*\^\s*\{?(\d+)\}?', expression)]
                degree = max(powers, default=0)
            if degree >= 4:
                raise AcademicScopeError(
                    'Hàm số bậc từ 4 đang được đưa vào phạm vi khảo sát cơ bản/bậc ba đã chọn. '
                    'Cần biên soạn lại toàn câu và đối chiếu khóa chấm, giữ đúng môn/lớp/chủ đề; '
                    'không thay riêng số mũ hoặc đáp án. Căn cứ phạm vi khảo sát: CT môn Toán, trang 106.')
    return text


def check_lesson_scope(text, subject, grade, topic):
    from services.lesson_contract import lesson_sections, question_blocks, without_metadata, essay_stems, LessonContractError
    try:
        theory, quiz, _ = lesson_sections(text)
        check_three_basic_survey_coverage(theory, subject, grade, topic)
        stems = [without_metadata(re.split(r'(?im)^\s*\*{0,2}A[.:)]', block, maxsplit=1)[0])
                 for _, block in question_blocks(quiz)]
        parts = [theory, *stems, *essay_stems(text)]
    except LessonContractError:
        parts = [str(text)]
    for part in parts:
        check_requested_scope(part, subject, grade, [topic])
    return text


def check_topic_content_consistency(question, subject):
    """Reject one evidenced metadata conflict, not a general semantic classifier.

    A statistical survey ('khảo sát thời gian') is not a function survey. Require
    an explicit grouped-statistics task and a conflicting function-only label;
    preserve integrated questions that actually ask about functions/derivatives.
    """
    from services.academic_context import canonical_subject
    if canonical_subject(subject) != 'Toán học':
        return question
    declared = folded(question.get('topic', ''))
    stem = folded(question.get('q', ''))
    function_label = any(term in declared for term in ('ham so', 'dao ham', 'tiem can', 'don dieu'))
    statistics_label = any(term in declared for term in ('ghep nhom', 'thong ke', 'phan tan', 'mau so lieu'))
    grouped_task = ('ghep nhom' in stem or bool(question.get('mslgn_data'))) and any(
        term in stem for term in ('khoang bien thien', 'tu phan vi', 'phuong sai', 'do lech chuan', 'trung vi', 'tan so'))
    function_task = any(term in stem for term in ('ham so', 'dao ham', 'tiem can', 'dong bien', 'nghich bien', 'cuc tri'))
    if function_label and not statistics_label and grouped_task and not function_task:
        raise AcademicScopeError('Nhãn khảo sát hàm số mâu thuẫn với câu hỏi thống kê mẫu ghép nhóm. '
                                 'Cần chọn hoặc biên soạn lại toàn câu đúng chủ đề; không chỉ đổi nhãn hay đáp án.')
    return question


def check_exam_question_scope(question, subject, grade, topics=(), custom=''):
    check_topic_content_consistency(question, subject)
    selected = [topics] if isinstance(topics, str) else list(topics)
    # For a mixed-topic exam, use the item's stated topic if it matches one of
    # the selected topics; final context validation remains a separate gate.
    from services.academic_context import topic_matches
    declared = question.get('topic', '')
    if len(selected) > 1 and declared:
        matched = [topic for topic in selected if topic_matches(topic, declared)]
        if matched:
            selected = matched
    check_requested_scope(question.get('q', ''), subject, grade, selected, custom)
    for statement in question.get('stmts', []):
        if isinstance(statement, dict):
            check_requested_scope(statement.get('t', ''), subject, grade, selected, custom)
    return question
