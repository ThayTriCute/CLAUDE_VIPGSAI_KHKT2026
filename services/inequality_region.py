"""Miền nghiệm hệ bất phương trình bậc nhất hai ẩn (Toán 10, KNTT) — dựng tại chỗ, không gọi AI.

Quy ước SGK: miền nghiệm là miền KHÔNG bị gạch (kể cả bờ nếu bất phương trình không ngặt);
bờ của bất phương trình ngặt vẽ nét đứt. Tọa độ đỉnh tính bằng phân số chính xác, không làm tròn.
"""
import html
import re
from fractions import Fraction

T1_CONTEXT_REVISION = 2026110913

_OPS = {'<=': '<=', '=<': '<=', '≤': '<=', '⩽': '<=', '>=': '>=', '=>': '>=', '≥': '>=', '⩾': '>=', '<': '<', '>': '>'}
_OP_RE = r'(<=|=<|≤|⩽|>=|=>|≥|⩾|<|>)'
_KEYWORDS = ('mien nghiem', 'bat phuong trinh', 'he bpt', 'bpt', 'mien xac dinh boi', 'gioi han boi')


def _fold(text):
    import unicodedata
    text = unicodedata.normalize('NFD', str(text).lower()).replace('đ', 'd')
    return ''.join(ch for ch in text if unicodedata.category(ch) != 'Mn')


def _number(token):
    token = token.replace(',', '.')
    if '/' in token:
        num, den = token.split('/', 1)
        return Fraction(num) / Fraction(den)
    return Fraction(token)


def _linear(expr):
    """'3x + 5y - 1' -> (a, b, c) với biểu thức = a*x + b*y + c. None nếu không tuyến tính theo x, y."""
    s = expr.replace(' ', '').replace('−', '-').replace('*', '').replace('·', '').lower()
    s = re.sub(r'\\frac\{([^{}]+)\}\{([^{}]+)\}', r'(\1/\2)', s).replace('{', '').replace('}', '')
    s = re.sub(r'\((\d+(?:[.,]\d+)?/\d+(?:[.,]\d+)?)\)', r'\1', s)
    if not s or re.search(r'[^0-9xy+\-./,]', s) or re.search(r'xy|yx|x\d|y\d|[xy][xy]', s):
        return None
    a = b = c = Fraction(0)
    for sign, coef, var in re.findall(r'([+-]?)(\d+(?:[.,]\d+)?(?:/\d+(?:[.,]\d+)?)?)?([xy]?)', s):
        if not coef and not var:
            continue
        value = _number(coef) if coef else Fraction(1)
        if sign == '-':
            value = -value
        if var == 'x':
            a += value
        elif var == 'y':
            b += value
        else:
            c += value
    rebuilt = re.sub(r'([+-]?)(\d+(?:[.,]\d+)?(?:/\d+(?:[.,]\d+)?)?)?([xy]?)', '', s)
    return None if rebuilt else (a, b, c)


def parse_constraints(text):
    """Danh sách (a, b, op, c) nghĩa là a*x + b*y op c. Bỏ qua phần không phải bất phương trình tuyến tính."""
    body = str(text or '').replace('\\leq', '≤').replace('\\le', '≤').replace('\\geq', '≥').replace('\\ge', '≥')
    body = re.sub(r'\\d?frac\{([^{}]+)\}\{([^{}]+)\}', r'(\1/\2)', body.replace('$', ' '))
    constraints = []
    for chunk in re.split(r'[;\n]|,(?!\d)|\bvà\b|\band\b|\bva\b', body, flags=re.I):
        parts = re.split(_OP_RE, chunk)
        if len(parts) < 3:
            continue
        sides = parts[0::2]
        ops = parts[1::2]
        # chỉ giữ phần biểu thức toán ở hai đầu (bỏ chữ mô tả)
        sides[0] = re.split(r'[^\w\s+\-*/.,()·{}\\−]|[a-wzA-WZ_À-ỹ]{2,}', sides[0])[-1]
        sides[-1] = re.split(r'[^\w\s+\-*/.,()·{}\\−]|[a-wzA-WZ_À-ỹ]{2,}', sides[-1])[0]
        for left, op, right in zip(sides, ops, sides[1:]):
            l, r = _linear(left), _linear(right)
            if l is None or r is None:
                continue
            a, b, c = l[0] - r[0], l[1] - r[1], r[2] - l[2]
            if a == 0 and b == 0:
                continue
            op = _OPS[op]
            if l[0] == 0 and l[1] == 0:
                # '0 <= x', '7 >= 3x + 5y': giữ dạng biến ở vế trái như SGK.
                a, b, c, op = -a, -b, -c, {'<=': '>=', '>=': '<=', '<': '>', '>': '<'}[op]
            constraints.append((a, b, op, c))
    unique = []
    for item in constraints:
        if item not in unique:
            unique.append(item)
    return unique


def linear_region_request(command, subject):
    """Lệnh Lab Toán chứa hệ BPT bậc nhất hai ẩn -> mô hình dựng tại chỗ (không tốn lượt AI)."""
    from services.academic_context import canonical_subject
    if canonical_subject(subject) != 'Toán học':
        return None
    constraints = parse_constraints(command)
    if not constraints:
        return None
    folded = _fold(command)
    mixed = any(a != 0 and b != 0 for a, b, _, _ in constraints)
    if not (mixed or any(k in folded for k in _KEYWORDS)) or len(constraints) > 8:
        return None
    return dict(type='linear_region', constraints=[_constraint_text(c) for c in constraints])


def _satisfies(point, constraint, strict_as_closed=True):
    a, b, op, c = constraint
    value = a * point[0] + b * point[1]
    if op in ('<=', '<'):
        return value <= c if (strict_as_closed or op == '<=') else value < c
    return value >= c if (strict_as_closed or op == '>=') else value > c


def _frac_text(value):
    value = Fraction(value)
    sign = '−' if value < 0 else ''
    value = abs(value)
    return sign + (str(value.numerator) if value.denominator == 1 else f'{value.numerator}/{value.denominator}')


def _frac_tex(value):
    value = Fraction(value)
    sign = '-' if value < 0 else ''
    value = abs(value)
    return sign + (str(value.numerator) if value.denominator == 1 else rf'\dfrac{{{value.numerator}}}{{{value.denominator}}}')


def _side(a, b, c, tex=False):
    fmt = _frac_tex if tex else _frac_text
    terms = []
    for coef, var in ((a, 'x'), (b, 'y')):
        if coef == 0:
            continue
        mag = abs(coef)
        body = var if mag == 1 else (fmt(mag) + var if tex or mag.denominator == 1 else '(' + fmt(mag) + ')' + var)
        terms.append(('-' if coef < 0 else '+', body))
    out = ''
    for i, (sign, body) in enumerate(terms):
        out += (('-' if tex else '−') + body if sign == '-' else body) if i == 0 else (f' {"-" if tex else "−"} ' if sign == '-' else ' + ') + body
    return out


def _constraint_text(constraint, tex=False):
    a, b, op, c = constraint
    symbol = {'<=': r'\le' if tex else '≤', '>=': r'\ge' if tex else '≥', '<': '<', '>': '>'}[op]
    return f'{_side(a, b, c, tex)} {symbol} {(_frac_tex if tex else _frac_text)(c)}'


def _clip(polygon, constraint):
    """Sutherland–Hodgman với nửa mặt phẳng đóng; tọa độ Fraction nên giao điểm chính xác."""
    a, b, op, c = constraint
    sign = 1 if op in ('<=', '<') else -1
    inside = lambda p: sign * (a * p[0] + b * p[1] - c) <= 0
    out = []
    for i, cur in enumerate(polygon):
        prev = polygon[i - 1]
        if inside(cur):
            if not inside(prev):
                out.append(_intersect(prev, cur, a, b, c))
            out.append(cur)
        elif inside(prev):
            out.append(_intersect(prev, cur, a, b, c))
    return out


def _intersect(p, q, a, b, c):
    fp, fq = a * p[0] + b * p[1] - c, a * q[0] + b * q[1] - c
    t = fp / (fp - fq)
    return (p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1]))


def _dedupe(points):
    out = []
    for p in points:
        if not out or p != out[-1]:
            out.append(p)
    if len(out) > 1 and out[0] == out[-1]:
        out.pop()
    return out


def analyse(constraints):
    """Đỉnh chính xác, tình trạng (bounded / unbounded / empty / degenerate)."""
    big = Fraction(10 ** 6)
    region = [(-big, -big), (big, -big), (big, big), (-big, big)]
    for constraint in constraints:
        region = _dedupe(_clip(region, constraint))
        if not region:
            return {'status': 'empty', 'vertices': []}
    area = sum(region[i - 1][0] * region[i][1] - region[i][0] * region[i - 1][1] for i in range(len(region)))
    if len(region) < 3 or area == 0:
        status = 'degenerate'
    elif any(abs(x) >= big / 2 or abs(y) >= big / 2 for x, y in region):
        status = 'unbounded'
    else:
        status = 'bounded'
    vertices = [p for p in region if abs(p[0]) < big / 2 and abs(p[1]) < big / 2]
    # Bất phương trình ngặt: miền rỗng nếu chỉ còn bờ (diện tích 0).
    if status == 'degenerate' and any(op in ('<', '>') for _, _, op, _ in constraints):
        status, vertices = 'empty', []
    return {'status': status, 'vertices': vertices}


def _view(constraints, vertices):
    xs, ys = [Fraction(0)], [Fraction(0)]
    for x, y in vertices:
        xs.append(x); ys.append(y)
    for a, b, _, c in constraints:
        if a != 0:
            xs.append(c / a)
        if b != 0:
            ys.append(c / b)
    lo_x, hi_x = float(min(xs)) - 1, float(max(xs)) + 1
    lo_y, hi_y = float(min(ys)) - 1, float(max(ys)) + 1
    span = max(hi_x - lo_x, hi_y - lo_y, 4.0)
    cx, cy = (lo_x + hi_x) / 2, (lo_y + hi_y) / 2
    return cx - span / 2, cx + span / 2, cy - span / 2, cy + span / 2


def region_svg(constraints):
    """SVG nền sáng, chữ đậm, không phụ thuộc font/thiết bị. Trả (svg, info)."""
    info = analyse(constraints)
    x0, x1, y0, y1 = _view(constraints, info['vertices'])
    W = H = 520
    pad = 46
    sx = lambda x: pad + (x - x0) / (x1 - x0) * (W - 2 * pad)
    sy = lambda y: H - pad - (y - y0) / (y1 - y0) * (H - 2 * pad)
    box = [(Fraction(x0).limit_denominator(1000), Fraction(y0).limit_denominator(1000)),
           (Fraction(x1).limit_denominator(1000), Fraction(y0).limit_denominator(1000)),
           (Fraction(x1).limit_denominator(1000), Fraction(y1).limit_denominator(1000)),
           (Fraction(x0).limit_denominator(1000), Fraction(y1).limit_denominator(1000))]
    pts = lambda poly: ' '.join(f'{sx(float(x)):.2f},{sy(float(y)):.2f}' for x, y in poly)
    parts = ['<defs><pattern id="gsai-hatch" width="9" height="9" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
             '<line x1="0" y1="0" x2="0" y2="9" stroke="#64748b" stroke-width="1.6"/></pattern>'
             f'<clipPath id="gsai-view"><rect x="{pad}" y="{pad}" width="{W-2*pad}" height="{H-2*pad}"/></clipPath></defs>',
             f'<rect width="{W}" height="{H}" fill="#ffffff"/>']
    grid = []
    near_x = [float(x) for x, y in info['vertices'] if y == 0]
    near_y = [float(y) for x, y in info['vertices'] if x == 0]
    for gx in range(int(x0) - 1, int(x1) + 2):
        if x0 <= gx <= x1:
            grid.append(f'<line x1="{sx(gx):.2f}" y1="{pad}" x2="{sx(gx):.2f}" y2="{H-pad}" stroke="#e2e8f0"/>')
            if gx != 0 and all(abs(gx - v) > 0.45 * (x1 - x0) / 8 for v in near_x):
                grid.append(f'<text x="{sx(gx):.2f}" y="{min(H-pad, max(pad, sy(0)))+16:.2f}" font-size="12" text-anchor="middle" fill="#334155">{gx}</text>')
    for gy in range(int(y0) - 1, int(y1) + 2):
        if y0 <= gy <= y1:
            grid.append(f'<line x1="{pad}" y1="{sy(gy):.2f}" x2="{W-pad}" y2="{sy(gy):.2f}" stroke="#e2e8f0"/>')
            if gy != 0 and all(abs(gy - v) > 0.45 * (y1 - y0) / 8 for v in near_y):
                grid.append(f'<text x="{min(W-pad, max(pad, sx(0)))-6:.2f}" y="{sy(gy)+4:.2f}" font-size="12" text-anchor="end" fill="#334155">{gy}</text>')
    parts += grid
    # Gạch phần KHÔNG thỏa từng bất phương trình (quy ước SGK).
    for a, b, op, c in constraints:
        flipped = (a, b, {'<=': '>', '<': '>=', '>=': '<', '>': '<='}[op], c)
        excluded = _dedupe(_clip(box, flipped))
        if len(excluded) >= 3:
            parts.append(f'<polygon points="{pts(excluded)}" fill="url(#gsai-hatch)" fill-opacity="0.75" clip-path="url(#gsai-view)"/>')
    feasible = box
    for constraint in constraints:
        feasible = _dedupe(_clip(feasible, constraint))
    if len(feasible) >= 3:
        parts.append(f'<polygon points="{pts(feasible)}" fill="#22c55e" fill-opacity="0.12" stroke="none" clip-path="url(#gsai-view)"/>')
    # Trục tọa độ.
    ax_y, ax_x = sy(0), sx(0)
    parts.append(f'<line x1="{pad-6}" y1="{ax_y:.2f}" x2="{W-pad+14}" y2="{ax_y:.2f}" stroke="#0f172a" stroke-width="1.6" marker-end="url(#gsai-arrow)"/>')
    parts.append(f'<line x1="{ax_x:.2f}" y1="{H-pad+6}" x2="{ax_x:.2f}" y2="{pad-14}" stroke="#0f172a" stroke-width="1.6" marker-end="url(#gsai-arrow)"/>')
    parts[0] = parts[0].replace('</defs>', '<marker id="gsai-arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 Z" fill="#0f172a"/></marker></defs>')
    parts.append(f'<text x="{W-pad+12}" y="{ax_y-8:.2f}" font-size="15" font-style="italic" font-weight="700" fill="#0f172a">x</text>')
    parts.append(f'<text x="{ax_x+8:.2f}" y="{pad-6}" font-size="15" font-style="italic" font-weight="700" fill="#0f172a">y</text>')
    parts.append(f'<text x="{ax_x-6:.2f}" y="{ax_y+16:.2f}" font-size="13" text-anchor="end" font-weight="700" fill="#0f172a">O</text>')
    # Đường bờ: nét liền (không ngặt), nét đứt (ngặt).
    legend = []
    palette = ['#2563eb', '#dc2626', '#7c3aed', '#ea580c', '#0891b2', '#be185d', '#4d7c0f', '#0f766e']
    for k, (a, b, op, c) in enumerate(constraints):
        seg = _dedupe(_clip(_clip(box, (a, b, '<=', c)), (a, b, '>=', c)))
        if len(seg) < 2:
            continue
        (p, q) = seg[0], seg[-1]
        dash = ' stroke-dasharray="7 5"' if op in ('<', '>') else ''
        color = palette[k % len(palette)]
        parts.append(f'<line x1="{sx(float(p[0])):.2f}" y1="{sy(float(p[1])):.2f}" x2="{sx(float(q[0])):.2f}" y2="{sy(float(q[1])):.2f}" stroke="{color}" stroke-width="2.4"{dash}/>')
        t = 0.82 - 0.11 * (k % 4)
        lx = sx(float(p[0]) + t * (float(q[0]) - float(p[0])))
        ly = sy(float(p[1]) + t * (float(q[1]) - float(p[1])))
        parts.append(f'<text x="{lx+5:.2f}" y="{ly-5:.2f}" font-size="14" font-weight="700" font-style="italic" fill="{color}" stroke="#ffffff" stroke-width="3.5" paint-order="stroke">d{k+1}</text>')
        legend.append((color, op in ('<', '>'), f'd{k+1}: {_side(a, b, c)} = {_frac_text(c)}  —  ứng với {_constraint_text((a, b, op, c))}'))
    # Đỉnh, tọa độ chính xác.
    names = iter('ABCDEFGHKLMNPQ')
    labels = []
    verts = info['vertices']
    mx = sum(float(x) for x, _ in verts) / len(verts) if verts else 0.0
    my = sum(float(y) for _, y in verts) / len(verts) if verts else 0.0
    for x, y in verts:
        name = 'O' if x == 0 and y == 0 else next(names)
        labels.append((name, x, y))
        cx, cy = sx(float(x)), sy(float(y))
        parts.append(f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="4.2" fill="#0f172a"/>')
        if name != 'O':
            text = f'{name}({_frac_text(x)}; {_frac_text(y)})'
            right = float(x) >= mx
            tx = cx + 8 if right else cx - 8
            ty = cy - 8 if float(y) >= my else cy + 18
            tx = min(max(tx, pad + (0 if right else 8 * len(text))), W - pad - (8 * len(text) if right else 0))
            anchor = 'start' if right else 'end'
            parts.append(f'<text x="{tx:.2f}" y="{ty:.2f}" text-anchor="{anchor}" font-size="13" font-weight="700" fill="#0f172a" stroke="#ffffff" stroke-width="3.5" paint-order="stroke">{html.escape(text)}</text>')
    head = ['Miền nghiệm: phần KHÔNG bị gạch (tô xanh nhạt).', 'Nét liền: bờ thuộc miền nghiệm; nét đứt: bờ không thuộc miền nghiệm.']
    rows = head + [r[2] for r in legend]
    for i, row in enumerate(rows):
        color = '#0f172a' if i < len(head) else legend[i - len(head)][0]
        if i >= len(head):
            dash = ' stroke-dasharray="7 5"' if legend[i - len(head)][1] else ''
            parts.append(f'<line x1="14" y1="{H + 8 + 24 * i:.0f}" x2="44" y2="{H + 8 + 24 * i:.0f}" stroke="{color}" stroke-width="2.6"{dash}/>')
        parts.append(f'<text x="{52 if i >= len(head) else 14}" y="{H + 13 + 24 * i:.0f}" font-size="{12.5 if i < len(head) else 13.5}" font-weight="700" fill="{color}">{html.escape(row)}</text>')
    H_total = H + 24 * len(rows) + 10
    parts.insert(1, f'<rect y="{H}" width="{W}" height="{H_total - H}" fill="#ffffff"/>')
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H_total}" role="img" '
           f'aria-label="Miền nghiệm của hệ bất phương trình" style="max-width:560px;width:100%;height:auto;font-family:Arial,sans-serif">'
           + ''.join(parts) + '</svg>')
    info['labels'] = labels
    return svg, info


def region_plotly_spec(constraints):
    """Cùng dữ liệu chính xác như SVG, dạng Plotly (dict data/layout, không phụ thuộc plotly khi kiểm thử).
    Phần không thỏa từng BPT tô gạch xám; miền nghiệm tô xanh nhạt; bờ ngặt nét đứt; đỉnh ghi phân số."""
    info = analyse(constraints)
    x0, x1, y0, y1 = _view(constraints, info['vertices'])
    box = [(Fraction(x0).limit_denominator(1000), Fraction(y0).limit_denominator(1000)),
           (Fraction(x1).limit_denominator(1000), Fraction(y0).limit_denominator(1000)),
           (Fraction(x1).limit_denominator(1000), Fraction(y1).limit_denominator(1000)),
           (Fraction(x0).limit_denominator(1000), Fraction(y1).limit_denominator(1000))]
    closed = lambda poly: ([float(x) for x, _ in poly] + [float(poly[0][0])], [float(y) for _, y in poly] + [float(poly[0][1])])
    data = []
    for k, (a, b, op, c) in enumerate(constraints):
        flipped = (a, b, {'<=': '>', '<': '>=', '>=': '<', '>': '<='}[op], c)
        excluded = _dedupe(_clip(box, flipped))
        if len(excluded) >= 3:
            xs, ys = closed(excluded)
            data.append(dict(type='scatter', x=xs, y=ys, mode='lines', fill='toself', line=dict(width=0),
                             fillcolor='rgba(100,116,139,0.28)', fillpattern=dict(shape='/', fgcolor='#64748b', size=9),
                             hoverinfo='skip', showlegend=k == 0, name='Phần bị gạch (không thỏa)', legendgroup='hatch'))
    feasible = box
    for constraint in constraints:
        feasible = _dedupe(_clip(feasible, constraint))
    if len(feasible) >= 3:
        xs, ys = closed(feasible)
        data.append(dict(type='scatter', x=xs, y=ys, mode='lines', fill='toself', line=dict(width=0),
                         fillcolor='rgba(34,197,94,0.18)', hoverinfo='skip', name='Miền nghiệm (không bị gạch)'))
    palette = ['#2563eb', '#dc2626', '#7c3aed', '#ea580c', '#0891b2', '#be185d', '#4d7c0f', '#0f766e']
    for k, (a, b, op, c) in enumerate(constraints):
        seg = _dedupe(_clip(_clip(box, (a, b, '<=', c)), (a, b, '>=', c)))
        if len(seg) < 2:
            continue
        p, q = seg[0], seg[-1]
        data.append(dict(type='scatter', x=[float(p[0]), float(q[0])], y=[float(p[1]), float(q[1])], mode='lines',
                         line=dict(color=palette[k % len(palette)], width=3, dash='dash' if op in ('<', '>') else 'solid'),
                         name=f'd{k+1}: {_side(a, b, c)} = {_frac_text(c)} ({_constraint_text((a, b, op, c))})',
                         hovertemplate=f'd{k+1}: {_side(a, b, c)} = {_frac_text(c)}<extra></extra>'))
    names = iter('ABCDEFGHKLMNPQ')
    labels = [('O' if x == 0 and y == 0 else next(names), x, y) for x, y in info['vertices']]
    if labels:
        data.append(dict(type='scatter', x=[float(x) for _, x, _ in labels], y=[float(y) for _, _, y in labels],
                         mode='markers+text', marker=dict(size=9, color='#0f172a'),
                         text=[n if n == 'O' else f'{n}({_frac_text(x)}; {_frac_text(y)})' for n, x, y in labels],
                         textposition='top right', textfont=dict(size=13, color='#0f172a'),
                         hovertemplate='%{text}<extra></extra>', name='Đỉnh (tọa độ chính xác)'))
    axis = dict(zeroline=True, zerolinecolor='#0f172a', zerolinewidth=2, gridcolor='#e2e8f0', dtick=1,
                color='#0f172a', showline=False)
    layout = dict(template='plotly_white', height=560, margin=dict(l=40, r=20, t=40, b=40),
                  paper_bgcolor='#ffffff', plot_bgcolor='#ffffff', font=dict(color='#0f172a'),
                  title=dict(text='Miền nghiệm của hệ bất phương trình', font=dict(size=16)),
                  xaxis=dict(axis, range=[x0, x1], title='x'), yaxis=dict(axis, range=[y0, y1], title='y', scaleanchor='x', scaleratio=1),
                  legend=dict(orientation='h', y=-0.12, font=dict(size=12)))
    return {'data': data, 'layout': layout}, info
