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
        stems = [without_metadata(re.split(r'(?im)^\s*\*{0,2}A[.:)]', block, maxsplit=1)[0])
                 for _, block in question_blocks(quiz)]
        parts = [theory, *stems, *essay_stems(text)]
    except LessonContractError:
        parts = [str(text)]
    for part in parts:
        check_requested_scope(part, subject, grade, [topic])
    return text


def check_exam_question_scope(question, subject, grade, topics=(), custom=''):
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
