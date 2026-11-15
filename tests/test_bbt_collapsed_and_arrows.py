# -*- coding: utf-8 -*-
"""BBT: tách bảng dồn 1 dòng, không phá \\nearrow, khóa mũi tên theo dấu y'."""
from __future__ import annotations

import unittest

from services.bbt_display_contract import (
    expand_collapsed_bbt_line,
    expand_collapsed_bbt_prose,
    repair_bbt_arrows_from_signs,
    supplied_bbt_rows,
    aligned_bbt_rows,
)
from services.function_visuals import with_function_visuals
from services.lesson_export import lesson_body_html, build_lesson_html


# Case thật từ Bai_hoc_GSAI-434B92BCF3E2: BBT (x^2-x+1)/(x-1) AI ghi +∞ ↗ 3 (sai).
_COLLAPSED_WRONG = (
    r"| $x$ | $-\infty$ | | $0$ | | $1$ | | $2$ | | $+\infty$ | "
    r"| :--- | :--- | :---: | :---: | :---: | :||: | :---: | :---: | :---: | ---: | "
    r"| $y'$ | | $+$ | $0$ | $-$ | || | $-$ | $0$ | $+$ | | "
    r"| $y$ | $-\infty$ | $\nearrow$ | $-1$ | $\searrow$ | $-\infty$ || $+\infty$ | $\nearrow$ | $3$ | $\nearrow$ | $+\infty$ |"
)

_COLLAPSED_OK = (
    r"| $x$ | $-\infty$ | | $-1$ | | $+\infty$ | "
    r"| :--- | :--- | :---: | :||: | :---: | ---: | "
    r"| $y'$ | | $+$ | || | $+$ | | "
    r"| $y$ | $2$ | $\nearrow$ | $+\infty$ || $-\infty$ | $\nearrow$ | $2$ |"
)


class CollapsedBbtTests(unittest.TestCase):
    def test_expand_collapsed_line_into_four_rows(self):
        out = expand_collapsed_bbt_line(_COLLAPSED_WRONG)
        self.assertEqual(out.count("\n"), 3)
        self.assertIn("| $y'$ |", out)
        self.assertTrue(out.strip().startswith("| $x$"))

    def test_nearrow_survives_supplied_rows(self):
        expanded = expand_collapsed_bbt_line(_COLLAPSED_WRONG)
        rows = supplied_bbt_rows(expanded)
        self.assertEqual(len(rows), 3)
        joined = " ".join(" ".join(r) for r in rows)
        self.assertIn("nearrow", joined)
        self.assertNotIn("earrow", joined.replace("nearrow", "").replace("searrow", ""))

    def test_repair_arrows_follow_yprime_signs(self):
        expanded = expand_collapsed_bbt_line(_COLLAPSED_WRONG)
        repaired = repair_bbt_arrows_from_signs(expanded)
        # Interval (1;2) has y' = − → must be searrow, not nearrow before 3.
        y_line = [ln for ln in repaired.splitlines() if ln.strip().startswith("| $y$")][0]
        # After || the next arrow before 3 must be searrow
        after_pole = y_line.split("||", 1)[1]
        self.assertIn(r"\searrow", after_pole)
        self.assertNotIn(r"\nearrow$", after_pole.split("$3$")[0] if "$3$" in after_pole else after_pole)
        # Count: signs + - - + → nearrow, searrow, searrow, nearrow
        arrows = []
        import re
        for m in re.finditer(r"\\nearrow|\\searrow", y_line):
            arrows.append(m.group(0))
        self.assertEqual(arrows, [r"\nearrow", r"\searrow", r"\searrow", r"\nearrow"])

    def test_lesson_body_html_makes_table_not_pipe_paragraph(self):
        body = lesson_body_html("Bảng biến thiên:\n\n" + _COLLAPSED_WRONG + "\n\nĐồ thị.")
        self.assertIn("<table", body)
        self.assertNotIn("<p>|", body)

    def test_with_function_visuals_replaces_pipe_bbt_in_place(self):
        lesson = (
            r"Ví dụ $y=\frac{2x-1}{x+1}$."
            + "\n\nBảng biến thiên:\n\n"
            + _COLLAPSED_OK
            + "\n\n"
            + r"Ví dụ $y=\frac{x^2-x+1}{x-1}$."
            + "\n\nBảng biến thiên:\n\n"
            + _COLLAPSED_WRONG
            + "\n"
        )
        html_body = lesson_body_html(lesson)
        result = with_function_visuals(html_body, "Khảo sát ba hàm số cơ bản", lesson)
        self.assertEqual(result.count('class="verified-function-visuals"'), 2)
        # Không còn BBT AI dạng ống / bảng markdown sai trong bài.
        self.assertNotIn("<p>|", result)
        self.assertNotIn(r"+\infty$ | $\nearrow$ | $3$", result)
        # Verified của phân thức 2/1 có mũi tên giảm đúng (path DOWN trên khoảng sau cực).
        self.assertIn(r"y=\frac{x^{2} - x + 1}{x - 1}", result)
        self.assertIn(r"y=\frac{2 x - 1}{x + 1}", result)

    def test_export_handwritten_no_orphan_pipe_bbt(self):
        lesson = (
            r"Khảo sát $y=\frac{x^2-x+1}{x-1}$."
            + "\n\nBảng biến thiên:\n\n"
            + _COLLAPSED_WRONG
        )
        page = build_lesson_html("Toán học", 12, "Khảo sát hàm hữu tỉ", lesson, "handwritten")
        self.assertIn('class="verified-function-visuals"', page)
        self.assertNotIn("<p>| $x$", page)
        # Arrow repair also applied if table somehow remains
        if "<table" in page:
            self.assertNotIn(r"$+\infty$ | $\nearrow$ | $3$", page)


if __name__ == "__main__":
    unittest.main()
