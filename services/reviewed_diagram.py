"""Draw independently transcribed source geometry without inferring equations."""
import html
import math
import re


def draw_reviewed_diagram(spec):
    if spec.get('kind') != 'reviewed_diagram':
        return {}
    width, height = 360, 320

    def point(pair):
        x, y = pair
        if not all(type(v) in (int, float) and math.isfinite(v) for v in pair):
            raise ValueError('Invalid coordinates')
        if not (0 <= x <= width and 0 <= y <= height):
            raise ValueError('Point outside diagram')
        return f'{x:g},{y:g}'

    svg = []
    tikz = [r'\begin{tikzpicture}[x=0.022cm,y=-0.022cm]']
    try:
        if len(spec['paths']) > 48 or len(spec['labels']) > 32:
            return {}
        for path in spec['paths']:
            style = path['style']
            if style not in ('curve', 'edge', 'hidden', 'axis') or len(path['points']) > 25:
                return {}
            start, *points = [point(p) for p in path['points']]
            if not points or (style == 'curve' and len(points) % 3):
                return {}
            if style == 'curve':
                data = 'C ' + ' '.join(points)
                draw = ' '.join(f'.. controls ({a}) and ({b}) .. ({c})'
                                for a, b, c in zip(points[::3], points[1::3], points[2::3]))
            else:
                data = 'L ' + ' '.join(points)
                draw = ' '.join(f'-- ({p})' for p in points)
            attrs = {'hidden': ' stroke-dasharray="4 3"', 'axis': ' marker-end="url(#tip)"'}.get(style, '')
            options = {'hidden': 'dashed', 'axis': '->'}.get(style, '')
            weight = 2.5 if style == 'curve' else 1.4
            svg.append(f'<path d="M {start} {data}" fill="none" stroke="currentColor" stroke-width="{weight}"{attrs}/>')
            tikz.append(rf'\draw[{options},line width={0.95 if style == "curve" else 0.55}pt] ({start}) {draw};' if options else
                        rf'\draw[line width={0.95 if style == "curve" else 0.55}pt] ({start}) {draw};')
        for label in spec['labels']:
            name = label['text']
            if not re.fullmatch(r'[A-Za-z][0-9]?|-?[0-9]', name):
                return {}
            x, y = point(label['point']).split(',')
            svg.append(f'<text x="{x}" y="{y}" dominant-baseline="central" text-anchor="middle" fill="currentColor" font-family="serif" font-size="16">{html.escape(name)}</text>')
            tex = name[0] + '_' + name[1:] if name.startswith('O') and len(name) == 2 else name
            tikz.append(rf'\node at ({x},{y}) {{${tex}$}};')
    except (KeyError, TypeError, ValueError):
        return {}
    if not svg:
        return {}
    defs = '<defs><marker id="tip" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto"><path d="M0 0L6 3L0 6Z" fill="currentColor"/></marker></defs>'
    return {'type': 'reviewed_diagram',
            'svg': f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}">' + defs + ''.join(svg) + '</svg>',
            'tikz': '\n'.join([*tikz, r'\end{tikzpicture}'])}
