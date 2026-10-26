"""Bounded independent check: numeric cubic polynomials and four open intervals.

Unknown tasks/formats remain unverified. Never rewrite questions or answer keys.
"""
import math
import re

from services.academic_context import folded


def audit_monotonic_options(question):
    unknown = {'verified': False, 'hallucination_detected': False}
    stem = folded(question.get('q', ''))
    increasing = 'dong bien tren khoang' in stem
    decreasing = 'nghich bien tren khoang' in stem
    if increasing == decreasing or any(t in stem for t in ('khong dong bien', 'khong nghich bien', 'dao ham')) or re.search(r"[fgy]\s*['′]", str(question.get('q', ''))):
        return unknown
    options = question.get('opt', [])
    if len(options) != 4:
        return unknown
    import sympy as sp
    from services.neuro_symbolic_verifier import clean_latex_math_to_sympy_expr, x
    model = question.get('f')
    try:
        if isinstance(model, dict) and model.get('type') in {'func_3', 'cubic'}:
            if not all(k in model and math.isfinite(float(model[k])) and abs(float(model[k])) <= 1000000 for k in 'abcd'):
                return unknown
            a, b, c, d = [sp.Rational(str(model[k])) for k in 'abcd']
            expression = a*x**3 + b*x**2 + c*x + d
        else:
            match = re.search(r'(?:\by|\bf\(x\))\s*=\s*([^$;\n]+)', str(question.get('q', '')))
            if not match or len(match[1]) > 300:
                return unknown
            expression = clean_latex_math_to_sympy_expr(match[1])
        if expression is None or expression.free_symbols - {x} or not expression.is_polynomial(x) or sp.degree(expression, x) > 3:
            return unknown
        if not all(math.isfinite(float(c)) and abs(float(c)) <= 1000000 for c in sp.Poly(expression, x).all_coeffs()):
            return unknown
        explicit = re.search(r'(?:\by|\bf\(x\))\s*=\s*([^$;\n]+)', str(question.get('q', '')))
        if isinstance(model, dict) and explicit and len(explicit[1]) <= 300:
            stated = clean_latex_math_to_sympy_expr(explicit[1])
            if stated is not None and not stated.free_symbols - {x} and stated.is_polynomial(x) and sp.expand(stated-expression) != 0:
                return {'verified': False, 'hallucination_detected': True, 'reason': 'function_model_formula_conflict'}
        derivative = sp.diff(expression, x)
        roots = sorted([r for r in sp.solve(derivative, x) if r.is_real], key=float) if derivative != 0 else []
        endpoint = r'[+-]?(?:\d+(?:\.\d+)?(?:/\d+)?|inf)'
        pattern = re.compile(r'\(\s*(' + endpoint + r')\s*[;,]\s*(' + endpoint + r')\s*\)\.?')
        def value(text):
            if text in {'inf', '+inf'}:
                return sp.oo
            if text == '-inf':
                return -sp.oo
            return sp.Rational(text)
        answers = []
        for index, option in enumerate(options):
            if len(str(option)) > 100:
                return unknown
            text = re.sub(r'^[A-D][.)]\s*', '', str(option).strip(), flags=re.I)
            text = text.replace('$', '').replace(r'\left', '').replace(r'\right', '').replace(r'\infty', 'inf').replace('∞', 'inf').replace('−', '-')
            match = pattern.fullmatch(text.strip())
            if not match:
                return unknown  # All four options must be independently understood.
            left, right = map(value, match.groups())
            if not left < right:
                return unknown
            cuts = [left] + [r for r in roots if left < r < right] + [right]
            signs = []
            for low, high in zip(cuts, cuts[1:]):
                sample = (low+high)/2 if low != -sp.oo and high != sp.oo else high-1 if low == -sp.oo and high != sp.oo else low+1 if low != -sp.oo else sp.Integer(0)
                signs.append(sp.sign(derivative.subs(x, sample)))
            if signs and all(sign == (1 if increasing else -1) for sign in signs):
                answers.append('ABCD'[index])
        key = str(question.get('ans', '')).strip().upper()
        if key not in 'ABCD' or len(key) != 1:
            return unknown
        mismatch = len(answers) != 1 or key != answers[0]
        return {'verified': not mismatch, 'hallucination_detected': mismatch,
                'valid_options': answers, 'scope': 'numeric polynomial degree <=3, open numeric intervals'}
    except (ValueError, TypeError, ZeroDivisionError, NotImplementedError):
        return unknown
