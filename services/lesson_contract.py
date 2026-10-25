"""Station 1 learning contract; private answer keys never enter student prose."""
import re

from services.academic_context import academic_context


class LessonContractError(ValueError):
    pass


POLYA_LABELS = ("Tìm hiểu đề", "Lập kế hoạch", "Thực hiện kế hoạch", "Kiểm tra và nhìn lại")


def polya_questions(subject, grade):
    subject, grade = academic_context(subject, grade)
    questions = {
        "Toán học": ("Đề bài cho những dữ kiện, điều kiện nào và yêu cầu em tìm hoặc chứng minh điều gì?", "Em sẽ chọn kiến thức nào đã học và sắp xếp các bước giải ra sao?", "Em có thể tự thực hiện từng bước đã chọn và nêu lý do cho mỗi bước như thế nào?", "Em sẽ kiểm tra kết quả tự tìm được với điều kiện của đề và thử cách đối chiếu nào khác?"),
        "Vật lý": ("Đề bài mô tả hiện tượng nào, cho những đại lượng và đơn vị nào, cần xác định điều gì?", "Em sẽ chọn mô hình hoặc quy luật nào đã học và lập kế hoạch xử lý dữ kiện ra sao?", "Em có thể tự triển khai từng bước, ghi rõ lập luận và kiểm tra đơn vị như thế nào?", "Em sẽ đối chiếu kết quả tự tìm với điều kiện, đơn vị và tính hợp lý của hiện tượng ra sao?"),
        "Hóa học": ("Đề bài cho những chất, điều kiện và dữ kiện nào, yêu cầu giải quyết vấn đề gì?", "Em sẽ dựa vào kiến thức và phương pháp nào đã học để lập kế hoạch giải quyết?", "Em có thể tự triển khai từng bước và kiểm tra sự phù hợp với dữ kiện hóa học như thế nào?", "Em sẽ kiểm tra lại lập luận, điều kiện và kết quả tự tìm bằng những căn cứ nào?"),
        "Sinh học": ("Đề bài nêu hiện tượng, đối tượng và dữ kiện sinh học nào, yêu cầu em làm rõ điều gì?", "Em sẽ dựa vào cơ chế, quy luật hoặc bằng chứng nào đã học để lập kế hoạch?", "Em có thể tự triển khai lập luận và gắn từng nhận định với dữ kiện như thế nào?", "Em sẽ đối chiếu kết luận tự rút ra với bằng chứng và phạm vi kiến thức đã học ra sao?"),
        "Ngữ văn": ("Đề yêu cầu đọc hoặc viết điều gì, với văn bản, thể loại và phạm vi nào?", "Em sẽ chọn những ý chính và dẫn chứng nào để lập kế hoạch đáp ứng yêu cầu đề?", "Em có thể tự triển khai từng ý, gắn nhận xét với dẫn chứng và diễn đạt mạch lạc như thế nào?", "Em sẽ tự rà lại việc bám đề, sử dụng dẫn chứng và diễn đạt để chỉnh sửa những điểm nào?"),
        "Tiếng Anh": ("Đề bài cung cấp ngữ liệu nào và yêu cầu em thực hiện nhiệm vụ gì?", "Em sẽ vận dụng từ vựng, ngữ pháp hoặc cách đọc hiểu nào đã học để lập kế hoạch?", "Em có thể tự thực hiện nhiệm vụ và kiểm tra từng lựa chọn ngôn ngữ như thế nào?", "Em sẽ tự đối chiếu nội dung, ngữ pháp và cách diễn đạt với yêu cầu đề để sửa những điểm nào?"),
        "Lịch sử": ("Đề bài đề cập sự kiện, thời gian, tư liệu và yêu cầu tìm hiểu nào?", "Em sẽ chọn bằng chứng và sắp xếp các mối liên hệ lịch sử theo kế hoạch nào?", "Em có thể tự triển khai từng nhận định và chỉ ra căn cứ từ tư liệu như thế nào?", "Em sẽ đối chiếu mốc thời gian, bằng chứng và phạm vi kết luận của mình ra sao?"),
        "Địa lý": ("Đề bài cung cấp dữ liệu, bản đồ hoặc biểu đồ nào, có mốc thời gian và yêu cầu gì?", "Em sẽ chọn cách đọc, so sánh hoặc phân tích dữ liệu nào để lập kế hoạch?", "Em có thể tự thực hiện từng bước và ghi rõ căn cứ, đơn vị khi sử dụng dữ liệu như thế nào?", "Em sẽ kiểm tra lại nguồn, mốc thời gian, đơn vị và sự phù hợp của nhận xét ra sao?"),
        "Tin học": ("Bài toán cho dữ liệu và ràng buộc nào, yêu cầu đầu ra hoặc sản phẩm gì?", "Em sẽ chọn cách biểu diễn dữ liệu và phương pháp xử lý nào để lập kế hoạch?", "Em có thể tự triển khai từng bước và theo dõi cách xử lý dữ liệu như thế nào?", "Em sẽ tự kiểm thử với những trường hợp thông thường và trường hợp biên nào?"),
    }
    return questions.get(subject, (
        "Đề bài cung cấp những thông tin, điều kiện nào và yêu cầu em giải quyết vấn đề gì?",
        "Em sẽ vận dụng những kiến thức đã học và sắp xếp công việc theo kế hoạch nào?",
        "Em có thể tự thực hiện từng bước và nêu căn cứ cho cách làm của mình như thế nào?",
        "Em sẽ đối chiếu sản phẩm hoặc lập luận của mình với yêu cầu đề và tự điều chỉnh ra sao?"))


def lesson_sections(text):
    markers = list(re.finditer(r"(?im)^\s*#{0,6}\s*PHẦN\s*([123])\s*[:.]", str(text)))
    if [m[1] for m in markers] != ["1", "2", "3"]:
        raise LessonContractError("Trạm 1 phải có đủ ba phần bài học, trắc nghiệm và tự luận, đúng thứ tự.")
    return [str(text)[m.end():markers[i+1].start() if i+1 < len(markers) else len(str(text))].strip()
            for i, m in enumerate(markers)]


def question_blocks(text):
    matches = list(re.finditer(r"(?im)^\s*(?:#{1,6}\s*)?(?:\*\*)?(?:Câu|Bài)\s*(\d+)\s*[.:)]\s*(?:\*\*)?", text))
    return [(int(m[1]), text[m.end():matches[i+1].start() if i+1 < len(matches) else len(text)].strip())
            for i, m in enumerate(matches)]


def without_metadata(text):
    text = re.sub(r"(?im)^\s*COGNITIVE_STEPS:\s*\[[\s\S]*?\]\s*$", "", text)
    return re.sub(r"(?im)^\s*(?:OUTCOME|COGNITIVE_REASON|COGNITIVE_STEPS):[^\n]*$", "", text).strip()


def essay_stems(text):
    blocks = question_blocks(lesson_sections(text)[2])
    if [number for number, _ in blocks] != [1, 2]:
        raise LessonContractError("Phần tự luận Trạm 1 cần đúng hai bài, đánh số 1 và 2.")
    stems = []
    for _, block in blocks:
        steps = list(re.finditer(r"(?im)^\s*(?:#{1,6}\s*)?(?:\*\*)?Bước\s*([1-4])\b", block))
        if [step[1] for step in steps] != ["1", "2", "3", "4"]:
            raise LessonContractError("Mỗi bài tự luận cần đủ bốn bước Pólya theo thứ tự 1–4.")
        stem = without_metadata(block[:steps[0].start()])
        stem = re.sub(r"(?i)^\s*\[Mức độ:[^\]]*\]\s*", "", stem)
        stem = re.sub(r"(?im)^\s*(?:Hướng dẫn[^\n]*|Gợi ý[^\n]*)$", "", stem).strip()
        if not stem or re.search(r"(?im)^\s*(?:Đáp án|Đáp số|Lời giải|Giải chi tiết|Answer|Solution|CORRECT)\s*:", stem):
            raise LessonContractError("Đề tự luận thiếu nội dung hoặc trộn sẵn lời giải/đáp số.")
        stems.append(stem)
    return stems


def validate_lesson_contract(text, subject, grade):
    academic_context(subject, grade)
    _, quiz, _ = lesson_sections(text)
    blocks = question_blocks(quiz)
    if [number for number, _ in blocks] != [1, 2, 3]:
        raise LessonContractError("Trạm 1 cần đúng ba câu trắc nghiệm, đánh số 1–3.")
    stems = []
    for _, block in blocks:
        options = re.findall(r"(?im)^\s*\*{0,2}([A-D])[.:)]\s*\*{0,2}\s*([^\n]+)", block)
        if [letter.upper() for letter, _ in options] != list("ABCD"):
            raise LessonContractError("Mỗi câu trắc nghiệm cần đúng bốn phương án A, B, C, D trên bốn dòng.")
        if len({value.strip().casefold() for _, value in options}) != 4:
            raise LessonContractError("Các phương án trong một câu trắc nghiệm không được trùng nhau.")
        question = re.split(r"(?im)^\s*\*{0,2}A[.:)]", block, maxsplit=1)[0]
        question = without_metadata(re.sub(r"(?i)\[Mức độ:[^\]]*\]", "", question))
        if not question or re.search(r"(?i)(?:đáp án|chọn)\s*(?:đúng|là|:)\s*[A-D]\b", question):
            raise LessonContractError("Câu hỏi thiếu nội dung hoặc lộ khóa đáp án ngay trong đề.")
        stems.append(" ".join(question.casefold().split()))
        keys = re.findall(r"(?im)^\s*(?:CORRECT|ĐÁP ÁN|Đáp án đúng)\s*:\s*([A-D])\s*[.]?\s*$", block)
        if len(keys) != 1:
            raise LessonContractError("Trắc nghiệm cần một khóa đáp án riêng để chấm; không tự gán đáp án A.")
    if len(set(stems)) != 3:
        raise LessonContractError("Ba câu trắc nghiệm phải có nội dung khác nhau.")
    essay_stems(text)
    return text


def student_polya(text, subject, grade):
    """Only vetted Vietnamese questions enter guidance; AI solution prose is not rendered."""
    stems = essay_stems(text)
    questions = polya_questions(subject, grade)
    return "\n\n".join(f"#### Bài {index+1}\n\n{stem}\n\n" + "\n\n".join(
        f"**Bước {step+1}: {POLYA_LABELS[step]}**\n\n{question}"
        for step, question in enumerate(questions)) for index, stem in enumerate(stems))


def safe_quiz_hint(subject, grade):
    academic_context(subject, grade)
    return "Em hãy đọc lại yêu cầu, đối chiếu từng phương án với dữ kiện và kiến thức đã học; em có thể tự loại trừ phương án nào và vì sao?"
