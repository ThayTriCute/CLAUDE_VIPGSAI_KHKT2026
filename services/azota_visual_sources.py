"""Editable figures indexed by section and question for Azota editing."""

import re

from services.bbt_display_contract import export_bbt_rows


_PICTURE = re.compile(r"\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}", re.DOTALL)


def numeric_model_picture(model):
    """Use the existing numeric-function engines without defaults or answers."""
    from services.context_recovery import has_visual
    if not has_visual({'f': model}):
        return ''
    import precision_visual_engine as engine
    from services.exam_print_style import exam_tikz
    kind = model.get('type')
    if kind == 'func_1_1':
        a,b,c,d = (float(model[k]) for k in ('a','b','c','d'))
        if not c or a*d == b*c:
            return ''
        return exam_tikz(engine.build_rational_1_1_tikz(a,b,c,d))
    if kind == 'func_2_1':
        a,b,c,d,e = (float(model[k]) for k in ('a','b','c','d','e'))
        if not a or not d or a*e*e-b*d*e+c*d*d == 0:
            return ''
        return exam_tikz(engine.build_rational_2_1_tikz(a,b,c,d,e))
    return ''


def _bbt_picture(raw):
    rows, excluded_right = export_bbt_rows(raw)
    if rows is None:
        return ""
    points, signs, values = rows
    end = 2 * len(points) - 1
    lines = [
        r"\begin{tikzpicture}",
        rf"\draw (0,0) rectangle ({end},3.4);",
        rf"\draw (0,1.8) -- ({end},1.8) (0,2.6) -- ({end},2.6) (1,0) -- (1,3.4);",
    ]

    def node(x, y, value):
        value = value.replace("$", "").replace("∞", r"\infty")
        lines.append(r"\node at (%s,%s) {$%s$};" % (x, y, value))

    for y, label in zip((3, 2.2, 0.9), (points[0], signs[0], values[0])):
        node(0.5, y, label)
    for index, point in enumerate(points[1:]):
        x = 2 * index + 2
        node(x, 3, point)
        marker = signs[2 * index + 1]
        value = values[2 * index + 1]
        left_high = index > 0 and signs[2 * index] == "+"
        right_high = index < len(points) - 2 and signs[2 * index + 2] == "-"
        if excluded_right and index == len(points) - 2:
            lines.append(rf"\draw ({x-0.05},0) -- ({x-0.05},2.6) ({x+0.05},0) -- ({x+0.05},2.6);")
            node(x - 0.43, 1.42 if left_high else 0.38, value)
        elif marker == "||":
            lines.append(rf"\draw ({x-0.05},0) -- ({x-0.05},2.6) ({x+0.05},0) -- ({x+0.05},2.6);")
            left, right = value.split("||")
            node(x - 0.43, 1.42 if left_high else 0.38, left)
            node(x + 0.43, 1.42 if right_high else 0.38, right)
        else:
            if marker:
                node(x, 2.2, marker)
            node(x, 1.42 if left_high or right_high else 0.38, value)
        if index < len(points) - 2:
            sign = signs[2 * index + 2]
            node(x + 1, 2.2, sign)
            start, finish = (0.48, 1.31) if sign == "+" else (1.31, 0.48)
            lines.append(rf"\draw[->] ({x+0.49},{start}) -- ({x+1.51},{finish});")
    return "\n".join([*lines, r"\end{tikzpicture}"])


def export_azota_visual_sources(exam):
    """Keep editable sources separate from the text imported by the LMS."""
    blocks = []
    for part, label in (("p1", "I"), ("p2", "II"), ("p3", "III")):
        for number, question in enumerate(exam.get(part) or [], 1):
            from services.context_recovery import recover_visual
            if exam.get('subject') and exam.get('grade') is not None:
                question = recover_visual(question, exam['subject'], exam['grade'])
            composite = question.get("composite_visual")
            composite = composite if isinstance(composite, dict) else {}
            geometry = question.get('geom_3d')
            geometry = geometry if isinstance(geometry, dict) else {}
            pictures = _PICTURE.findall(str(question.get("tikz") or composite.get("tikz") or geometry.get('tikz') or ""))
            from services.exam_print_style import DRAWING_METHODS, exam_tikz
            if question.get('visual_recovery', {}).get('method') in DRAWING_METHODS:
                pictures = [exam_tikz(picture) for picture in pictures]
            if not pictures:
                models = composite.get('models') or [question.get('f')]
                for model in models:
                    picture = numeric_model_picture(model)
                    if picture:
                        pictures.append(picture)
            bbt = question.get("bbt")
            table = _bbt_picture(bbt) if bbt else ""
            notes = ["% Bảng biến thiên thiếu dữ kiện để dựng TikZ."] if bbt and not table else []
            if not pictures and question.get('f'):
                notes.append('% Mô hình hàm số chưa có bộ xuất TikZ tương ứng được xác minh.')
            if question.get('visual_recovery', {}).get('kind') == 'source_image':
                notes.append('% Chỉ có ảnh nguồn đã đối chiếu; chưa có mô hình TikZ được xác minh.')
            if table:
                pictures.append(table)
            if pictures or notes:
                blocks.append("\n".join([f"% Phần {label} - Câu {number}", *pictures, *notes]))
    return "\n\n".join(blocks)
