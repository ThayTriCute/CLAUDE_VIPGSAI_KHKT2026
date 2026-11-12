# -*- coding: utf-8 -*-
"""Ưu tiên hình nguồn đã render; WebP hệ số chỉ khi thiếu hình — một luồng."""
from pathlib import Path

APP = Path(__file__).resolve().parents[1] / "app.py"

OLD = """    # Một luồng đồ thị: render WebP từ hệ số trước; chỉ dùng hình nguồn khi render thất bại
    graph_done = False
    if coeff_ok:
        try:
            image = render_math_graph_to_webp_base64(dict(function))
        except Exception:
            image = \"\"
        if image:
            pieces.append(\"<img alt='Đồ thị theo hệ số đã cung cấp' style='max-width:100%' src='\" + html.escape(image, quote=True) + \"'/>\")
            graph_done = True
    if not graph_done and has_source:
        pieces.append(\"<img alt='Hình trong ngữ liệu nguồn' style='max-width:100%' src='\" + html.escape(source, quote=True) + \"'/>\")
        graph_done = True"""

NEW = """    # Một luồng đồ thị: ưu tiên hình nguồn (đã render); WebP hệ số chỉ khi thiếu hình nguồn
    graph_done = False
    if has_source:
        pieces.append(\"<img alt='Hình trong ngữ liệu nguồn' style='max-width:100%' src='\" + html.escape(source, quote=True) + \"'/>\")
        graph_done = True
    elif coeff_ok:
        try:
            image = render_math_graph_to_webp_base64(dict(function))
        except Exception:
            image = \"\"
        if image:
            pieces.append(\"<img alt='Đồ thị theo hệ số đã cung cấp' style='max-width:100%' src='\" + html.escape(image, quote=True) + \"'/>\")
            graph_done = True"""


def main():
    data = APP.read_bytes()
    lf0 = data.count(b"\n") - data.count(b"\r\n")
    # Unescape the \" in the Python source strings above - they were written with escaped quotes
    # Actually OLD/NEW use \" inside normal \"\"\" which means literal backslash-quote. Fix:
    old = OLD.replace('\\"', '"').replace("\n", "\r\n").encode("utf-8")
    new = NEW.replace('\\"', '"').replace("\n", "\r\n").encode("utf-8")
    if old not in data:
        raise SystemExit("OLD graph block not found")
    data2 = data.replace(old, new, 1)
    lf1 = data2.count(b"\n") - data2.count(b"\r\n")
    if lf1 != lf0:
        raise SystemExit(f"LF drift {lf0}->{lf1}")
    APP.write_bytes(data2)
    print("PATCH_OK source-first", "lf_only", lf1)


if __name__ == "__main__":
    main()
