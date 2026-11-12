# -*- coding: utf-8 -*-
from pathlib import Path
d = Path(__file__).resolve().parents[1] / "app.py"
text = d.read_text(encoding="utf-8")
start = text.index("def question_visual_html(question):")
end = text.index("\ndef latex_text(value):", start)
fn = text[start:end]
checks = {
    "webp_bbt_first": "render_bbt_to_webp_base64(raw_bbt)" in fn,
    "svg_only_fallback": "Chỉ khi WebP thất bại" in fn,
    "graph_done": "graph_done" in fn,
    "one_stream": "Một luồng đồ thị" in fn,
    "no_always_both": fn.count("Hình trong ngữ liệu nguồn") == 1 and "if not graph_done and has_source" in fn,
}
print(checks)
print("PASS" if all(checks.values()) else "FAIL")
