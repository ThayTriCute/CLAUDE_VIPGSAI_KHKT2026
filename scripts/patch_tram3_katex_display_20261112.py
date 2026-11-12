# -*- coding: utf-8 -*-
"""Byte-safe: Trạm 3 testing/graded câu hỏi qua sanitize_katex_latex như Trạm 1."""
from pathlib import Path

APP = Path(__file__).resolve().parents[1] / "app.py"

OLD = (
    'st.markdown(f"**Câu {original_question_number(exam, q, idx+1)}:** '
    '{clean_question_bbt_text(q.get(\'q\'))}")'
)
NEW = (
    'st.markdown(f"**Câu {original_question_number(exam, q, idx+1)}:** '
    '{sanitize_katex_latex(clean_question_bbt_text(q.get(\'q\')))}")'
)


def main():
    data = APP.read_bytes()
    lf_before = data.count(b"\n") - data.count(b"\r\n")
    old_b = OLD.replace("\n", "\r\n").encode("utf-8") if "\n" in OLD else OLD.encode("utf-8")
    # Force CRLF line endings for the single-line patterns (no newlines)
    old_b = OLD.encode("utf-8")
    new_b = NEW.encode("utf-8")
    count = data.count(old_b)
    if count < 3:
        raise SystemExit(f"expected >=3 occurrences, found {count}")
    data2 = data.replace(old_b, new_b)
    lf_after = data2.count(b"\n") - data2.count(b"\r\n")
    if lf_after != lf_before:
        raise SystemExit(f"LF drift {lf_before}->{lf_after}")
    APP.write_bytes(data2)
    print("PATCH_OK katex", count, "->", data2.count(new_b), "lf_only", lf_after)


if __name__ == "__main__":
    main()
