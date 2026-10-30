"""Bounded proofs of specific contradictions; no answer rewriting or certification."""
import re

import sympy as sp

from qa_runtime import parse_math_expression
from services.academic_context import canonical_subject, folded


def _rational_interval_choice_conflict(question):
    """Exact signs on explicit intervals for a numeric linear fraction only."""
    raw = str(question.get('q', ''))
    formula = re.search(r'\by\s*=\s*\\frac\{([^{}]+)\}\{([^{}]+)\}', raw)
    options = question.get('opt')
    if not formula or not isinstance(options, list) or len(options) != 4:
        return ''
    stem = folded(raw[:formula.start()] + ' FORMULA ' + raw[formula.end():])
    match = re.fullmatch(r'ham so formula (dong bien|nghich bien) tren khoang nao (?:duoi day|sau day)', stem)
    if not match:
        return ''
    x = sp.Symbol('x', real=True)
    try:
        polynomials = []
        for text in formula.groups():
            if len(text) > 80 or not re.fullmatch(r'[0-9x+\-*/().\s]+', text):
                return ''
            text = re.sub(r'(?<=[0-9x)])(?=[x(])', '*', text)
            value = parse_math_expression(text)
            if value.free_symbols - {x} or not value.is_polynomial(x) or sp.degree(value, x) > 1:
                return ''
            polynomials.append(sp.expand(value))
        numerator, denominator = polynomials
        a, b = numerator.coeff(x), numerator.subs(x, 0)
        c, d = denominator.coeff(x), denominator.subs(x, 0)
        determinant = sp.simplify(a*d-b*c)
        if c == 0 or determinant == 0:
            return ''
        pole = -d/c
        sign_matches = bool(determinant > 0 if match[1] == 'dong bien' else determinant < 0)
        truths = []
        def bound(text):
            text = text.strip()
            if text in (r'\infty', r'+\infty', '∞', '+∞'):
                return sp.oo
            if text in (r'-\infty', '-∞'):
                return -sp.oo
            if len(text) > 20 or not re.fullmatch(r'[+\-]?\d+(?:\.\d+|/\d+)?', text):
                raise ValueError('Unknown interval bound')
            return sp.Rational(text)
        for option in options:
            value = re.sub(r'^[A-D][.)]\s*', '', str(option).strip(), flags=re.I)
            value = value.replace('$', '').replace(r'\left', '').replace(r'\right', '').strip().rstrip('.')
            domain = re.sub(r'\\(?:mathbb|mathbf)\s*\{R\}', 'R', value)
            domain = domain.replace(r'\setminus', '\\').replace(r'\{', '{').replace(r'\}', '}').replace(' ', '')
            if domain.startswith('R\\{') and domain.endswith('}'):
                bound(domain[3:-1])  # Only a known single excluded real point.
                truths.append(False)  # Across a nonremovable pole global monotonicity fails.
                continue
            chunks = re.split(r'\s+và\s+', value)
            if not 1 <= len(chunks) <= 2:
                return ''
            interval_truths = []
            for chunk in chunks:
                interval = re.fullmatch(r'\(\s*([^;]+)\s*;\s*([^;]+)\s*\)', chunk.strip())
                if not interval:
                    return ''
                lower, upper = map(bound, interval.groups())
                if not lower < upper:
                    return ''
                interval_truths.append(sign_matches and not bool(lower < pole < upper))
            truths.append(all(interval_truths))
        if sum(truths) != 1:
            return 'rational_interval_choice_not_unique'
    except (ValueError, TypeError, NotImplementedError, ZeroDivisionError):
        return ''
    return ''


def _unbounded_integer_parameter_count(raw, text):
    """Prove an unrestricted cubic no-extrema parameter count is infinite."""
    if not re.search(r'bao nhieu gia tri nguyen\b', text):
        return ''
    prefix, separator, _ = text.partition('de ham so')
    if not separator or not re.fullmatch(r'(?:co )?bao nhieu gia tri nguyen cua (?:tham so )?m', prefix.strip()):
        return ''  # Unknown qualifiers may bound the integer parameter.
    match = re.search(r'khong co (?:diem )?cuc tri', text)
    if not match or text[match.end():].strip():
        return ''
    if (re.search(r'\bm\s*(?:\\in\b|∈|[<>≤≥=])', raw)
            or any(t in text for t in ('nguyen duong', 'nguyen am', 'm thuoc',
                                        'm duong', 'm am', 'trong doan', 'trong khoang'))):
        return ''
    expressions = list(re.finditer(r'(?:\by|\bf\s*\(\s*x\s*\))\s*=\s*([^$\n;]+)', raw))
    for expression_match in expressions[:3]:
        if not re.fullmatch(r'khong co (?:diem )?cuc tri', folded(raw[expression_match.end():])):
            continue
        expression = expression_match.group(1)
        expression = re.sub(r'^f\s*\(\s*x\s*\)\s*=\s*', '', expression).strip()
        expression = re.sub(r'\\frac\s*\{\s*([+-]?\d+)\s*\}\s*\{\s*(\d+)\s*\}', r'(\1/\2)', expression)
        if len(expression) > 160 or not re.fullmatch(r'[0-9xm+\-*/^().{}\s]+', expression):
            continue
        value = expression.replace('m', 't').replace('^', '**').replace('{', '(').replace('}', ')')
        value = re.sub(r'(?<=[0-9xt)])(?=[xt(])', '*', value)
        try:
            polynomial = parse_math_expression(value)
            x, t = sp.symbols('x t', real=True)
            if not polynomial.is_polynomial(x, t) or sp.degree(polynomial, x) != 3:
                continue
            a, b, c, d = [sp.expand(polynomial).coeff(x, i) for i in (3, 2, 1, 0)]
            if any(v.free_symbols for v in (a, b, d)) or a == 0 or sp.degree(c, t) != 1:
                continue
            # Derivative discriminant <=0 is a nonempty half-line in m.
            # Either direction contains infinitely many unrestricted integers.
            slope = sp.diff(4*b*b - 12*a*c, t)
            if not slope.free_symbols and slope != 0:
                return 'unbounded_integer_parameter_count'
        except (ValueError, TypeError, NotImplementedError, ZeroDivisionError):
            continue
    return ''


def math_condition_conflict(question):
    if not isinstance(question, dict):
        return ""
    if question.get('subject') and canonical_subject(question['subject']) != 'Toán học':
        return ""
    raw = str(question.get('q', ''))
    if len(raw) > 10000:
        return ""
    text = folded(raw)
    rational_issue = _rational_interval_choice_conflict(question)
    if rational_issue:
        return rational_issue
    count_issue = _unbounded_integer_parameter_count(raw, text)
    if count_issue:
        answer = str(question.get('ans', '')).strip()
        options = question.get('opt')
        if isinstance(options, list) and answer.upper() in ('A', 'B', 'C', 'D'):
            index = ord(answer.upper()) - ord('A')
            if index < len(options):
                answer = str(options[index])
        answer_text = folded(answer)
        if re.search(r'\b(?:vo han|infty|infinite|infinity)\b', answer_text) and 'khong' not in answer_text:
            return ''  # Infinite counts are valid when the answer contract says so.
        return count_issue
    from services.polynomial_choice_contract import polynomial_choice_conflict
    choice_issue = polynomial_choice_conflict(question)
    if choice_issue:
        return choice_issue
    from services.parameter_interval_contract import interval_code_conflict
    interval_issue = interval_code_conflict(question)
    if interval_issue:
        return interval_issue
    # Read four asserted curve points, not unrelated points later in the question.
    four_points = re.search(r'đi\s+qua\s+(?:bốn|4)\s+điểm', raw, re.I)
    if re.search(r'\bcho ham so bac (?:ba|3)\b', text) and four_points and 'khong di qua' not in text:
        number = r'[+-]?\d{1,6}(?:[.,]\d{1,6})?'
        pairs = re.findall(r'\b[A-Z]\s*\(\s*(' + number + r')\s*;\s*(' + number + r')\s*\)', raw[four_points.end():])[:4]
        if len(pairs) == 4:
            points = [(sp.Rational(a.replace(',', '.')), sp.Rational(b.replace(',', '.'))) for a,b in pairs]
            by_x = {}
            for a,b in points:
                if a in by_x and by_x[a] != b:
                    return 'contradictory_points'
                by_x[a] = b
            if len(by_x) >= 4:
                x = sp.Symbol('x', real=True)
                polynomial = sp.interpolate(list(by_x.items()), x)
                if sp.degree(polynomial, x) != 3:
                    return 'asserted_cubic_inconsistent_with_points'

    if 'khong co cuc tri' not in text:
        return ""
    tail = text.split('khong co cuc tri', 1)[1].strip()
    if tail and not re.fullmatch(r'neu ket qua la mot khoang hoac doan hay nhap (?:gia tri )?bien (?:lon|nho) nhat cua m thoa man dieu kien do', tail):
        return ""
    if 'tren' in text and not any(term in text for term in ('tren r', 'tren mathbb r')):
        return ""
    upper = 'bien lon nhat cua m' in text or 'gia tri lon nhat cua m' in text
    lower = 'bien nho nhat cua m' in text or 'gia tri nho nhat cua m' in text
    if not (upper or lower):
        return ""
    # Additional parameter restrictions require their own interpretation.
    if any(term in text for term in ('so nguyen', 'so tu nhien', 'm thuoc', 'm duong', 'm am')):
        return ""
    if re.search(r'\bm\s*(?:\\in\b|∈|[<>≤≥=])', raw):
        return ""
    expressions = re.findall(r'(?:\by|\bf\s*\(\s*x\s*\))\s*=\s*([^$\n;]+)', raw)
    for expression in expressions[:3]:
        expression = re.sub(r'^f\s*\(\s*x\s*\)\s*=\s*', '', expression).strip()
        if len(expression) > 160 or not re.fullmatch(r'[0-9xm+\-*/^().{}\s]+', expression):
            continue
        value = expression.replace('m', 't').replace('^', '**').replace('{','(').replace('}',')')
        value = re.sub(r'(?<=[0-9xt)])(?=[xt(])', '*', value)
        try:
            polynomial = parse_math_expression(value)
            x,t = sp.symbols('x t', real=True)
            if not polynomial.is_polynomial(x,t) or sp.degree(polynomial,x) != 3:
                continue
            a,b,c,d = [sp.expand(polynomial).coeff(x,i) for i in (3,2,1,0)]
            if any(v.free_symbols for v in (a,b,d)) or a == 0 or sp.degree(c,t) != 1:
                continue
            slope = sp.diff(4*b*b-12*a*c,t)
            if slope.free_symbols or slope == 0:
                continue
            # No extrema iff discriminant <=0; a nonconstant linear inequality
            # is a half-line. A negative slope is unbounded above, and vice versa.
            if (upper and slope < 0) or (lower and slope > 0):
                return 'requested_parameter_boundary_does_not_exist'
        except (ValueError, TypeError, NotImplementedError, ZeroDivisionError):
            continue
    return ""
