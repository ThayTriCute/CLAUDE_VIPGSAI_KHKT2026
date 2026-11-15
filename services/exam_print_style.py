"""Exam export presentation, separate from source data and learning UI.

These are application design choices informed by reviewed official-paper
reprints, not a Ministry certification or prescribed universal typography.
"""
import re
import xml.etree.ElementTree as ET


DRAWING_METHODS = frozenset({
    "explicit_window_shape", "explicit_led_coordinates", "supplied_box_sphere_model",
    "explicit_square_pyramid_net", "reviewed_rational_constraints", "reviewed_diagram",
})


def exam_svg(svg):
    """Restyle known labelled geometric drawings; retain all geometry/patterns.

    Call only for the data-driven drawings in DRAWING_METHODS, never arbitrary
    source photos or charts whose series are distinguished only by colour.
    """
    if not isinstance(svg, str) or len(svg) > 2_000_000:
        return svg
    try:
        root = ET.fromstring(svg)
    except ET.ParseError:
        return svg
    ET.register_namespace('', 'http://www.w3.org/2000/svg')
    root.set('color', '#000000')
    def paint(value, shaded=False):
        if value.lower().strip() in {'none', 'transparent', 'white', '#fff', '#ffffff'} or value.startswith('url('):
            return value
        if shaded:
            from PIL import ImageColor
            try:
                rgb = ImageColor.getrgb(value)[:3]
                level = round(sum(c*w for c, w in zip(rgb, (.2126, .7152, .0722))))
                return '#%02x%02x%02x' % (level, level, level)
            except ValueError:
                pass
        return '#000000'
    for node in root.iter():
        area = node.tag.rsplit('}', 1)[-1] in {'polygon', 'rect', 'ellipse'}
        for name in ('stroke', 'fill', 'color'):
            if name in node.attrib:
                node.set(name, paint(node.get(name), shaded=area and name == 'fill'))
        if 'style' in node.attrib:
            node.set('style', re.sub(
                r'(?<![\w-])(stroke|fill|color)\s*:\s*([^;]+)',
                lambda m: m[1] + ':' + paint(m[2], shaded=area and m[1] == 'fill'), node.get('style')))
    return ET.tostring(root, encoding='unicode')


def exam_bbt_html(rendered):
    """Retain the existing table/arrow renderer, removing its teaching banner."""
    rendered = re.sub(r'<div style="[^"]*">📐 Bảng Biến Thiên Chuẩn Sư Phạm \(CT GDPT 2018\)</div>', '', rendered)
    return (
        '<style>.exam-print-bbt{color:#000;background:#fff;margin:10px auto;max-width:100%}'
        '.exam-print-bbt div{background:#fff!important;color:#000!important;'
        'box-shadow:none!important;border-radius:0!important;border-color:#000!important}'
        '.exam-print-bbt table{color:#000!important;border-collapse:collapse}'
        '.exam-print-bbt td,.exam-print-bbt span{background:#fff!important;color:#000!important;border-color:#000!important}'
        '.exam-print-bbt svg line{stroke:#000!important}'
        '.exam-print-bbt svg path{fill:#000!important}</style>'
        '<div class="exam-print-bbt">' + rendered + '</div>'
    )


def picture_width_inches(width, height, available_width=6.5, available_height=4.2):
    """Fit without aspect distortion or expanding a tiny raster to page width."""
    if width <= 0 or height <= 0:
        raise ValueError('Invalid picture dimensions')
    return min(available_width, available_height * width / height, width / 120)


def exam_tikz(picture):
    """Known renderer paint options only; never rewrite coordinates or labels."""
    return re.sub(r'([\[,=]\s*)(?:blue|red|orange|teal)(?=\s*[,\]])',
                  r'\1black', picture)
