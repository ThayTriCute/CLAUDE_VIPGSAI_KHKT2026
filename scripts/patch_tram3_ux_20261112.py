# -*- coding: utf-8 -*-
"""Byte-safe Trạm 3 UX patch — splice nhỏ, giữ CRLF/LF lẫn."""
from __future__ import annotations

from pathlib import Path

APP = Path(__file__).resolve().parents[1] / "app.py"


def u(s: str) -> bytes:
    return s.replace("\n", "\r\n").encode("utf-8")


def once(raw: bytes, old: bytes, new: bytes, label: str) -> bytes:
    if old not in raw:
        raise SystemExit(f"MISS: {label}\nOLD[:120]={old[:120]!r}")
    c = raw.count(old)
    if c != 1:
        raise SystemExit(f"COUNT {c}: {label}")
    print("OK", label)
    return raw.replace(old, new, 1)


def main() -> None:
    raw = APP.read_bytes()

    raw = once(
        raw,
        u(
            '        render_exam_clock()\n\n'
            '        st.caption("Bài tự nộp khi hết giờ. Hệ thống tự động lưu nháp mỗi 15 giây (chống mất bài nếu rớt mạng).")\n'
        ),
        u(
            '        render_exam_clock()\n\n'
            '        from services.tram3_exam_ux import answer_sheet_cells, render_answer_sheet_html\n'
            '        _sheet_cells = answer_sheet_cells(exam, st.session_state.get("exam_answers", {}), subject)\n'
            '        _sheet_html = render_answer_sheet_html(_sheet_cells)\n'
            '        if _sheet_html:\n'
            '            st.markdown(_sheet_html, unsafe_allow_html=True)\n'
            '        if st.session_state.get("tram3_sealed_mode"):\n'
            '            st.warning("🔒 Chế độ làm bài kín đang bật (buổi đo pre/post): hạn chế mở gợi mở Socratic.")\n\n'
            '        st.caption("Bài tự nộp khi hết giờ. Hệ thống tự động lưu nháp mỗi 15 giây (chống mất bài nếu rớt mạng). '
            'Nháp trình duyệt ưu tiên ô chữ; trắc nghiệm/Đ-S được giữ trong phiên Streamlit.")\n'
        ),
        "answer_sheet",
    )

    raw = once(
        raw,
        u(
            '                st.session_state.exam_time_mins = exam_time_mins\n\n'
            '                measure_phase = "practice"\n'
        ),
        u(
            '                st.session_state.exam_time_mins = exam_time_mins\n\n'
            '                st.checkbox(\n'
            '                    "🔒 Làm bài kín (nhắc tắt gợi mở Socratic — dùng khi đo pre/post)",\n'
            '                    value=bool(st.session_state.get("tram3_sealed_mode", False)),\n'
            '                    key="tram3_sealed_mode",\n'
            '                    help="Khi tắt: luyện tập Socratic bình thường. Khi bật: cảnh báo làm bài kín."\n'
            '                )\n\n'
            '                measure_phase = "practice"\n'
        ),
        "sealed_toggle",
    )

    raw = once(
        raw,
        u('                real_exams_list = ree.get_baseline_full_exams(subject, grade_num) if ree else []\n'),
        u(
            '                real_exams_list = ree.get_baseline_full_exams(subject, grade_num) if ree else []\n'
            '                from services.tram3_exam_ux import find_exam_by_access_code, filter_exams_for_listing, is_teacher_uploaded_exam\n'
            '                from services.exam_delivery import exam_delivery_held\n'
            '                real_exams_list = filter_exams_for_listing(real_exams_list, exclude_held_fn=exam_delivery_held)\n'
            '                _qp = {}\n'
            '                try:\n'
            '                    _qp = dict(st.query_params)\n'
            '                except Exception:\n'
            '                    _qp = {}\n'
            '                _access_code = str(_qp.get("exam_code") or st.session_state.get("tram3_access_code_input") or "").strip()\n'
            '                if _access_code:\n'
            '                    _matched = find_exam_by_access_code(real_exams_list, _access_code, identity_fn=exam_storage_identity)\n'
            '                    if _matched is not None:\n'
            '                        st.success(f"🔗 Đã khớp mã đề `{_access_code}` — xác nhận rồi nạp. Chưa tự vào phòng thi.")\n'
            '                        st.session_state["tram3_deep_link_exam"] = _matched\n'
            '                    else:\n'
            '                        st.warning(f"Không tìm thấy đề mã `{_access_code}` đúng môn/lớp đang chọn (hoặc đề đang bị giữ thẩm định).")\n'
            '                st.text_input("Mã đề / mã truy cập (từ QR hoặc giáo viên giao):", value=_access_code, key="tram3_access_code_input")\n'
        ),
        "deeplink",
    )

    raw = once(
        raw,
        u('                    if thithu_count > 0: filter_opts.append(f"🏛️ Thi thử ({thithu_count} đề)")\n'),
        u(
            '                    if thithu_count > 0: filter_opts.append(f"🏛️ Thi thử ({thithu_count} đề)")\n'
            '                    _gv_n = sum(1 for it in real_exams_list if is_teacher_uploaded_exam(it))\n'
            '                    if _gv_n > 0: filter_opts.append(f"👨‍🏫 Đề giáo viên đã lưu ({_gv_n} đề)")\n'
        ),
        "gv_filter_opt",
    )

    raw = once(
        raw,
        u('                        elif "Thi thử" in filter_ex_type: filtered_exams = thithu_exams or real_exams_list\n'),
        u(
            '                        elif "Thi thử" in filter_ex_type: filtered_exams = thithu_exams or real_exams_list\n'
            '                        elif "Đề giáo viên" in filter_ex_type: filtered_exams = [e for e in real_exams_list if is_teacher_uploaded_exam(e)] or real_exams_list\n'
        ),
        "gv_filter_apply",
    )

    raw = once(
        raw,
        u(
            '                        if btn_load_random:\n'
            '                            random.seed(time.time_ns())\n'
        ),
        u(
            '                        if (not btn_load_random) and st.session_state.get("tram3_deep_link_exam") is not None:\n'
            '                            sel_real_item = st.session_state.get("tram3_deep_link_exam")\n'
            '                            st.session_state["tram3_deep_link_exam"] = None\n'
            '                        elif btn_load_random:\n'
            '                            random.seed(time.time_ns())\n'
        ),
        "deeplink_load",
    )
    # NOTE: site has NO blank line between if btn_load_random and random.seed (probe confirmed).

    raw = once(
        raw,
        u(
            '                        key=f"t3_p3_{idx}",\n\n'
            '                        max_chars=6,\n'
        ),
        u(
            '                        key=f"t3_p3_{idx}",\n\n'
            '                        max_chars=16,\n'
        ),
        "max_chars",
    )

    raw = once(
        raw,
        u(
            '            st.caption(assessment_profile(subject, grade_num)["note"])\n\n'
            '    elif st.session_state.exam_state == "testing":\n'
        ),
        u(
            '            if st.session_state.get("gv_parsed_exam_temp") or st.session_state.get("exam_data"):\n'
            '                _exp_obj = st.session_state.get("gv_parsed_exam_temp") or st.session_state.get("exam_data")\n'
            '                if isinstance(_exp_obj, dict) and (_exp_obj.get("p1") or _exp_obj.get("p2") or _exp_obj.get("p3") or _exp_obj.get("part_doc_hieu")):\n'
            '                    with st.expander("🖨️ In đề trắng / xuất bản trước khi vào phòng thi", expanded=False):\n'
            '                        st.caption("Soạn xong có thể phát đề giấy hoặc QR trước giờ làm. Mặc định không kèm đáp án.")\n'
            '                        try:\n'
            '                            render_exam_export_suite(_exp_obj, subject, grade_num, st.session_state.get("exam_time_mins", 45), include_ans_default=False, key_prefix="gv_pre")\n'
            '                        except Exception as _ex:\n'
            '                            st.warning(f"Chưa xuất được bản nháp: {_ex}")\n\n'
            '            st.caption(assessment_profile(subject, grade_num)["note"])\n\n'
            '    elif st.session_state.exam_state == "testing":\n'
        ),
        "blank_export",
    )

    APP.write_bytes(raw)
    new = APP.read_bytes()
    crlf = new.count(b"\r\n")
    lf = sum(1 for i, x in enumerate(new) if x == 10 and (i == 0 or new[i - 1] != 13))
    print("DONE", len(new), "CRLF", crlf, "LF_only", lf, "delta_bytes", len(new) - 799153)


if __name__ == "__main__":
    main()
