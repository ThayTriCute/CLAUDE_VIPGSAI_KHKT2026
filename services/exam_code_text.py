"""Escape printable source text while retaining fenced code verbatim."""
import html
import re

FENCES = re.compile(r'(```[^\n]*\n[\s\S]*?```|~~~[^\n]*\n[\s\S]*?~~~)')


def code_body(block):
    return block.split('\n', 1)[1][:-3].rstrip('\r\n')


def source_text_html(value):
    chunks = FENCES.split(str(value or ''))
    return ''.join('<code class="exam-source-code" style="display:block;white-space:pre-wrap;'
                   'font:12px/1.4 monospace;overflow-wrap:anywhere;margin:6px 0">'
                   + html.escape(code_body(chunk)) + '</code>' if index % 2
                   else html.escape(chunk) for index, chunk in enumerate(chunks))


def teaching_text_html(value):
    """Use the shared step layout in answer sheets, retaining literal code/math."""
    from services.lesson_export import _TOKENS
    from services.text_boundaries import polya_display_markdown
    def prose(text):
        escaped = html.escape(text)
        escaped = re.sub(r'\*\*((?:Bước|Step)\s+\d+:[^*\n]*?)\*\*', r'<strong>\1</strong>', escaped, flags=re.I)
        return escaped.replace('\n\n', '<br><br>')
    chunks = _TOKENS.split(polya_display_markdown(value))
    return ''.join(source_text_html(chunk) if index % 2 else prose(chunk)
                   for index, chunk in enumerate(chunks))


def teaching_text_latex(value, converter):
    """Insert TeX paragraphs only outside protected code and math spans."""
    from services.text_boundaries import polya_display_markdown, preserve_math_and_code
    formatted = polya_display_markdown(value)
    marker = 'GSAISTEPPARAGRAPH'
    while marker in formatted:
        marker += 'X'
    separated = preserve_math_and_code(formatted, lambda text: text.replace('\n\n', marker))
    parts = []
    for part in separated.split(marker):
        # The label is display markup; preserve its words in the TeX output.
        part = preserve_math_and_code(part, lambda text: re.sub(
            r'\*\*((?:Bước|Step)\s+\d+:[^*\n]*?)\*\*', r'\1', text, flags=re.I))
        parts.append(converter(part))
    return r'\par\smallskip '.join(parts)


def code_text_latex(block):
    replacements = {"\\": r"\textbackslash{}", "{": r"\{", "}": r"\}",
                    "&": r"\&", "%": r"\%", "_": r"\_", "#": r"\#",
                    "$": r"\$", "~": r"\textasciitilde{}", "^": r"\textasciicircum{}",
                    " ": r"\ "}
    lines = [''.join(replacements.get(c,c) for c in line) for line in code_body(block).splitlines()]
    return r"\par\begingroup\ttfamily\small " + r"\\ ".join(lines) + r"\par\endgroup "
