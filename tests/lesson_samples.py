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
        hint = ("Em nhớ cách biểu diễn một nửa của một số như thế nào?" if i == 1 else "Em sẽ quy đồng hai phân số trong phép cộng như thế nào?" if i == 2 else "Em có thể dùng tính chất bằng nhau của phân số để đối chiếu các lựa chọn như thế nào?") if not chemistry else ("Em sẽ dùng thành phần nguyên tố của nước để đối chiếu các công thức như thế nào?" if i == 1 else "Em đã học kí hiệu của nguyên tố oxygen trong bảng tuần hoàn như thế nào?" if i == 2 else "Em đã học kí hiệu của nguyên tố hydrogen trong bảng tuần hoàn như thế nào?")
        result += f"\nĐÁP ÁN: {key}\nGỢI MỞ SOCRATIC: {hint}\nGIẢI THÍCH: PRIVATE_WORKED_EXPLANATION.\n"
    result += "### PHẦN 3: BÀI TẬP TỰ LUẬN\n"
    for i in (1, 2):
        stem = "Nêu thành phần nguyên tố của nước." if chemistry and i == 1 else "Đối chiếu vai trò của chỉ số trong công thức phân tử." if chemistry else f"Tự tính tổng một phần hai và một phần {i+2}."
        result += f"Câu {i}. [Mức độ: VD] {stem}\nOUTCOME: Rèn thao tác tự suy luận.\nCOGNITIVE_STEPS: [\"PRIVATE_REASONING\"]\n"
        for step, title in enumerate(("Tìm hiểu đề", "Lập kế hoạch", "Thực hiện kế hoạch", "Kiểm tra và nhìn lại"), 1):
            result += f"Bước {step}: {title}\nEm cần tự xem xét thông tin nào ở bước này?\n"
    return result
