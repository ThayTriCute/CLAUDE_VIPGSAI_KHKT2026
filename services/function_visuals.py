"""Offline, deterministic visuals for one explicitly specified rational function."""
import ast
import html
import math
import re
from functools import lru_cache

import sympy as sp

X = sp.Symbol('x', real=True)


class NonStandardFunction(ValueError):
    """Outside the three non-degenerate function families selected for this lesson."""


def parse_function(source, strict=False):
    """Restricted arithmetic, never eval/sympify generated text. Keep original holes."""
    if len(source) > 180:
        raise ValueError('Expression too long')
    source = source.replace('\\left', '').replace('\\right', '').replace('\\cdot', '*').replace('\\times', '*')
    source = re.sub(r'\^\{([0-3])\}', r'^\1', source)
    for _ in range(4):
        source = re.sub(r'\\(?:dfrac|frac)\{([^{}]+)\}\{([^{}]+)\}', r'((\1)/(\2))', source)
    source = re.sub(r'(?<=\d)(?=x)|(?<=\))(?=[x(])|(?<=x)(?=\()', '*', source)
    tree = ast.parse(source.replace('^', '**'), mode='eval')
    if len(list(ast.walk(tree))) > 90:
        raise ValueError('Expression too complex')
    excluded = set()

    def visit(node):
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            if not math.isfinite(node.value) or abs(node.value) > 10**9:
                raise ValueError('Coefficient out of range')
            return sp.Rational(str(node.value))
        if isinstance(node, ast.Name) and node.id == 'x':
            return X
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
            value = visit(node.operand)
            return -value if isinstance(node.op, ast.USub) else value
        if isinstance(node, ast.BinOp):
            left, right = visit(node.left), visit(node.right)
            if isinstance(node.op, ast.Add):
                return left + right
            if isinstance(node.op, ast.Sub):
                return left - right
            if isinstance(node.op, ast.Mult):
                return left * right
            if isinstance(node.op, ast.Pow) and right.is_Integer and 0 <= right <= 3:
                return left ** right
            if isinstance(node.op, ast.Div):
                if right == 0:
                    raise ValueError('Zero denominator')
                numerator, denominator = sp.fraction(sp.cancel(right))
                if X in denominator.free_symbols or sp.degree(numerator, X) > 1:
                    raise ValueError('Only linear denominators supported')
                excluded.update(sp.solve(numerator, X))
                return left / right
        raise ValueError('Unsupported expression')

    original = visit(tree.body)
    expression = sp.cancel(original)
    numerator, denominator = sp.fraction(expression)
    if sp.degree(denominator, X) > 1 or sp.degree(numerator, X) > (2 if X in denominator.free_symbols else 3):
        raise ValueError('Unsupported function family')
    if len(excluded) > 1:
        raise ValueError('Multiple excluded points')
    if strict:
        degree_n, degree_d = sp.degree(numerator, X), sp.degree(denominator, X)
        if excluded:
            # A remaining pole is required: cancellation would turn it into a
            # different function with a removable hole, not the SGK family.
            if degree_d != 1 or degree_n not in (0, 1, 2):
                raise NonStandardFunction('Cancelled denominator')
        elif degree_d != 0 or degree_n != 3:
            raise NonStandardFunction('Not a cubic or a non-degenerate rational function')
    return expression, tuple(sorted(excluded, key=float))


def function_model(source, strict=False):
    expression, excluded = parse_function(source, strict=strict)
    derivative = sp.factor(sp.diff(expression, X))
    stationary = [] if derivative == 0 else [r for r in sp.solve(derivative, X) if r.is_real and r not in excluded]
    points = [-sp.oo] + sorted(set(stationary) | set(excluded), key=float) + [sp.oo]
    signs = []
    for left, right in zip(points, points[1:]):
        sample = right - 1 if left == -sp.oo else left + 1 if right == sp.oo else (left + right) / 2
        signs.append(int(sp.sign(derivative.subs(X, sample))))
    limits = []
    for point in points:
        if point in excluded:
            limits.append((sp.limit(expression, X, point, dir='-'), sp.limit(expression, X, point, dir='+')))
        else:
            value = sp.limit(expression, X, point, dir='+' if point == -sp.oo else '-')
            limits.append((value, value))
    return dict(expression=expression, derivative=derivative, excluded=excluded,
                stationary=stationary, points=points, signs=signs, limits=limits)


def _text(value):
    return str(value).replace('-oo', '−∞').replace('oo', '+∞').replace('sqrt', '√').replace('**', '^').replace('*', '·').replace('-', '−')


def _svg(width, height, label, content):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" '
            f'aria-label="{html.escape(label, quote=True)}" style="width:100%;height:auto;display:block;background:white;color:#111;font:18px Times New Roman,serif">'
            + content + '</svg>')


def _label(x, y, text, size=18):
    return f'<text x="{x:.3f}" y="{y:.3f}" text-anchor="middle" dominant-baseline="middle" fill="#111" font-size="{size}">{html.escape(str(text))}</text>'


def _line(x1, y1, x2, y2, dashed=False):
    return f'<line x1="{x1:.3f}" y1="{y1:.3f}" x2="{x2:.3f}" y2="{y2:.3f}" stroke="#111" stroke-width="1.6"' + (' stroke-dasharray="6 5"' if dashed else '') + '/>'


def variation_svg(model):
    points, signs, limits = model['points'], model['signs'], model['limits']
    width = max(820, 180 * (len(points) - 1) + 120)
    xs = [140 + i * (width - 210) / (len(points) - 1) for i in range(len(points))]
    finite = [float(v) for pair in limits for v in pair if v.is_finite]
    low, high = min(finite or [0]), max(finite or [0])

    def level(value):
        if value == sp.oo:
            return 128
        if value == -sp.oo:
            return 236
        return 182 if high == low else 213 - 62 * (float(value) - low) / (high - low)

    body = f'<rect x="1" y="1" width="{width-2}" height="258" fill="white" stroke="#111" stroke-width="2"/>'
    body += _line(82, 1, 82, 259) + _line(1, 52, width-1, 52) + _line(1, 100, width-1, 100)
    body += _label(42, 28, 'x') + _label(42, 77, 'y′') + _label(42, 180, 'y')
    for i, point in enumerate(points):
        body += _label(xs[i], 28, _text(point))
        if point in model['excluded']:
            pole = any(v in (sp.oo, -sp.oo) for v in limits[i])
            body += _label(xs[i], 77, '∥' if pole else '×')
            for offset in (-3, 3) if pole else (0,):
                body += _line(xs[i]+offset, 101, xs[i]+offset, 258, dashed=not pole)
            for offset, value in zip((-28, 28), limits[i]):
                body += _label(xs[i]+offset, level(value), _text(value), 16)
        else:
            if point in model['stationary']:
                body += _label(xs[i], 77, '0')
            body += _label(xs[i], level(limits[i][0]), _text(limits[i][0]), 17)
    for i, sign in enumerate(signs):
        body += _label((xs[i]+xs[i+1])/2, 77, '+' if sign > 0 else '−' if sign < 0 else '0')
        x1, x2 = xs[i]+42, xs[i+1]-42
        y1, y2 = level(limits[i][1]), level(limits[i+1][0])
        body += _line(x1, y1, x2, y2)
        angle = math.atan2(y2-y1, x2-x1)
        body += '<path d="M %.3f %.3f L %.3f %.3f L %.3f %.3f" fill="none" stroke="#111" stroke-width="1.6"/>' % (x2-9*math.cos(angle-.45), y2-9*math.sin(angle-.45), x2, y2, x2-9*math.cos(angle+.45), y2-9*math.sin(angle+.45))
    return _svg(width, 260, 'Bảng biến thiên y=' + str(model['expression']), body)


def graph_svg(model):
    expression = model['expression']
    numerator, denominator = sp.fraction(expression)
    roots = sp.real_roots(numerator) if sp.degree(numerator, X) > 0 else []
    roots = [r for r in set(roots) if r not in model['excluded']]
    center = None
    if X in denominator.free_symbols:
        pole = model['excluded'][0]
        quotient = sp.div(numerator, denominator, X)[0]
        center = (pole, quotient.subs(X, pole))
    elif sp.degree(numerator, X) == 3:
        poly = sp.Poly(numerator, X)
        xc = -poly.nth(2) / (3*poly.nth(3))
        center = (xc, expression.subs(X, xc))
    landmarks = [float(v) for v in (*model['stationary'], *model['excluded'], *roots)]
    if center:
        landmarks.append(float(center[0]))
    low_x, high_x = min([0, *landmarks]), max([0, *landmarks])
    padding = max(1, (high_x-low_x)*.25)
    xmin, xmax = low_x-padding, high_x+padding
    if xmax-xmin > 100000:
        raise ValueError('Plot window out of range')
    function = sp.lambdify(X, expression, modules='math')
    cuts = [xmin] + [float(v) for v in model['excluded'] if xmin < float(v) < xmax] + [xmax]
    branches, values = [], []
    for left, right in zip(cuts, cuts[1:]):
        samples = []
        for i in range(401):
            x = left + (right-left) * (i+.25)/401
            try:
                y = float(function(x))
                if math.isfinite(y):
                    samples.append((x, y)); values.append(y)
            except (ZeroDivisionError, ValueError, OverflowError):
                pass
        for point in (*model['stationary'], *roots):
            xp = float(point)
            if left < xp < right:
                samples.append((xp, 0.0 if point in roots else float(expression.subs(X, point))))
        samples.sort(key=lambda pair: pair[0])
        branches.append(samples)
    values.sort()
    if not values:
        raise ValueError('No finite plot values')
    special = [float(expression.subs(X, p)) for p in model['stationary']]
    if center:
        special.append(float(center[1]))
    if 0 not in model['excluded']:
        special.append(float(expression.subs(X, 0)))
    if len(model['stationary']) == 2:
        # A textbook sketch must make the extrema readable, rather than flatten
        # them against axes because of large cubic values at the window edges.
        ymin, ymax = min([0, *special]), max([0, *special])
        margin = max(1, (ymax-ymin)*.4)
    else:
        ymin = min([0, values[len(values)//10], *special])
        ymax = max([0, values[9*len(values)//10], *special])
        margin = max(1, (ymax-ymin)*.12)
    ymin, ymax = ymin-margin, ymax+margin
    px = lambda x: 58 + (x-xmin)*690/(xmax-xmin)
    py = lambda y: 430 - (y-ymin)*390/(ymax-ymin)
    body = '<defs><clipPath id="function-plot-clip"><rect x="58" y="40" width="690" height="390"/></clipPath></defs>'
    body += _line(58, py(0), 765, py(0)) + _line(px(0), 440, px(0), 24)
    body += f'<path d="M 757 {py(0)-4:.3f} L 765 {py(0):.3f} L 757 {py(0)+4:.3f} M {px(0)-4:.3f} 32 L {px(0):.3f} 24 L {px(0)+4:.3f} 32" fill="none" stroke="#111" stroke-width="1.6"/>'
    body += _label(773, py(0), 'x') + _label(px(0), 14, 'y') + _label(px(0)-12, py(0)+15, 'O', 15)
    def ticks(lo, hi):
        raw = (hi-lo)/6
        base = 10**math.floor(math.log10(raw))
        step = next((factor*base for factor in (1, 2, 5, 10) if factor*base >= raw), 10*base)
        return [i*step for i in range(math.ceil(lo/step), math.floor(hi/step)+1)]

    for v in ticks(xmin, xmax):
        if abs(v) < 1e-12:
            continue
        body += _line(px(v), py(0)-3, px(v), py(0)+3) + _label(px(v), py(0)+18, f'{v:.3g}', 13)
    for v in ticks(ymin, ymax):
        if abs(v) < 1e-12:
            continue
        body += _line(px(0)-3, py(v), px(0)+3, py(v)) + _label(px(0)-25, py(v), f'{v:.3g}', 13)
    clipped = ''
    for branch in branches:
        coords = ' '.join(f'{px(x):.3f},{max(-10000,min(10000,py(y))):.3f}' for x,y in branch)
        clipped += f'<polyline points="{coords}" fill="none" stroke="#163e87" stroke-width="2"/>'
    asymptote = None
    if X in denominator.free_symbols:
        asymptote = sp.div(numerator, denominator, X)[0]
        clipped += _line(px(xmin), py(float(asymptote.subs(X,xmin))), px(xmax), py(float(asymptote.subs(X,xmax))), True)
    for p in model['excluded']:
        value = sp.limit(expression, X, p)
        if value in (sp.oo, -sp.oo):
            clipped += _line(px(float(p)), 40, px(float(p)), 430, True)
        else:
            clipped += f'<circle cx="{px(float(p)):.3f}" cy="{py(float(value)):.3f}" r="4" fill="white" stroke="#163e87" stroke-width="2"/>'
    body += '<g clip-path="url(#function-plot-clip)">' + clipped + '</g>'
    def coordinate(value):
        return _text(value) if value.is_Rational else '≈' + f'{float(value):.3f}'.rstrip('0').rstrip('.')

    special_points = {}
    for p in model['stationary']:
        special_points[(p, expression.subs(X, p))] = ['Cực trị' if len(model['stationary']) == 2 else 'Điểm dừng']
    for p in roots:
        special_points.setdefault((p, sp.S.Zero), []).append('Ox')
    if 0 not in model['excluded']:
        special_points.setdefault((sp.S.Zero, expression.subs(X, 0)), []).append('Oy')
    if center:
        special_points.setdefault(center, []).append('I')
    labels = []
    guides = ''
    for (p, v), names in special_points.items():
        xp, yp = px(float(p)), py(float(v))
        if any(n in names for n in ('Cực trị', 'Điểm dừng', 'I')):
            guides += '<g data-projection="true">' + _line(xp, yp, xp, py(0), True) + _line(xp, yp, px(0), yp, True) + '</g>'
        guides += f'<circle data-point="{html.escape(" ".join(names), quote=True)}" cx="{xp:.3f}" cy="{yp:.3f}" r="3.2" fill="#111" stroke="#111" stroke-width="1.5"/>'
        name = 'I' if 'I' in names else ''
        text = f'{name}({coordinate(p)}; {coordinate(v)})'
        # Keep labels clear of the axes and of other point labels.
        lx = xp + (48 if abs(xp-px(0)) < 28 else -25 if xp > 690 else 0)
        ly = yp - 17 if yp < py(0)-6 else yp + 22
        for old_x, old_y in labels:
            if abs(lx-old_x) < 95 and abs(ly-old_y) < 20:
                ly += 23
        lx, ly = min(730, max(84, lx)), min(446, max(30, ly))
        labels.append((lx, ly))
        body += _label(lx, ly, text, 13)
    # Guides are clipped to the graph rectangle; point labels remain readable.
    body += '<g clip-path="url(#function-plot-clip)">' + guides + '</g>'
    if asymptote is not None:
        poles = [p for p in model['excluded'] if sp.limit(expression, X, p) in (sp.oo, -sp.oo)]
        caption = '; '.join(['x=' + _text(p) for p in poles] + ['y=' + _text(asymptote)])
        body += _label(410, 469, 'Tiệm cận: ' + caption, 15)
    return _svg(820, 490, 'Đồ thị y=' + str(expression), body)


@lru_cache(maxsize=64)
def explicit_function_visuals(topic):
    """Only one unambiguous ASCII function in the selected topic; no guessed examples."""
    matches = list(re.finditer(r'(?<!\w)y\s*=\s*((?:(?:\\(?:dfrac|frac|left|right|cdot|times))|[0-9xX+\-*/^().{}\s])+)', topic))
    if len(matches) != 1:
        return ''
    raw = matches[0][1].strip()
    tail = topic[matches[0].end():]
    if not raw.endswith('.') and re.match(r'[A-Za-z_\\]', tail):
        return ''
    source = raw.rstrip('.').strip().lower()
    try:
        model = function_model(source, strict=True)
        numerator, denominator = sp.fraction(model['expression'])
        if re.search(r'2\s*/\s*1|bậc hai trên bậc nhất', topic, re.I):
            if sp.degree(numerator, X) != 2 or sp.degree(denominator, X) != 1:
                raise NonStandardFunction('Not a non-degenerate quadratic over linear')
        if re.search(r'1\s*/\s*1|bậc nhất trên bậc nhất', topic, re.I):
            if sp.degree(numerator, X) > 1 or sp.degree(denominator, X) != 1:
                raise NonStandardFunction('Not a non-degenerate homographic function')
        return ('<section class="verified-function-visuals" style="break-inside:avoid">'
                '<h3>Bảng biến thiên và đồ thị theo hàm số đã chọn</h3>'
                '<p class="lesson-math" data-display="false" data-tex="y=' + html.escape(sp.latex(model['expression']), quote=True) + '"></p>'
                + '<p>Điểm loại khỏi miền xác định: ' + html.escape(', '.join(_text(p) for p in model['excluded']) or 'không có') + '.</p>'
                + variation_svg(model) + graph_svg(model) + '</section>')
    except NonStandardFunction:
        return '<p class="notice" data-function-rejected="true">Hàm số không thuộc ba dạng không suy biến đang xét. Cần kiểm tra bậc tử, bậc mẫu và điều kiện không khử nhân tử trước khi dựng BBT và đồ thị.</p>'
    except ValueError as error:
        if str(error) == 'Zero denominator':
            return '<p class="notice" data-function-rejected="true">Mẫu số đồng nhất bằng 0: không xác định hàm số, không dựng BBT hoặc đồ thị.</p>'
        return ''
    except (SyntaxError, TypeError, NotImplementedError, OverflowError, ZeroDivisionError, sp.PolynomialError):
        return ''


def with_function_visuals(body, topic, lesson=''):
    """Use the same figure on the lesson page and in all export styles."""
    visuals = explicit_function_visuals(str(topic or ''))
    if not visuals and not re.search(r'(?<!\w)y\s*=', str(topic or '')):
        # A generic topic may have one repeated worked example. Never choose
        # between different examples, or interpret code snippets as mathematics.
        prose = re.sub(r'```[\s\S]*?```|~~~[\s\S]*?~~~|`[^`\n]*`', '', lesson)
        candidates = re.finditer(r'(?<!\w)y\s*=\s*((?:(?:\\(?:dfrac|frac|left|right|cdot|times))|[0-9xX+\-*/^().{}\s])+)', prose)
        figures = set()
        for candidate in candidates:
            raw = candidate[1].strip()
            if not raw.endswith('.') and re.match(r'[A-Za-z_\\]', prose[candidate.end():]):
                continue
            figure = explicit_function_visuals('y=' + raw)
            if figure and 'data-function-rejected' not in figure:
                figures.add(figure)
        if len(figures) == 1:
            visuals = figures.pop()
    if not visuals:
        return body
    replaced = [False]

    def replace_table(match):
        plain = html.unescape(re.sub(r'<[^>]+>', '', match[0]))
        if not replaced[0] and re.search(r'x[\s\S]*y[′\'][\s\S]*y', plain):
            replaced[0] = True
            return visuals
        return match[0]

    result = re.sub(r'<table\b[^>]*>[\s\S]*?</table>', replace_table, body)
    return result if replaced[0] else result + visuals
