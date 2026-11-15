"""Align supplied rows for the existing BBT renderer; never invent limits."""
import re

# Đổi giá trị khi đổi API module này: worker Cloud giữ module cũ sẽ được nạp lại
# (app._refresh_t1_context_services) trước khi app.py gọi hàm mới. Sự cố 09/11/2026:
# ImportError normalize_bbt_discontinuity vì worker còn giữ bản cũ.
# 15/11/2026: expand BBT dồn 1 dòng; không phá \nearrow bằng replace \n; sửa mũi tên theo dấu y'.
T1_CONTEXT_REVISION = 2026111523

_ARROW_RE = re.compile(r"\$\\(?:nearrow|searrow)\$|\\(?:nearrow|searrow)|[↗↘]")


def expand_collapsed_bbt_line(line: str) -> str:
    """Tách BBT bị dồn một dòng (header|sep|y'|y) thành 4 hàng Markdown.

    Model hay xuất cả bảng trên một dòng; CommonMark không tạo <table> →
    bài giữ ống '|' (mũi tên đúng/sai lẫn) trong khi SVG verified bị đẩy xuống cuối.
    """
    line = str(line or "").strip()
    if "\n" in line or line.count("|") < 12:
        return line
    if not re.match(r"^\|\s*\$?x\$?\s*\|", line, re.I):
        return line
    if not (
        re.search(r"\$y\s*'\$|\$y'\$|y\\prime|\\nearrow|\\searrow|↗|↘", line, re.I)
        or "$y$" in line
        or "y'" in line
        or "y′" in line
    ):
        return line
    sep = re.search(r"\|\s*:?-{3,}:?\s*\|", line)
    if not sep:
        return line
    yp = re.search(r"\|\s*\$?y\s*(?:\\prime|[′'])\$?\s*\|", line[sep.end() - 1 :], re.I)
    if not yp:
        yp = re.search(r"\|\s*\$y'\s*\$\s*\|", line[sep.end() - 1 :])
    if not yp:
        return line
    yp_abs = sep.end() - 1 + yp.start()
    yr = re.search(r"\|\s*\$y\$\s*\|", line[yp_abs + 1 :])
    if not yr:
        yr = re.search(r"\|\s*y\s*\|(?!\s*\$?[′'])", line[yp_abs + 1 :])
    if not yr:
        return line
    yr_abs = yp_abs + 1 + yr.start()
    rows = [
        line[: sep.start()].strip(),
        line[sep.start() : yp_abs].strip(),
        line[yp_abs:yr_abs].strip(),
        line[yr_abs:].strip(),
    ]
    if not all(r.startswith("|") for r in rows):
        return line
    return "\n".join(rows)


def expand_collapsed_bbt_prose(prose: str) -> str:
    """Mở rộng mọi dòng BBT dồn trong khối văn."""
    return re.sub(
        r"(?m)^[ \t]{0,3}\|([^\n]{40,})\|[ \t]*$",
        lambda m: expand_collapsed_bbt_line(m[0]),
        str(prose or ""),
    )


def _is_separator_line(line: str) -> bool:
    stripped = str(line or "").strip()
    if not stripped.startswith("|"):
        return False
    # :||: của AI cũng là separator — bỏ || trước khi kiểm tra ký tự cho phép.
    core = stripped.replace("||", "").replace("|", "").replace(":", "").replace("-", "").strip()
    return not core and ("-" in stripped or ":" in stripped)


def sanitize_bbt_separator_row(line: str, columns=None) -> str:
    """Hàng separator Markdown chỉ được | :- ; AI hay viết :||: → CommonMark bỏ bảng."""
    if not _is_separator_line(line):
        return line
    if columns is None or columns < 2:
        # Đếm ô trước khi || bị split thành ô rỗng.
        probe = re.sub(r"\|\|+", "§", str(line).strip().strip("|"))
        columns = len(probe.split("|"))
    return "| " + " | ".join(":---:" for _ in range(columns)) + " |"


def prepare_bbt_markdown_block(block: str) -> str:
    """Tách dòng dồn → chuẩn hóa || → sửa separator (đúng số cột) → khóa mũi tên theo y'."""
    block = expand_collapsed_bbt_line(str(block or "").strip())
    rows = block.splitlines()
    if not is_bbt_markdown(rows):
        return block
    header = next((r for r in rows if r.strip().startswith("|") and not _is_separator_line(r)), None)
    columns = None
    if header is not None:
        columns = len(header.strip().strip("|").split("|"))
    normalized = []
    for row in rows:
        if _is_separator_line(row):
            normalized.append(sanitize_bbt_separator_row(row, columns=columns))
        else:
            normalized.append(normalize_bbt_discontinuity(row))
    return repair_bbt_arrows_from_signs("\n".join(normalized))


def _row_head(line: str) -> str:
    if not line.strip().startswith("|") or re.fullmatch(r"[\s|:\-]+", line.strip()):
        return ""
    return re.sub(r"[$\s*`{}^]", "", line.strip().strip("|").split("|")[0]).replace("\\prime", "'")


def _yprime_signs(yprime_line: str) -> list:
    body = yprime_line.strip().strip("|")
    body = re.sub(r"(?<!\|)\|\|(?!\|)", "§BAR§", normalize_bbt_discontinuity(body))
    cells = [c.strip().replace("§BAR§", "||") for c in body.split("|")]
    signs = []
    for cell in cells[1:]:
        token = re.sub(r"[$\s]", "", cell).replace("−", "-")
        if token in ("+", "-"):
            signs.append(token)
    return signs


def repair_bbt_arrows_from_signs(block: str) -> str:
    """Khóa mũi tên hàng y theo dấu y' (+→↗/\\nearrow, −→↘/\\searrow). Không bịa giới hạn."""
    lines = [ln for ln in str(block or "").splitlines()]
    useful = [ln for ln in lines if ln.strip()]
    if not is_bbt_markdown(useful):
        return block
    content = [
        ln
        for ln in useful
        if ln.strip().startswith("|") and not re.fullmatch(r"[\s|:\-]+", ln.strip())
    ]
    if len(content) < 3:
        return block
    yprime = next((ln for ln in content if "'" in _row_head(ln) or "′" in _row_head(ln)), None)
    yrow = next(
        (
            ln
            for ln in content
            if _row_head(ln) in ("y", "f(x)", "g(x)")
            or (
                _row_head(ln)
                and "'" not in _row_head(ln)
                and "′" not in _row_head(ln)
                and _row_head(ln) not in ("x", "t")
            )
        ),
        None,
    )
    if yprime is None or yrow is None:
        return block
    signs = _yprime_signs(yprime)
    arrows = list(_ARROW_RE.finditer(yrow))
    if not signs or len(arrows) != len(signs):
        return block
    out = []
    pos = 0
    for match, sign in zip(arrows, signs):
        out.append(yrow[pos : match.start()])
        token = match.group(0)
        if token.startswith("$"):
            out.append(r"$\nearrow$" if sign == "+" else r"$\searrow$")
        elif token.startswith("\\"):
            out.append(r"\nearrow" if sign == "+" else r"\searrow")
        else:
            out.append("↗" if sign == "+" else "↘")
        pos = match.end()
    out.append(yrow[pos:])
    repaired = "".join(out)
    return "\n".join(repaired if ln == yrow else ln for ln in lines)


def normalize_bbt_discontinuity(text):
    """Một nguồn duy nhất cho ký hiệu tiệm cận đứng (vạch kép) của BBT: mọi biến thể -> '||'.

    Model có thể viết \\parallel, \\Vert, ∥, ║, hoặc dạng thoát Markdown '\\|\\|' / '\\|'
    (bảng Markdown bắt buộc thoát '|' trong ô). Không chuẩn hóa thì ô y' bị coi như '0' và
    hai giới hạn ±∞ dồn chung một ô. Trị tuyệt đối \\|x\\| (dính chữ/số) được giữ nguyên.
    Chỉ gọi cho dữ liệu đã xác định là BBT/bảng xét dấu, không cho bảng thường.
    """
    if not text:
        return text
    s = str(text)
    s = re.sub(r'\\(?:\||Vert|lVert|rVert)\s*\\(?:\||Vert|lVert|rVert)(?![a-zA-Z])', '||', s)
    s = re.sub(r'\\(?:parallel|shortparallel|Vert|lVert|rVert)(?![a-zA-Z])', '||', s)
    s = re.sub(r'(?<![\w)\]}\\])\\\|(?![\w(\[{])', '||', s)
    return s.replace('∥', '||').replace('║', '||').replace('⫲', '||')


def is_bbt_markdown(lines):
    """Bảng có hàng đầu là biến (x/t) và một hàng đạo hàm/hàm số: BBT hoặc bảng xét dấu."""
    heads = [re.sub(r'[$\s*`{}^]', '', str(line).strip().strip('|').split('|')[0]).replace('\\prime', "'")
             for line in lines if str(line).strip().startswith('|') and not re.fullmatch(r'[\s|:\-]+', str(line))]
    return len(heads) >= 2 and heads[0] in ('x', 't') and any(re.search(r"[′'’]|^f\(x\)$|^y$|^g\(x\)$", h) for h in heads[1:])


def supplied_bbt_rows(raw):
    # Tách `\n` giả lập JSON kể cả khi dòng sau bắt đầu bằng y'/f'/x.
    # Không nuốt chữ n của \nearrow, \neq, \nu, \nabla, \not.
    text = re.sub(
        r'\\n(?!earrow|warrow|eq(?![A-Za-z])|e(?![A-Za-z])|u(?![A-Za-z])|abla|ot(?![A-Za-z])|less|gtr|mid|parallel|exists)',
        '\n', str(raw or ''))
    rows = []
    for line in text.splitlines():
        if '|' not in line or re.fullmatch(r'[\s|:\-]+', line):
            continue
        line = re.sub(r'(?<!\|)\|\|(?!\|)', '§BAR§', normalize_bbt_discontinuity(line.strip()))
        rows.append([s.strip().replace('§BAR§', '||') for s in line.strip('|').split('|')])
    return rows


def export_bbt_rows(raw):
    """Return existing alignment and a supplied excluded right endpoint flag."""
    aligned = aligned_bbt_rows(raw)
    if aligned is not None:
        return aligned, False
    rows = supplied_bbt_rows(raw)
    if len(rows) != 3 or not rows[-1]:
        return None, False
    end = rows[-1][-1].strip()
    if (not end.endswith("||") or not end[:-2].strip()
            or re.search(r'inf|∞', end, re.I)):
        return None, False
    rows[-1][-1] = end[:-2].strip()
    aligned = aligned_bbt_rows("\n".join(" | ".join(row) for row in rows))
    return aligned, aligned is not None


def missing_asymptote_limits(raw):
    rows = supplied_bbt_rows(raw)
    return bool(len(rows) == 3 and any(cell.replace('$', '').strip() == '||' for cell in rows[2][1:]))


def aligned_bbt_rows(raw):
    rows = supplied_bbt_rows(raw)
    if len(rows) != 3:
        return None
    clean = lambda s: s.replace('$', '').strip().replace('−', '-')
    def label(value):
        value = clean(value).replace(r'\prime', "'").replace('′', "'").replace('’', "'")
        return re.sub(r'[{}^\s]', '', value)
    variable, derivative, function = [label(row[0]) for row in rows]
    if (not variable or not re.search(r'[^\W\d_]', variable)
            or "'" not in derivative
            or not (derivative.replace("'", '') == function
                    or (function == 'y' and derivative == "f'(x)"))):
        return None
    points = [clean(s) for s in rows[0][1:] if clean(s)]
    n = len(points)
    if not 2 <= n <= 12:
        return None
    tokens = ' '.join(clean(s) for s in rows[1][1:])
    if not re.fullmatch(r'[+\-0|\s]+', tokens):
        return None
    tokens = re.findall(r'\|\||[+\-]|0', tokens)
    if len(tokens) != 2*n-3 or any(t not in ('+', '-') for t in tokens[::2]) or any(t not in ('0', '||') for t in tokens[1::2]):
        return None
    values = [clean(s) for s in rows[2][1:]]
    if len(values) == 2*n-1 and all(v in {r'\nearrow', r'\searrow', '↗', '↘'} for v in values[1::2]):
        values = values[::2]
    if len(values) != n or any(not v for v in values):
        return None
    for i, value in enumerate(values):
        split = [s.strip() for s in value.split('||')]
        marker = tokens[2*i-1] if 0 < i < n-1 else ''
        if (marker == '||' and (len(split) != 2 or not all(split))) or (marker != '||' and len(split) != 1):
            return None
    norm = lambda s: re.sub(r'(?<![A-Za-z])([+-]?)inf\b', lambda m: m[1]+r'\infty', s)
    y = []
    for i, value in enumerate(values):
        y.append(norm(value))
        if i < n-1:
            y.append('↗' if tokens[2*i] == '+' else '↘')
    return [[rows[0][0]] + [norm(v) for v in points], [rows[1][0]] + [''] + tokens + [''], [rows[2][0]] + y]
