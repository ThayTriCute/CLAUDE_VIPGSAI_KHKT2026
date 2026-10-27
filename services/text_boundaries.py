"""Preserve typed content at presentation boundaries; do not judge curriculum."""
import hashlib
import json
import re

from services.lesson_export import _TOKENS


def preserve_math_and_code(text, normalize_prose):
    value = str(text or '')
    prefix = 'GSAIPRESERVE' + hashlib.sha256(value.encode()).hexdigest()[:16]
    while prefix in value:
        prefix += 'X'
    slots = []

    def save(match):
        original = match[0]
        # Streamlit's Markdown math path uses dollars. Change delimiters only,
        # retaining the formula body and whether it is inline or display math.
        if original.startswith(r'\['):
            original = '$$' + original[2:-2] + '$$'
        elif original.startswith(r'\('):
            original = '$' + original[2:-2] + '$'
        slots.append(original)
        return f'{prefix}N{len(slots)-1}END'

    result = normalize_prose(_TOKENS.sub(save, value))
    for index, original in enumerate(slots):
        result = result.replace(f'{prefix}N{index}END', original)
    return result


def student_essay_text(text):
    """Hide reserved author metadata, retaining the question and Polya prompts.

    A complete JSON value may occupy several lines. Do not guess its closing
    delimiters or consume the following student exercise when JSON is damaged.
    """
    value = str(text or '')
    spans = []
    for match in re.finditer(r'(?mi)^[ \t]*(OUTCOME|COGNITIVE_REASON|COGNITIVE_STEPS):[ \t]*', value):
        end = value.find('\n', match.end())
        end = len(value) if end < 0 else end
        if match[1].upper() == 'COGNITIVE_STEPS':
            tail = value[match.end():].lstrip()
            try:
                _, length = json.JSONDecoder().raw_decode(tail)
                end = max(end, len(value) - len(tail) + length)
            except (ValueError, TypeError):
                pass
        spans.append((match.start(), end))
    for start, end in reversed(spans):
        value = value[:start] + value[end:]
    return value.strip()
