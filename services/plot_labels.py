"""Đặt nhãn điểm trên đồ thị Plotly: gộp điểm trùng, chọn vị trí tránh đè (dùng chung mọi Lab đồ thị).

Ca thật owner 09/11/2026: y = 3x³ − 2x + 1 có I(0; 1) trùng giao Oy (0; 1) -> hai nhãn,
nhãn Oy lệch cố định nên trông như một điểm khác; miền nghiệm Plotly nhãn đỉnh đè nhau.
Tính theo pixel ước lượng của vùng vẽ, không theo đơn vị trục.
"""
import math
import re

T1_CONTEXT_REVISION = 2026110914

# Thứ tự ưu tiên giữ nhãn khi nhiều đối tượng trùng một điểm.
PRIORITY = {'CĐ': 0, 'CT': 0, 'I': 1, 'Đỉnh': 1, 'Oy': 3, 'Ox': 4}


def plain_length(text):
    """Độ dài hiển thị gần đúng của nhãn (bỏ lệnh LaTeX, phân số tính theo phần dài hơn)."""
    s = str(text or '')
    s = re.sub(r'\\(?:d?frac)\{([^{}]*)\}\{([^{}]*)\}', lambda m: max(m[1], m[2], key=len), s)
    s = re.sub(r'\\(?:left|right|mathrm|sqrt|alpha|,|;|!)', '', s)
    s = re.sub(r'[${}\\_^]', '', s)
    return max(1, len(s))


def label_box(text, char_px=8.2, pad=10):
    tall = bool(re.search(r'\\d?frac|/', str(text)))
    return plain_length(text) * char_px + pad, (40 if tall else 24)


def merge_coincident(points, tol=1e-6):
    """points: dict(x, y, text, kind, name). Giữ một nhãn cho mỗi tọa độ; ghép tên chú giải các vai trò trùng."""
    kept = []
    for p in sorted(points, key=lambda q: PRIORITY.get(q.get('kind'), 2)):
        same = next((k for k in kept if abs(k['x'] - p['x']) <= tol * max(1.0, abs(p['x']))
                     and abs(k['y'] - p['y']) <= tol * max(1.0, abs(p['y']))), None)
        if same is None:
            kept.append(dict(p, aliases=[]))
        else:
            same['aliases'].append(p.get('name') or p.get('kind'))
    return kept


def _overlap(a, b):
    w = min(a[0] + a[2], b[0] + b[2]) - max(a[0], b[0])
    h = min(a[1] + a[3], b[1] + b[3]) - max(a[1], b[1])
    return w * h if w > 0 and h > 0 else 0.0


def place_labels(points, x_range, y_range, plot_w=620, plot_h=430, obstacles=()):
    """Trả danh sách (xshift, yshift) pixel cho từng điểm (theo thứ tự vào); yshift dương = lên trên.

    Tham lam theo ưu tiên: thử 8 hướng × 2 khoảng cách, chọn ô ít đè nhất với nhãn đã đặt,
    các điểm đánh dấu và mép vùng vẽ; ưu tiên hướng ra xa tâm cụm điểm.
    """
    x0, x1 = x_range
    y0, y1 = y_range
    sx = lambda x: (x - x0) / ((x1 - x0) or 1) * plot_w
    sy = lambda y: (y1 - y) / ((y1 - y0) or 1) * plot_h
    marks = [(sx(p['x']) - 7, sy(p['y']) - 7, 14, 14) for p in points]
    placed = [tuple(o) for o in obstacles]
    if points:
        gx = sum(sx(p['x']) for p in points) / len(points)
        gy = sum(sy(p['y']) for p in points) / len(points)
    else:
        gx, gy = plot_w / 2, plot_h / 2
    dirs = [(1, -1), (-1, -1), (1, 1), (-1, 1), (0, -1), (0, 1), (1, 0), (-1, 0)]
    order = sorted(range(len(points)), key=lambda i: PRIORITY.get(points[i].get('kind'), 2))
    shifts = [None] * len(points)
    for i in order:
        p = points[i]
        w, h = label_box(p['text'])
        cx, cy = sx(p['x']), sy(p['y'])
        ox, oy = cx - gx, cy - gy
        norm = math.hypot(ox, oy) or 1.0
        best = None
        for scale in (1.0, 1.7):
            for k, (ux, uy) in enumerate(dirs):
                dx = ux * (w / 2 + 9) * scale
                dy = uy * (h / 2 + 9) * scale
                box = (cx + dx - w / 2, cy + dy - h / 2, w, h)
                cost = sum(_overlap(box, b) for b in placed) * 3
                cost += sum(_overlap(box, m) for j, m in enumerate(marks) if j != i) * 2
                out_w = max(0, -box[0]) + max(0, box[0] + w - plot_w)
                out_h = max(0, -box[1]) + max(0, box[1] + h - plot_h)
                cost += (out_w * h + out_h * w) * 4
                cost += (scale - 1) * 60 + k * 0.5
                cost -= ((ux * ox + uy * oy) / norm) * 8  # ra xa tâm cụm
                if best is None or cost < best[0]:
                    best = (cost, dx, dy, box)
        placed.append(best[3])
        shifts[i] = (round(best[1]), round(-best[2]))
    return shifts


def axis_letter_annotations(x_range, y_range, color='#f8fafc', muted='#94a3b8'):
    """O, x, y đặt bằng pixel quanh gốc/đầu trục: không trôi khi khung hình đổi tỉ lệ."""
    x0, x1 = x_range
    y0, y1 = y_range
    out = []
    if x0 <= 0 <= x1 and y0 <= 0 <= y1:
        out.append(dict(x=0, y=0, text='<i>O</i>', showarrow=False, xshift=-11, yshift=-12,
                        font=dict(color=muted, size=15, family='Times New Roman')))
    out.append(dict(x=x1, y=0 if y0 <= 0 <= y1 else y0, text='<b>x</b>', showarrow=False, xshift=-8, yshift=-14,
                    font=dict(color=color, size=15, family='Times New Roman')))
    out.append(dict(x=0 if x0 <= 0 <= x1 else x0, y=y1, text='<b>y</b>', showarrow=False, xshift=-14, yshift=-8,
                    font=dict(color=color, size=15, family='Times New Roman')))
    return out
