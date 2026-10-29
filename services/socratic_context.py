"""Subject-aware fallback questions, without certifying generated hint content."""
import re

from services.academic_context import canonical_subject, folded


def math_context_question(question):
    """Small context-specific fallback library; no calculation or answer content."""
    text = folded(question)
    if 'truc tung' in text and any(term in text for term in ('cat truc tung', 'giao diem', 'tung do')):
        return ('Một điểm nằm trên trục tung thì hoành độ có đặc điểm gì? '
                'Từ đó, em sẽ dùng hàm số đã cho để xác định tung độ như thế nào?')
    for kind in ('tieu', 'dai'):
        if 'toa do diem cuc ' + kind in text:
            label = 'cực tiểu' if kind == 'tieu' else 'cực đại'
            return (f'Em cần nhận ra sự đổi dấu nào của đạo hàm để tìm hoành độ điểm {label}? '
                    'Sau đó, em sẽ dùng hàm số ban đầu như thế nào để xác định đủ hai tọa độ?')
    return None


_QUESTIONS = {
    'Ngữ văn': 'Em cần tìm chi tiết, từ ngữ hoặc bằng chứng nào trong ngữ liệu để trả lời đúng yêu cầu?',
    'Tiếng Anh': 'Em nhận thấy dấu hiệu nào về nghĩa, cấu trúc câu hoặc ngữ cảnh trước khi đối chiếu các phương án?',
    'Lịch sử': 'Em cần xác định mốc thời gian, bối cảnh và bằng chứng lịch sử nào liên quan đến yêu cầu?',
    'Địa lý': 'Em cần đọc thông tin nào từ bản đồ, bảng số liệu hoặc ngữ liệu địa lí để đối chiếu yêu cầu?',
    'Lịch sử & Địa lý': 'Em cần xác định bối cảnh thời gian, không gian và bằng chứng nào trong ngữ liệu?',
    'Vật lý': 'Em cần nhận diện hiện tượng, các đại lượng và điều kiện áp dụng mối quan hệ vật lí nào?',
    'Hóa học': 'Em cần xác định chất, điều kiện hoặc bằng chứng phản ứng nào trước khi đối chiếu các phương án?',
    'Sinh học': 'Em cần xác định cấp độ tổ chức, quá trình hoặc bằng chứng sinh học nào trong câu hỏi?',
    'Khoa học tự nhiên': 'Em cần nhận diện hiện tượng, dữ kiện và mối quan hệ khoa học nào trong câu hỏi?',
    'Tin học': 'Em cần xác định đầu vào, đầu ra hoặc quy tắc hoạt động nào trong tình huống được nêu?',
    'Công nghệ': 'Em cần xác định chức năng, điều kiện sử dụng và tiêu chí nào của giải pháp công nghệ?',
    'Giáo dục công dân': 'Em cần đối chiếu hành vi, hoàn cảnh và nguyên tắc ứng xử nào trong tình huống?',
    'Giáo dục kinh tế và pháp luật': 'Em cần xác định chủ thể, quan hệ kinh tế hoặc quyền và nghĩa vụ nào trong tình huống?',
}


def guiding_question(hint, options=None, correct_answer=''):
    """Prefer a separate guiding question; never substitute the EXPLAIN field.

    Explicit answer markers and verbatim alternatives are rejected here. This
    is a structural check, not proof that every paraphrase is non-revealing.
    Rejection changes only the hint, never blocks the lesson or calls AI again.
    """
    value = str(hint or '').strip()
    marked_answer = re.search(
        r'(?i)(?:\b(?:chọn|đáp án|đáp số|answer|choose|option)\s*(?:là|is|:)?\s*[A-D]\b'
        r'|\b[A-D]\s*(?:là\s*)?(?:đúng|correct)\b)', value)
    alternatives = [re.sub(r'^[A-D][.):]\s*', '', str(o), flags=re.I).strip().casefold()
                    for o in options or []]
    answer = str(correct_answer or '').strip().casefold()
    if len(answer) > 3:
        alternatives.append(answer)
    repeats_answer = any(len(o) > 3 and o in value.casefold() for o in alternatives)
    if value and len(value) <= 800 and value.endswith('?') and not marked_answer and not repeats_answer:
        return value
    return None


def english_reading_question(question):
    """Guide evidence selection from the final reading task, never quote its answer."""
    text = str(question or '')
    if not re.search(r'(?i)\b(?:read\b.{0,50}\b(?:passage|text)|according to (?:the )?(?:passage|text))\b', text):
        return None
    tasks = re.findall(r'(?i)\b(what|where|when|who|why|how)\b[^?]{0,300}\?', text)
    if not tasks:
        return None
    kind = tasks[-1].lower()
    targets = {'what': 'hoạt động, sự việc hoặc thông tin được hỏi',
               'where': 'địa điểm được hỏi', 'when': 'thời điểm được hỏi',
               'who': 'nhân vật được hỏi', 'why': 'nguyên nhân được hỏi',
               'how': 'cách thức hoặc mức độ được hỏi'}
    return (f'Câu hỏi cuối đoạn đọc yêu cầu em xác định {targets[kind]}. '
            'Em sẽ tìm chi tiết nào trong đoạn và kiểm tra đúng chủ thể, hoàn cảnh '
            'trước khi đối chiếu các phương án?')


def subject_socratic_hint(hint, subject, options=None, correct_answer='', question_text=''):
    subject = canonical_subject(subject)
    question = guiding_question(hint, options, correct_answer)
    if question:
        return question
    if subject == 'Tiếng Anh':
        contextual = english_reading_question(question_text)
        if contextual:
            return contextual
    return _QUESTIONS.get(subject, 'Em cần xác định dữ kiện và yêu cầu nào trước khi tự đối chiếu các phương án?')
