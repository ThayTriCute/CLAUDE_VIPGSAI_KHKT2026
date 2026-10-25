"""Station 1 learning contract; private answer keys never enter student prose."""
import re

from services.academic_context import academic_context


class LessonContractError(ValueError):
    pass


POLYA_LABELS = ("Tìm hiểu đề", "Lập kế hoạch", "Thực hiện kế hoạch", "Kiểm tra và nhìn lại")


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
    # The question precedes its private evidence. Cut the whole evidence tail,
    # including multi-line/bulleted reasoning, rather than stripping only its label.
    return re.split(r"(?im)^[ \t]*(?:[-*•][ \t]*)?(?:\*\*)?(?:OUTCOME|COGNITIVE_REASON|COGNITIVE_STEPS)(?:\*\*)?[ \t]*:", str(text), maxsplit=1)[0].strip()


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
        hints = re.findall(r"(?im)^\s*(?:GỢI MỞ SOCRATIC|SOCRATIC|GỢI MỞ)\s*:\s*(.+)$", block)
        if len(hints) != 1:
            raise LessonContractError("Mỗi câu trắc nghiệm cần một gợi mở Socratic riêng theo ngữ cảnh.")
        validate_socratic_question(hints[0], question, dict(options)[keys[0].upper()])
        # Use the reconstruction tool in the publication gate, not only while
        # drawing the page. If reconstruction is impossible, the one bounded
        # whole-lesson repair must supply a coherent complete question.
        from services.context_recovery import needs_visual, has_visual, recover_visual
        item = {"q": question, "opt": [f"{letter}. {value}" for letter, value in options], "ans": keys[0].upper()}
        if needs_visual(item):
            restored = recover_visual(item, subject, grade)
            if not has_visual(restored):
                raise LessonContractError("Câu trắc nghiệm thiếu hàm số/hình hoặc dữ kiện để phục dựng; hãy bổ sung ngữ liệu trọn vẹn hoặc biên soạn lại cả câu và bốn phương án, bảo đảm duy nhất một đáp án.")
            if restored.get("visual_recovery", {}).get("unique_answer") not in (None, item["ans"]):
                raise LessonContractError("Khóa chấm không khớp phương án duy nhất được kiểm chứng từ hình phục dựng; cần đối soát lại cả câu.")
    if len(set(stems)) != 3:
        raise LessonContractError("Ba câu trắc nghiệm phải có nội dung khác nhau.")
    essay_guidance(text)
    return text


def validate_socratic_question(hint, question="", correct_text=""):
    hint = without_metadata(str(hint or "")).strip().strip("* ")
    if not hint or len(hint) > 500 or hint.count("?") != 1 or not hint.endswith("?"):
        raise LessonContractError("Gợi mở Socratic phải là một câu hỏi dẫn dắt, không phải lời giải.")
    if not re.search(r"[ăâđêôơưàáảãạèéẻẽẹìíỉĩịòóỏõọùúủũụỳýỷỹỵ]", hint, re.I):
        raise LessonContractError("Câu hỏi hướng dẫn phải bằng tiếng Việt.")
    if re.search(r"(?i)(?:đáp án|đáp số|kết quả là|nghiệm là|(?:chọn|phương án)\s+[A-D]\b|the answer|therefore|solution)", hint):
        raise LessonContractError("Gợi mở đang chứa chỉ dẫn đáp án hoặc lời giải.")
    for expression in re.findall(r"[A-Za-z][^$\n]{0,35}=\s*[-+]?\d+(?:[.,]\d+)?", hint):
        if expression not in question:
            raise LessonContractError("Gợi mở không được tính toán ra số thay học sinh.")
    answer = re.sub(r"^[A-D][.):]\s*", "", str(correct_text)).strip()
    if len(answer) >= 3 and answer.casefold() in hint.casefold() and answer.casefold() not in question.casefold():
        raise LessonContractError("Gợi mở đang nhắc nguyên văn phương án đúng.")
    return hint


def essay_guidance(text):
    stems = essay_stems(text)
    blocks = question_blocks(lesson_sections(text)[2])
    result = []
    for stem, (_, block) in zip(stems, blocks):
        steps = list(re.finditer(r"(?im)^\s*(?:#{1,6}\s*)?(?:\*\*)?Bước\s*([1-4])\b", block))
        hints = []
        for index, step in enumerate(steps):
            section = block[step.start():steps[index+1].start() if index+1 < len(steps) else len(block)]
            heading, _, body = section.partition("\n")
            # Canonical Vietnamese titles are rendered separately from the model's title.
            if "?" in heading:
                body = heading.split(":", 1)[-1] + "\n" + body
            hints.append(validate_socratic_question(body, stem))
        result.append((stem, hints))
    return result


def student_polya(text, subject, grade):
    academic_context(subject, grade)
    return "\n\n".join(f"#### Bài {index+1}\n\n{stem}\n\n" + "\n\n".join(
        f"**Bước {step+1}: {POLYA_LABELS[step]}**\n\n{question}"
        for step, question in enumerate(questions)) for index, (stem, questions) in enumerate(essay_guidance(text)))


def socratic_prompt(question, subject, grade, options=()):
    subject, grade = academic_context(subject, grade)
    return (f"Vai trò: gia sư môn {subject}, lớp {grade}. Chỉ tạo MỘT câu hỏi gợi mở Socratic bằng tiếng Việt, tối đa 450 ký tự, kết thúc bằng dấu hỏi. "
            "Bám chi tiết, đại lượng hoặc khái niệm trong đúng câu bên dưới, giúp học sinh tự làm bước tiếp theo. "
            "Không giải thích đáp án, không tính toán thay, không đưa kết quả, không nhắc chữ cái phương án; không chép một lời nhắc chung chung. "
            "Không thêm giả thiết hoặc công thức ngoài lớp/môn. Không viết tiêu đề, metadata hoặc lời giải.\n"
            f"Câu hỏi: {question}\nCác lựa chọn nếu có: {list(options)}")
