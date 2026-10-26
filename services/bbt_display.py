"""Display complete compact variation tables without inventing missing data."""
from fractions import Fraction
import html
import math
import re


def render_compact_bbt(raw):
    rows = [[c.strip().strip('$').strip() for c in line.strip().strip('|').split('|')]
            for line in str(raw).splitlines() if '|' in line]
    if len(rows) != 3 or [r[0] for r in rows] not in (['x', "y'", 'y'], ['x', 'y′', 'y']):
        return ''
    points, signs, values = [r[1:] for r in rows]
    n = len(points)
    if not 2 <= n <= 12 or len(values) != n or len(signs) != 2*n-3:
        return ''
    if any(signs[2*i] not in ('+', '-', '−') for i in range(n-1)) or any(signs[2*i-1] != '0' for i in range(1, n-1)):
        return ''

    def number(token):
        token = token.replace(r'\infty', 'inf').replace('∞', 'inf').replace('−', '-')
        if token in ('inf', '+inf'):
            return math.inf
        if token == '-inf':
            return -math.inf
        if len(token) > 40 or not re.fullmatch(r'[+-]?\d+(?:\.\d+)?(?:/\d+)?', token):
            raise ValueError('Unsupported numeric cell')
        return Fraction(token)

    def display(token):
        value = number(token)
        return '−∞' if value == -math.inf else '+∞' if value == math.inf else html.escape(token)

    try:
        xs, ys = list(map(number, points)), list(map(number, values))
        if any(not a < b for a, b in zip(xs, xs[1:])):
            return ''
        for i in range(n-1):
            if not (ys[i] < ys[i+1] if signs[2*i] == '+' else ys[i] > ys[i+1]):
                return ''  # Do not repair conflicting source data in the renderer.
        xcells, dcells, ycells = [], [], []
        for i in range(n):
            xcells.append(display(points[i]))
            dcells.append('0' if 0 < i < n-1 else '')
            ycells.append(display(values[i]))
            if i < n-1:
                xcells.append('')
                dcells.append('+' if signs[2*i] == '+' else '−')
                ycells.append('↗' if signs[2*i] == '+' else '↘')
        def row(label, cells):
            return '<tr><th scope="row">'+label+'</th>'+''.join('<td>'+cell+'</td>' for cell in cells)+'</tr>'
        return ('<div style="overflow-x:auto"><table aria-label="Bảng biến thiên theo dữ liệu câu hỏi" '
                'class="gsai-compact-bbt" style="border-collapse:collapse;text-align:center;min-width:480px">'
                '<style>.gsai-compact-bbt td,.gsai-compact-bbt th{border:1px solid #64748b;padding:10px;min-width:35px}</style>'
                +row('x', xcells)+row('y′', dcells)+row('y', ycells)+'</table></div>')
    except (ValueError, ZeroDivisionError, OverflowError):
        return ''
