"""Label the existing preset library without pretending it is the current lesson."""
import re

from services.academic_context import academic_context


def preset_lab_label(label, subject, grade):
    _, grade = academic_context(subject, grade)
    value = str(label)
    match = re.search(r'(?:KNTT|Vật l[íý]|Hóa học|Sinh học)\s*(\d{1,2})(?:\s*[-–]\s*(\d{1,2}))?', value, re.I)
    # Existing grade annotations are descriptions supplied with the preset,
    # not a verified curriculum map. Never invent a grade for untagged tools.
    if match:
        first, last = int(match[1]), int(match[2] or match[1])
        grades = f'{first}–{last}' if first != last else str(first)
        prefix = f'Mẫu tham khảo, nhãn lớp {grades}' if first <= grade <= last else f'Mở rộng, nhãn lớp {grades}'
    else:
        prefix = 'Công cụ minh họa'
    body = re.sub(r'\(\s*KNTT\s*\d{1,2}(?:\s*[-–]\s*\d{1,2})?\s*\)', '', value, flags=re.I).strip()
    return f'[{prefix}] {body}'


def preset_lab_note(subject, grade):
    subject, grade = academic_context(subject, grade)
    return (f'Thư viện mẫu minh họa độc lập với bài {subject} lớp {grade} đang học. '
            'Giữ các công cụ mở rộng; nhãn lớp lấy từ cấu hình mẫu, chưa phải đối chiếu SGK. '
            'Mẫu có sẵn không tự lấy hàm số hoặc dữ kiện từ bài học. '
            'Muốn mô phỏng theo bài, hãy nêu rõ dữ kiện trong lệnh mô phỏng bên dưới.')
