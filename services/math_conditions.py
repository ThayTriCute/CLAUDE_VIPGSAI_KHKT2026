"""Bounded proofs of specific contradictions; no answer rewriting or certification."""
import re

import sympy as sp

from qa_runtime import parse_math_expression
from services.academic_context import canonical_subject, folded


def math_condition_conflict(question):
    if not isinstance(question, dict):
        return ""
    if question.get('subject') and canonical_subject(question['subject']) != 'Toán học':
        return ""
    raw = str(question.get('q', ''))
    if len(raw) > 10000:
        return ""
    text = folded(raw)
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
