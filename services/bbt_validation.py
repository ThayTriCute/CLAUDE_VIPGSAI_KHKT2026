"""Validate complete compact BBT input for the application's EXISTING renderer.

This module does not draw HTML/SVG or invent missing signs/values.
"""
from fractions import Fraction
import math
import re


def validated_compact_bbt_rows(raw):
    rows = [[c.strip().strip('$').strip() for c in line.strip().strip('|').split('|')]
            for line in str(raw).splitlines() if '|' in line]
    if len(rows) != 3 or [r[0] for r in rows] not in (['x', "y'", 'y'], ['x', 'y′', 'y']):
        return None
    points, signs, values = [r[1:] for r in rows]
    n = len(points)
    if not 2 <= n <= 12 or len(values) != n or len(signs) != 2*n-3:
        return None
    if any(signs[2*i] not in ('+', '-', '−') for i in range(n-1)) or any(signs[2*i-1] != '0' for i in range(1, n-1)):
        return None

    def number(token):
        token = token.replace(r'\infty', 'inf').replace('∞', 'inf').replace('−', '-')
        if token in ('inf', '+inf'):
            return math.inf
        if token == '-inf':
            return -math.inf
        if len(token) > 40 or not re.fullmatch(r'[+-]?\d+(?:\.\d+)?(?:/\d+)?', token):
            raise ValueError('Unsupported numeric cell')
        return Fraction(token)

    def notation(token):
        value = number(token)
        return r'-\infty' if value == -math.inf else r'+\infty' if value == math.inf else token

    try:
        xs, ys = list(map(number, points)), list(map(number, values))
        if any(not a < b for a, b in zip(xs, xs[1:])):
            return None
        for i in range(n-1):
            if not (ys[i] < ys[i+1] if signs[2*i] == '+' else ys[i] > ys[i+1]):
                return None
        return (['x', *map(notation, points)], ["y'", *signs], ['y', *map(notation, values)])
    except (ValueError, ZeroDivisionError, OverflowError):
        return None
