"""Lab ảo: dữ liệu do AI trả về không được làm sập giao diện.

AI có thể trả hệ số ngoài khoảng thanh trượt (a = 7 khi thanh trượt chỉ tới 4), số dạng
chuỗi ("2,5", "1/2"), null, hoặc không phải object. Trước đây các trường hợp này gây lỗi
đỏ của Streamlit và lặp lại ở mọi lần tải vì dữ liệu nằm trong phiên.
"""
import math
import re
from fractions import Fraction

_NUMERIC_TEXT = re.compile(r"\s*[-+]?\d+(?:[.,]\d+)?(?:\s*/\s*[-+]?\d+(?:[.,]\d+)?)?\s*")


def to_number(value):
    """Số hữu hạn từ số hoặc chuỗi số ('2,5', '1/2'); None nếu không phải số."""
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return value if math.isfinite(value) else None
    if isinstance(value, str) and _NUMERIC_TEXT.fullmatch(value):
        text = value.replace(",", ".").replace(" ", "")
        try:
            number = float(Fraction(text)) if "/" in text else float(text)
        except (ValueError, ZeroDivisionError):
            return None
        return number if math.isfinite(number) else None
    return None


def sanitize_lab_data(data):
    """Bản sao dict Lab: bỏ giá trị null/NaN, đổi chuỗi số thành số. None nếu không dùng được."""
    if not isinstance(data, dict) or not isinstance(data.get("type"), str) or not data["type"].strip():
        return None
    clean = {}
    for key, value in data.items():
        if value is None or (isinstance(value, float) and not math.isfinite(value)):
            continue
        if isinstance(value, str) and key not in ("type", "code", "func", "title", "shape"):
            number = to_number(value)
            clean[key] = value if number is None else number
        else:
            clean[key] = value
    clean["type"] = clean["type"].strip()
    return clean


def clamp_slider_value(low, high, value):
    """(giá trị hợp lệ cho st.slider, có phải đã chỉnh không). Giữ kiểu int/float theo low/high."""
    number = to_number(value)
    integral = isinstance(low, int) and isinstance(high, int) and not isinstance(low, bool)
    if number is None:
        number, changed = low if low > 0 or high < 0 else 0, True
    else:
        changed = False
    if number < low:
        number, changed = low, True
    elif number > high:
        number, changed = high, True
    if integral:
        if number != int(number):
            changed = True
        return int(round(number)), changed
    return float(number), changed
