"""Label the existing preset library without pretending it is the current lesson."""
import re

from services.academic_context import academic_context, canonical_subject


def resolve_preset_lab(subject, label, payload):
    """Correct one mismatched preset; keep its menu identity and other payloads."""
    if (canonical_subject(subject) == 'Tin học'
            and label == 'Sơ đồ thuật toán & Cây nhị phân'
            and payload.get('type') == 'oxyz'):
        return {'type': 'mermaid', 'code': '''graph TD
R["Mẫu minh họa: tìm kiếm trên cây nhị phân tìm kiếm"] --> T["Cây mẫu"]
T --> N8["8"]
N8 --> N3["Nhánh trái: 3"]
N8 --> N10["Nhánh phải: 10"]
N3 --> N1["Nhánh trái: 1"]
N3 --> N6["Nhánh phải: 6"]
R --> A["Thuật toán: bắt đầu tại gốc, so sánh k với khóa nút"]
A --> E["Nút rỗng: kết luận không tìm thấy"]
A --> F["k bằng khóa: tìm thấy, dừng"]
A --> L["k nhỏ hơn khóa: sang con trái và lặp lại"]
A --> G["k lớn hơn khóa: sang con phải và lặp lại"]'''}
    return dict(payload)


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
