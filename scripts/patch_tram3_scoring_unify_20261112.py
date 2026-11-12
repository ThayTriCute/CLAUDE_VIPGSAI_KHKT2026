# -*- coding: utf-8 -*-
"""Byte-safe: Trạm 3 graded dùng grade_exam_by_profile; metric theo phần thật có."""
from pathlib import Path

APP = Path(__file__).resolve().parents[1] / "app.py"


def crlf(text: str) -> bytes:
    return text.replace("\r\n", "\n").replace("\n", "\r\n").encode("utf-8")


OLD_IMPORT = (
    "from services.scoring_service import calculate_part2_statement_score, "
    "grade_part1, grade_part2, grade_part3"
)
NEW_IMPORT = (
    "from services.scoring_service import calculate_part2_statement_score, "
    "grade_part1, grade_part2, grade_part3, grade_exam_by_profile"
)

# Replace the non-literature scoring block (from "# 1. Chấm Phần I" through metrics)
OLD_BLOCK = r'''            # 1. Chấm Phần I (Trắc nghiệm 4 lựa chọn)

            p1_items = exam.get("p1", [])

            base_p1, base_p2, base_p3 = assessment_profile(subject, grade_num)["weights"]
            if subject == "Tiếng Anh":
                base_p1, base_p2, base_p3 = 10.0, 0.0, 0.0

            active_max = sum(weight for part, weight in zip(("p1", "p2", "p3"), (base_p1, base_p2, base_p3)) if exam.get(part))

            scale = 10.0/active_max if active_max else 0.0

            w_p1_total = base_p1*scale if exam.get("p1") else 0.0

            p1_correct = 0

            if p1_items:

                for idx, q in enumerate(p1_items):

                    user_a = st.session_state.exam_answers.get(f"p1_{idx}", "")

                    user_letter = re.sub(r'[^A-D]', '', user_a.strip()[:3]).upper()[:1] if user_a else ""

                    if mcq_answer_matches(q, user_a): p1_correct += 1

                score_p1 = round((p1_correct / len(p1_items)) * w_p1_total, 2)



            # 2. Chấm Phần II (Trắc nghiệm Đúng/Sai bậc 0.1 - 0.25 - 0.5 - 1.0)

            p2_items = exam.get("p2", [])

            w_p2_total = base_p2*scale if exam.get("p2") else 0.0

            if p2_items:

                w_per_q2 = w_p2_total / len(p2_items)

                for idx, q in enumerate(p2_items):

                    correct_stmts_cnt = 0

                    stmts = q.get("stmts", [])

                    for s_idx, stmt in enumerate(stmts):

                        user_choice = st.session_state.exam_answers.get(f"p2_{idx}_{s_idx}", "")

                        expected_bool = normalize_bool(stmt["a"] if "a" in stmt else stmt.get("ans"))

                        if (user_choice == "Đúng" and expected_bool is True) or (user_choice == "Sai" and expected_bool is False):

                            correct_stmts_cnt += 1



                    score_p2 += calculate_part2_statement_score(correct_stmts_cnt) * w_per_q2

                score_p2 = round(score_p2, 2)



            # 3. Chấm Phần III (Trả lời ngắn)

            p3_items = exam.get("p3", [])

            w_p3_total = base_p3*scale if exam.get("p3") else 0.0

            p3_correct = 0

            if p3_items:

                for idx, q in enumerate(p3_items):

                    user_ans_str = str(st.session_state.exam_answers.get(f"p3_{idx}", "")).strip().replace(',', '.')

                    expected_ans_str = str(q.get("ans", "")).strip().replace(',', '.')

                    if numeric_answer_matches(user_ans_str, expected_ans_str, q.get("rounding_decimals")):

                        p3_correct += 1

                score_p3 = round((p3_correct / len(p3_items)) * w_p3_total, 2)



            total_score = min(10.0, round(score_p1 + score_p2 + score_p3, 2))



            st.success(f"🏆 **ĐIỂM LUYỆN TẬP CỦA {student_name}: {total_score} / 10.0 ĐIỂM**")

            if subject == "Tiếng Anh":

                c_sc1, c_sc2, c_sc3 = st.columns(3)

                c_sc1.metric("Tổng Điểm Khảo Thí", f"{total_score:.2f} / 10.0 đ", f"{p1_correct}/{len(p1_items)} câu đúng")

                pct = (p1_correct / len(p1_items) * 100) if p1_items else 0

                c_sc2.metric("Tỉ Lệ Chính Xác", f"{pct:.1f}%", "Trong đề luyện tập này")

                c_sc3.metric("Khung Năng Lực CEFR", "Chưa đánh giá", "Cần bài đánh giá năng lực chuẩn hóa")

            elif is_social_or_tech_subject(subject):

                c_sc1, c_sc2 = st.columns(2)

                c_sc1.metric("Phần I: TN 4 Lựa Chọn", f"{score_p1:.2f} / {w_p1_total:.1f} đ", f"{p1_correct}/{len(p1_items)} câu đúng" if p1_items else "")

                c_sc2.metric("Phần II: Đúng/Sai (0.1-0.25-0.5-1.0)", f"{score_p2:.2f} / {w_p2_total:.1f} đ", "Thang điểm luyện tập")

            else:

                c_sc1, c_sc2, c_sc3 = st.columns(3)

                c_sc1.metric("Phần I: TN 4 Lựa Chọn", f"{score_p1:.2f} / {w_p1_total:.1f} đ", f"{p1_correct}/{len(p1_items)} câu đúng" if p1_items else "")

                c_sc2.metric("Phần II: Đúng/Sai (0.1-0.25-0.5-1.0)", f"{score_p2:.2f} / {w_p2_total:.1f} đ", "Thang điểm luyện tập")

                c_sc3.metric("Phần III: Trả Lời Ngắn", f"{score_p3:.2f} / {w_p3_total:.1f} đ", f"{p3_correct}/{len(p3_items)} câu đúng" if p3_items else "")
'''

NEW_BLOCK = r'''            # 1–3. Chấm điểm thống nhất qua scoring_service.grade_exam_by_profile (đa môn/đa lớp)

            graded = grade_exam_by_profile(exam, st.session_state.exam_answers, subject, grade_num)

            score_p1 = graded["score_p1"]

            score_p2 = graded["score_p2"]

            score_p3 = graded["score_p3"]

            w_p1_total = graded["w_p1"]

            w_p2_total = graded["w_p2"]

            w_p3_total = graded["w_p3"]

            p1_items = exam.get("p1", []) or []

            p2_items = exam.get("p2", []) or []

            p3_items = exam.get("p3", []) or []

            p1_correct = graded["p1_correct"]

            p3_correct = graded["p3_correct"]

            total_score = graded["total"]

            p2_caption = graded["p2_label"]



            st.success(f"🏆 **ĐIỂM LUYỆN TẬP CỦA {student_name}: {total_score} / 10.0 ĐIỂM**")

            if graded.get("scope") == "practice":

                st.caption("Điểm luyện tập theo lớp; không phải chứng nhận thi tốt nghiệp Bộ GD&ĐT.")

            elif graded.get("scope") == "graduation_reference":

                st.caption("Tham chiếu cấu trúc QĐ 764; đề trong app là luyện tập, chưa được Bộ thẩm định.")



            if subject == "Tiếng Anh":

                c_sc1, c_sc2, c_sc3 = st.columns(3)

                c_sc1.metric("Tổng Điểm Khảo Thí", f"{total_score:.2f} / 10.0 đ", f"{p1_correct}/{len(p1_items)} câu đúng")

                pct = (p1_correct / len(p1_items) * 100) if p1_items else 0

                c_sc2.metric("Tỉ Lệ Chính Xác", f"{pct:.1f}%", "Trong đề luyện tập này")

                c_sc3.metric("Khung Năng Lực CEFR", "Chưa đánh giá", "Cần bài đánh giá năng lực chuẩn hóa")

            else:

                # Metric theo phần thật có trên đề (không ẩn P3 của Địa lý / STEM)

                cols = []

                if graded["has_p1"]:

                    cols.append(("Phần I: TN 4 Lựa Chọn", f"{score_p1:.2f} / {w_p1_total:.1f} đ", f"{p1_correct}/{len(p1_items)} câu đúng"))

                if graded["has_p2"]:

                    cols.append((f"Phần II: Đúng/Sai ({p2_caption})", f"{score_p2:.2f} / {w_p2_total:.1f} đ", "Theo số ý đúng mỗi câu"))

                if graded["has_p3"]:

                    cols.append(("Phần III: Trả Lời Ngắn", f"{score_p3:.2f} / {w_p3_total:.1f} đ", f"{p3_correct}/{len(p3_items)} câu đúng"))

                if not cols:

                    st.info("Đề chưa có phần trắc nghiệm để hiển thị điểm thành phần.")

                else:

                    metric_cols = st.columns(len(cols))

                    for col, (label, value, delta) in zip(metric_cols, cols):

                        col.metric(label, value, delta)
'''


def main():
    data = APP.read_bytes()
    lf_before = data.count(b"\n") - data.count(b"\r\n")
    old_i = OLD_IMPORT.encode("utf-8")
    new_i = NEW_IMPORT.encode("utf-8")
    if old_i not in data:
        raise SystemExit("import not found")
    data = data.replace(old_i, new_i, 1)
    old_b = crlf(OLD_BLOCK)
    new_b = crlf(NEW_BLOCK)
    if old_b not in data:
        # try LF-only variant of old block for diagnostics
        raise SystemExit("graded block not found (CRLF exact match failed)")
    if data.count(old_b) != 1:
        raise SystemExit(f"graded block matches={data.count(old_b)}")
    data2 = data.replace(old_b, new_b, 1)
    lf_after = data2.count(b"\n") - data2.count(b"\r\n")
    if lf_after != lf_before:
        raise SystemExit(f"LF drift {lf_before}->{lf_after}")
    APP.write_bytes(data2)
    print("PATCH_OK scoring unify", "lf_only", lf_after, "bytes", len(data2))


if __name__ == "__main__":
    main()
