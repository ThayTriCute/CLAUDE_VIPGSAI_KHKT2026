"""Explicitly synthetic complete lessons for publication/UI regressions."""

def complete_lesson(theory="Phân số lớp 6: $\\frac{1}{2}$.", chemistry=False):
    questions = [
        ("Một nửa của 4 là bao nhiêu?", ["1", "2", "3", "4"], "B"),
        ("Một phần hai cộng một phần hai bằng bao nhiêu?", ["0", "1", "2", "3"], "B"),
        ("Phân số nào bằng một phần hai?", ["1/3", "2/4", "3/4", "4/5"], "B")]
    if chemistry:
        questions = [
            ("Công thức của nước là gì?", [r"$\ce{H2O}$", r"$\ce{CO2}$", r"$\ce{O2}$", r"$\ce{N2}$"], "A"),
            ("Kí hiệu của nguyên tố oxygen là gì?", ["H", "O", "C", "N"], "B"),
            ("Kí hiệu của nguyên tố hydrogen là gì?", ["O", "C", "H", "N"], "C")]
    result = "### PHẦN 1: BÀI HỌC\n" + theory + "\n### PHẦN 2: TRẮC NGHIỆM KHÁCH QUAN SOCRATIC\n"
    for i, (question, options, key) in enumerate(questions, 1):
        result += f"Câu {i}. [Mức độ: NB] {question}\n" + "\n".join(f"{chr(65+j)}. {value}" for j, value in enumerate(options))
        result += f"\nĐÁP ÁN: {key}\nGIẢI THÍCH: Em có thể đối chiếu định nghĩa nào đã học?\n"
    result += "### PHẦN 3: BÀI TẬP TỰ LUẬN\n"
    for i in (1, 2):
        stem = "Nêu thành phần nguyên tố của nước." if chemistry and i == 1 else "Đối chiếu vai trò của chỉ số trong công thức phân tử." if chemistry else f"Tự tính tổng một phần hai và một phần {i+2}."
        result += f"Câu {i}. [Mức độ: VD] {stem}\nOUTCOME: Rèn thao tác tự suy luận.\nCOGNITIVE_STEPS: [\"PRIVATE_REASONING\"]\n"
        for step, title in enumerate(("Tìm hiểu đề", "Lập kế hoạch", "Thực hiện kế hoạch", "Kiểm tra và nhìn lại"), 1):
            result += f"Bước {step}: {title}\nEm cần tự xem xét thông tin nào ở bước này?\n"
    return result
