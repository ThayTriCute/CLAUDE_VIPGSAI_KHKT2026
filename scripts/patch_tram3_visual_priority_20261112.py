# -*- coding: utf-8 -*-
"""Byte-safe patch: BBT/đồ thị ưu tiên WebP; SVG chỉ khi render chính thất bại; một luồng đồ thị."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "app.py"

OLD_QVH = """def question_visual_html(question):
    \"\"\"Render only supplied visual data; never guess a new graph from an answer.\"\"\"
    pieces = []
    raw_bbt = str(question.get(\"bbt\") or \"\").strip()
    if raw_bbt and raw_bbt.lower() not in {\"null\", \"none\", \"{}\"}:
        from services.bbt_display_contract import aligned_bbt_rows
        aligned = aligned_bbt_rows(raw_bbt)
        if aligned:
            safe_rows = [[html.escape(cell) for cell in row] for row in aligned]
            pieces.append(_build_svg_bbt_from_rows(*safe_rows))
        else:
            # Unknown/two-row formats remain visible without splitting double bars.
            pieces.append(\"<pre style='overflow-x:auto;white-space:pre'>\" + html.escape(raw_bbt) + \"</pre>\")
    grouped = question.get(\"mslgn_data\")
    if isinstance(grouped, dict):
        groups, frequencies = grouped.get(\"groups\", []), grouped.get(\"freq\", [])
        if groups and len(groups) == len(frequencies):
            cells = \"\".join(\"<tr>\" + \"\".join(\"<td style='border:1px solid #64748b;padding:6px'>\" + html.escape(str(value)) + \"</td>\" for value in row) + \"</tr>\" for row in (groups, frequencies))
            pieces.append(\"<table>\" + cells + \"</table>\")
    for visual_key in (\"composite_visual\", \"geom_3d\", \"thermal_pv_visual\", \"food_web_visual\"):
        visual = question.get(visual_key)
        if isinstance(visual, dict) and visual.get(\"svg\"):
            pieces.append(sanitize_svg_for_markdown(str(visual[\"svg\"])))
    function = question.get(\"f\")
    required = {\"func_3\": {\"a\", \"b\", \"c\", \"d\"}, \"cubic\": {\"a\", \"b\", \"c\", \"d\"}, \"func_1_1\": {\"a\", \"b\", \"c\", \"d\"}, \"func_2_1\": {\"a\", \"b\", \"c\", \"d\", \"e\"}, \"parabola\": {\"a\", \"b\", \"c\"}, \"func_2\": {\"a\", \"b\", \"c\"}}
    if isinstance(function, dict) and function.get(\"type\") in required and required[function[\"type\"]] <= function.keys():
        image = render_math_graph_to_webp_base64(dict(function))
        if image:
            pieces.append(\"<img alt='Đồ thị theo hệ số đã cung cấp' style='max-width:100%' src='\" + html.escape(image, quote=True) + \"'/>\")
    image = question.get(\"image_base64\") or question.get(\"image_url\") or question.get(\"image\")
    if isinstance(image, str) and image.startswith((\"data:image/png;base64,\", \"data:image/jpeg;base64,\", \"data:image/webp;base64,\")):
        pieces.append(\"<img alt='Hình trong ngữ liệu nguồn' style='max-width:100%' src='\" + html.escape(image, quote=True) + \"'/>\")
    if not pieces and any(term in str(question.get(\"q\", \"\")).lower() for term in (\"hình vẽ bên\", \"hình bên\", \"đồ thị như hình\", \"bảng biến thiên như hình\")):
        pieces.append(\"<p style='color:#b45309'>Thiếu dữ liệu hình gốc để đối chiếu; không tự dựng hình mẫu. Cần giáo viên kiểm tra câu này.</p>\")
    return \"\\n\".join(pieces)"""

NEW_QVH = '''def question_visual_html(question):
    """Render only supplied visual data; never guess a new graph from an answer.

    Ưu tiên ảnh WebP đã render; chỉ xuất SVG khi render chính thất bại.
    Đồ thị: một luồng duy nhất (WebP hệ số → hình nguồn nếu fail; không hiện kép).
    """
    pieces = []
    raw_bbt = str(question.get("bbt") or "").strip()
    if raw_bbt and raw_bbt.lower() not in {"null", "none", "{}"}:
        b64_bbt = ""
        try:
            b64_bbt = render_bbt_to_webp_base64(raw_bbt) or ""
        except Exception:
            b64_bbt = ""
        if b64_bbt:
            pieces.append(
                "<div style='display:flex;justify-content:center;margin:8px auto'>"
                "<img alt='Bảng biến thiên chuẩn Bộ GD&ĐT' style='max-width:100%;height:auto;border-radius:6px' src='"
                + html.escape(b64_bbt, quote=True) + "'/></div>"
            )
        else:
            # Chỉ khi WebP thất bại mới xuất SVG / pre an toàn (không để \\nearrow lộ KaTeX)
            from services.bbt_display_contract import aligned_bbt_rows
            aligned = aligned_bbt_rows(raw_bbt)
            svg_or_html = ""
            if aligned:
                safe_rows = [[html.escape(cell) for cell in row] for row in aligned]
                svg_or_html = _build_svg_bbt_from_rows(*safe_rows) or ""
            if not svg_or_html:
                try:
                    svg_or_html = format_pedagogical_bbt_html(raw_bbt, is_dark_mode=True) or ""
                except Exception:
                    svg_or_html = ""
            if svg_or_html:
                pieces.append(svg_or_html)
            else:
                safe_txt = re.sub(r'\\\\+nearrow\\b|\\\\nearrow', '↗', raw_bbt)
                safe_txt = re.sub(r'\\\\+searrow\\b|\\\\searrow', '↘', safe_txt)
                safe_txt = safe_txt.replace(r'\\infty', '∞').replace('+∞', '+∞').replace('-∞', '-∞')
                safe_txt = safe_txt.replace(r'+\\infty', '+∞').replace(r'-\\infty', '-∞')
                pieces.append("<pre style='overflow-x:auto;white-space:pre'>" + html.escape(safe_txt) + "</pre>")
    grouped = question.get("mslgn_data")
    if isinstance(grouped, dict):
        groups, frequencies = grouped.get("groups", []), grouped.get("freq", [])
        if groups and len(groups) == len(frequencies):
            cells = "".join("<tr>" + "".join("<td style='border:1px solid #64748b;padding:6px'>" + html.escape(str(value)) + "</td>" for value in row) + "</tr>" for row in (groups, frequencies))
            pieces.append("<table>" + cells + "</table>")
    for visual_key in ("composite_visual", "geom_3d", "thermal_pv_visual", "food_web_visual"):
        visual = question.get(visual_key)
        if isinstance(visual, dict) and visual.get("svg"):
            pieces.append(sanitize_svg_for_markdown(str(visual["svg"])))
    function = question.get("f")
    required = {"func_3": {"a", "b", "c", "d"}, "cubic": {"a", "b", "c", "d"}, "func_1_1": {"a", "b", "c", "d"}, "func_2_1": {"a", "b", "c", "d", "e"}, "parabola": {"a", "b", "c"}, "func_2": {"a", "b", "c"}}
    coeff_ok = isinstance(function, dict) and function.get("type") in required and required[function["type"]] <= function.keys()
    source = question.get("image_base64") or question.get("image_url") or question.get("image")
    has_source = isinstance(source, str) and source.startswith(("data:image/png;base64,", "data:image/jpeg;base64,", "data:image/webp;base64,"))
    # Một luồng đồ thị: render WebP từ hệ số trước; chỉ dùng hình nguồn khi render thất bại
    graph_done = False
    if coeff_ok:
        try:
            image = render_math_graph_to_webp_base64(dict(function))
        except Exception:
            image = ""
        if image:
            pieces.append("<img alt='Đồ thị theo hệ số đã cung cấp' style='max-width:100%' src='" + html.escape(image, quote=True) + "'/>")
            graph_done = True
    if not graph_done and has_source:
        pieces.append("<img alt='Hình trong ngữ liệu nguồn' style='max-width:100%' src='" + html.escape(source, quote=True) + "'/>")
        graph_done = True
    if not pieces and any(term in str(question.get("q", "")).lower() for term in ("hình vẽ bên", "hình bên", "đồ thị như hình", "bảng biến thiên như hình")):
        pieces.append("<p style='color:#b45309'>Thiếu dữ liệu hình gốc để đối chiếu; không tự dựng hình mẫu. Cần giáo viên kiểm tra câu này.</p>")
    return "\\n".join(pieces)'''

OLD_RFV = """def render_fast_visual(q, q_id=None):
        if not isinstance(q, dict):
            return
        rendered = question_visual_html(deepcopy(q))
        if rendered:
            st.markdown(rendered, unsafe_allow_html=True)"""

NEW_RFV = """def render_fast_visual(q, q_id=None):
        if not isinstance(q, dict):
            return
        # question_visual_html: WebP trước, SVG chỉ khi fail; đồ thị một luồng
        rendered = question_visual_html(deepcopy(q))
        if rendered:
            st.markdown(rendered, unsafe_allow_html=True)"""


def _to_crlf(text: str) -> bytes:
    return text.replace("\r\n", "\n").replace("\n", "\r\n").encode("utf-8")


def main():
    data = APP.read_bytes()
    lf_before = data.count(b"\n") - data.count(b"\r\n")
    old_q = _to_crlf(OLD_QVH)
    new_q = _to_crlf(NEW_QVH)
    old_r = _to_crlf(OLD_RFV)
    new_r = _to_crlf(NEW_RFV)
    if old_q not in data:
        raise SystemExit("OLD question_visual_html not found (exact CRLF match failed)")
    if data.count(old_q) != 1:
        raise SystemExit(f"question_visual_html matches={data.count(old_q)}")
    if old_r not in data:
        raise SystemExit("OLD render_fast_visual not found")
    data2 = data.replace(old_q, new_q, 1).replace(old_r, new_r, 1)
    lf_after = data2.count(b"\n") - data2.count(b"\r\n")
    if lf_after != lf_before:
        raise SystemExit(f"LF-only drift: {lf_before} -> {lf_after}")
    APP.write_bytes(data2)
    print("PATCH_OK", APP)
    print("bytes", len(data), "->", len(data2), "lf_only", lf_after)


if __name__ == "__main__":
    main()
