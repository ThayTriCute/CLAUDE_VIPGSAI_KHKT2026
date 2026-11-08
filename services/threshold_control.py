"""Explicit low-light controller model, independent of textbook or grade."""
import math
import re
from services.academic_context import folded


def light_controller_request(command):
    text = folded(str(command))
    if not ('den' in text and 'do sang' in text):
        return None
    low = re.search(r'nguong bat\s*[:=]?\s*(\d+(?:\.\d+)?)', text)
    high = re.search(r'nguong tat\s*[:=]?\s*(\d+(?:\.\d+)?)', text)
    if not low or not high:
        return None
    low, high = float(low[1]), float(high[1])
    if not 0 <= low < high <= 100:
        return None
    return {'type': 'light_threshold_control', 'low': low, 'high': high}


def light_controller_step(light, low, high, powered, previous):
    values = (light, low, high)
    if not all(math.isfinite(x) for x in values) or not 0 <= light <= 100 or not 0 <= low < high <= 100:
        raise ValueError('Độ sáng và ngưỡng phải thuộc 0–100; ngưỡng bật nhỏ hơn ngưỡng tắt.')
    if not powered:
        return False
    if light < low:
        return True
    if light > high:
        return False
    return bool(previous)
