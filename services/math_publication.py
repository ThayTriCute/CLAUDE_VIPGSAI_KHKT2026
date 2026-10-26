"""Parse math with the packaged KaTeX/mhchem before publishing academic text.

Rendering success is syntax evidence, never proof of scientific correctness.
"""
from collections import OrderedDict
from pathlib import Path
import hashlib
import html
import re
import threading
from functools import lru_cache

TOKENS = re.compile(r"```[\s\S]*?```|~~~[\s\S]*?~~~|`[^`\n]*`|(?<!\\)\$\$[\s\S]*?(?<!\\)\$\$|\\\[[\s\S]*?\\\]|\\\([^\n]*?\\\)|(?<!\\)\$(?!\$)[^\n$]+?(?<!\\)\$")
NAKED = re.compile(r"\\(?:frac|dfrac|tfrac|sqrt|begin|end|ce|pu|omega|Omega|alpha|beta|Delta|int|sum|vec|mathbb|mathrm|left|right)\b")
UNSAFE = re.compile(r"\\(?:href|url|includegraphics|html\w*|gdef|def|newcommand|renewcommand|global|catcode)\b")
_lock = threading.Lock()
_context = None
_cache = OrderedDict()


class MathPublicationError(ValueError):
    pass


def normalize_real_aliases(text):
    """Legacy real-number aliases, with explicit math delimiters; preserve code."""
    def rewrite(value, math=False):
        value = re.sub(r"(?i)\bD\s*=\s*R\b", lambda _: r"D = \mathbb{R}" if math else r"$D = \mathbb{R}$", value)
        return re.sub(r"\\R\b", lambda _: r"\mathbb{R}" if math else r"$\mathbb{R}$", value)
    chunks, last = [], 0
    for match in TOKENS.finditer(text):
        chunks.append(rewrite(text[last:match.start()]))
        raw = match[0]
        chunks.append(raw if raw.startswith(("`", "~~~")) else rewrite(raw, math=True))
        last = match.end()
    chunks.append(rewrite(text[last:]))
    return "".join(chunks)


def segments(text):
    result, outside, last = [], [], 0
    for match in TOKENS.finditer(text):
        raw = match[0]
        outside.append(text[last:match.start()])
        last = match.end()
        if raw.startswith(("`", "~~~")):
            continue
        display = raw.startswith(("$$", r"\["))
        width = 2 if raw.startswith(("$$", r"\[", r"\(")) else 1
        result.append((match.start(), match.end(), raw[width:-width], display))
    outside.append(text[last:])
    residual = " ".join(outside)
    if re.search(r"(?<!\\)\$|\\[\[\]()]", residual):
        raise MathPublicationError("Dấu phân cách công thức chưa khép đúng; cần sửa bản nháp trước khi hiển thị.")
    if NAKED.search(residual):
        raise MathPublicationError("Có lệnh LaTeX nằm ngoài vùng toán; cần sửa dấu phân cách trước khi hiển thị.")
    return result


def _engine():
    global _context
    if _context is None:
        from py_mini_racer import MiniRacer
        ctx = MiniRacer()
        try:
            ctx.set_hard_memory_limit(96 * 1024 * 1024)
            vendor = Path(__file__).resolve().parents[1] / "assets/vendor/katex/dist"
            ctx.eval((vendor / "katex.min.js").read_text(encoding="utf-8"), timeout_sec=3)
            ctx.eval("""var gsaiChemMacros={}; var gsaiDefineMacro=katex.__defineMacro;
              katex.__defineMacro=function(name,body){gsaiChemMacros[name]=body;gsaiDefineMacro(name,body);};""", timeout_sec=1)
            ctx.eval((vendor / "contrib/mhchem.min.js").read_text(encoding="utf-8"), timeout_sec=3)
            ctx.eval("""katex.__defineMacro=gsaiDefineMacro;
              function gsaiChemTex(command,body){
                var tokens=Array.from(body).map(function(text,index){return {text:text,loc:{start:index}};}).reverse();
                var value=gsaiChemMacros['\\\\'+command]({consumeArgs:function(){return [tokens];}});
                Object.keys(gsaiChemMacros).forEach(function(name){if(typeof gsaiChemMacros[name]==='string')value=value.split(name).join(gsaiChemMacros[name]);});
                return value;
              }""", timeout_sec=1)
            ctx.eval("""function gsaiMathBatch(items) {
              return items.map(function(item) {
                try { return {html:katex.renderToString(item[0], {displayMode:item[1],
                  throwOnError:true, strict:'warn', maxExpand:1000, maxSize:20,
                  trust:function(){throw Error('Unsupported trusted command');}, macros:{}}), error:null}; }
                catch(e) { return {html:null, error:String(e.message).slice(0,180)}; }
              });
            }""", timeout_sec=1)
        except Exception:
            ctx.close()
            raise
        _context = ctx
    return _context


def render_formulas(items):
    """One bounded V8 context per process, serialized; small, bounded formula cache."""
    global _context
    if len(items) > 500 or any(len(tex) > 4096 or UNSAFE.search(tex) for tex, _ in items):
        raise MathPublicationError("Công thức vượt giới hạn hoặc chứa lệnh không hỗ trợ; cần kiểm tra bản nháp.")
    if not items:
        return []
    if not _lock.acquire(timeout=4):
        raise MathPublicationError("Bộ kiểm tra công thức đang bận; hãy thử lại, chưa công bố nội dung này.")
    try:
        missing = list(dict.fromkeys(item for item in items if item not in _cache))
        if missing:
            try:
                checked = _engine().call("gsaiMathBatch", missing, timeout_sec=3)
            except Exception as error:
                if _context is not None:
                    _context.close()
                    _context = None
                _cache.clear()
                raise MathPublicationError("Chưa chạy được bộ kiểm tra KaTeX; chưa công bố bản nháp này.") from error
            current = dict(zip(missing, checked))
        else:
            current = {}
        values = [current.get(item, _cache.get(item)) for item in items]
        result = []
        for item, value in zip(items, values):
            if value["error"]:
                raise MathPublicationError("KaTeX chưa dựng được công thức: " + value["error"])
            result.append(value["html"])
            # Keep at most 128 short renderings, not unbounded lesson strings.
            if len(value["html"]) <= 24000:
                _cache[item] = value
                _cache.move_to_end(item)
                while len(_cache) > 128:
                    _cache.popitem(last=False)
        return result
    finally:
        _lock.release()


def validate_math_text(text):
    if not isinstance(text, str):
        return text
    if len(text) > 250000:
        raise MathPublicationError("Nội dung vượt giới hạn kiểm tra công thức trong một lượt.")
    parts = segments(text)
    render_formulas([(p[2], p[3]) for p in parts])
    return text


@lru_cache(maxsize=128)
def native_radio_label(text):
    """Expand mhchem through its own parser for native full-option radio labels.

    The original option remains the widget value and grading source. Streamlit's
    native KaTeX does not consistently load the mhchem extension.
    """
    text = str(text)
    validate_math_text(text)
    chunks, last = [], 0
    for start, end, tex, display in segments(text):
        expanded, cursor = [], 0
        while True:
            match = re.search(r"\\(ce|pu)\s*\{", tex[cursor:])
            if not match:
                expanded.append(tex[cursor:])
                break
            begin = cursor + match.start()
            body_start = cursor + match.end()
            position, depth = body_start, 1
            while position < len(tex) and depth:
                if tex[position] == "{" and (position == 0 or tex[position-1] != "\\"):
                    depth += 1
                elif tex[position] == "}" and (position == 0 or tex[position-1] != "\\"):
                    depth -= 1
                position += 1
            if depth:
                raise MathPublicationError("Nhóm công thức hóa học chưa đóng.")
            if not _lock.acquire(timeout=4):
                raise MathPublicationError("Bộ dựng công thức đang bận.")
            try:
                value = _engine().call("gsaiChemTex", match[1], tex[body_start:position-1], timeout_sec=3)
            finally:
                _lock.release()
            if len(value) > 24000:
                raise MathPublicationError("Công thức hóa học quá dài để dựng phương án.")
            expanded.extend((tex[cursor:begin], value))
            cursor = position
        formula = "".join(expanded)
        chunks.extend((text[last:start], "$" + formula + "$"))
        last = end
    chunks.append(text[last:])
    return "".join(chunks)


def escape_source_html(text):
    """Escape source HTML outside code/math before adding trusted local diagrams."""
    chunks, last = [], 0
    def escape_tags(value):
        return re.sub(r"<(?=[A-Za-z/!?])", "&lt;", value)
    for match in TOKENS.finditer(text):
        chunks.extend((escape_tags(text[last:match.start()]), match[0]))
        last = match.end()
    chunks.append(escape_tags(text[last:]))
    return "".join(chunks)


def math_for_web(text, trusted_layout=False):
    """Use the checked renderer instead of relying on another frontend version."""
    text = str(text or "")
    if len(text) > 250000:
        raise MathPublicationError("Nội dung quá dài để hiển thị trong một lượt.")
    parts = segments(text)
    rendered = render_formulas([(p[2], p[3]) for p in parts])
    from markdown_it import MarkdownIt
    nonce = hashlib.sha256(text.encode()).hexdigest()[:16]
    chunks, replacements, last = [], {}, 0
    for index, (part, formula_html) in enumerate(zip(parts, rendered)):
        token = f"GSAIMATH{nonce}N{index}END"
        chunks.extend((text[last:part[0]], token))
        replacements[token] = formula_html
        last = part[1]
    chunks.append(text[last:])
    md = MarkdownIt("commonmark", {"html": trusted_layout}).enable("table")
    md.renderer.rules["image"] = lambda tokens, idx, options, env: html.escape(tokens[idx].content)
    body = md.render("".join(chunks))
    for token, formula_html in replacements.items():
        body = body.replace(token, formula_html)
    return body


def validate_exam_math(exam):
    fields = {"q", "question", "t", "text", "explain", "ans", "answer", "opt", "options", "intro", "passage"}
    total = 0
    def walk(value, selected=False):
        nonlocal total
        if isinstance(value, dict):
            for key, child in value.items():
                if key not in {"image_base64", "svg_geom", "svg_comp", "bbt", "cognitive_audit", "curriculum_audit"}:
                    walk(child, key in fields)
        elif isinstance(value, list):
            for child in value:
                walk(child, selected)
        elif isinstance(value, str) and selected:
            total += len(value)
            if total > 500000:
                raise MathPublicationError("Đề vượt giới hạn tổng nội dung kiểm tra công thức.")
            validate_math_text(value)
    walk(exam)
    return exam


def generate_checked_text(prompt, generator, validator):
    """At most one repair attempt, then retain a clear failure instead of publishing."""
    from services.lesson_contract import LessonContractError
    from services.academic_scope import AcademicScopeError
    from services.curriculum_policy import AcademicPolicyError
    text = generator(prompt)
    try:
        return validator(text)
    except (MathPublicationError, LessonContractError, AcademicScopeError, AcademicPolicyError) as error:
        if isinstance(error, (LessonContractError, AcademicScopeError, AcademicPolicyError)):
            instruction = ("Sửa đầy đủ cấu trúc và tất cả câu hỏi/hướng dẫn chưa hợp lệ trong bản nháp. "
                           "Giữ nguyên môn, lớp, chủ đề, tùy biến và các phần đúng. "
                           "Với câu thiếu hình/dữ kiện không thể phục dựng: được biên soạn lại TOÀN BỘ câu đó cùng bốn phương án và khóa chấm, "
                           "dùng dữ kiện tường minh và kiểm tra đúng một đáp án; không sửa riêng một phương án để ép khớp. "
                           "Ưu tiên câu tự đủ dữ kiện bằng văn bản/công thức, không tham chiếu hình hoặc bảng không có trong đầu ra. "
                           "Mỗi gợi mở và mỗi bước Pólya là câu hỏi tiếng Việt bám đúng đề, không giải hộ hoặc nêu kết quả. "
                           "Viết nhãn trường trên dòng riêng dạng ĐÁP ÁN: B, GỢI MỞ SOCRATIC: ...?; "
                           "bốn tiêu đề Bước 1–4 trên dòng riêng, câu hỏi ở dòng kế tiếp. "
                           "Xuất lại đủ ba phần, ba câu trắc nghiệm và hai bài tự luận.")
        else:
            instruction = "Sửa cú pháp/dấu phân cách, giữ nguyên nhiệm vụ, số liệu và ý nghĩa; không thêm kiến thức hoặc đổi môn/lớp. Xuất lại đầy đủ định dạng yêu cầu."
        repair = (prompt + "\nBản nháp chưa đạt kiểm tra công thức/cấu trúc bài học: " + str(error)[:240]
                  + "\n" + instruction + "\nBản nháp cần sửa:\n"
                  + str(text)[:250000])
        repaired_text = generator(repair)
        try:
            return validator(repaired_text)
        except (MathPublicationError, LessonContractError, AcademicScopeError, AcademicPolicyError) as final_error:
            # Keep the same exception type/message. Only the authenticated app
            # diagnostic path may use this draft; never interpolate it into UI.
            final_error.rejected_draft = str(repaired_text)[:250000]
            final_error.validation_attempts = 2
            raise
