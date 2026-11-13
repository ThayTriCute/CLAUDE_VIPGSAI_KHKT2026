# Báo cáo test AI live — 13/11/2026

**Môi trường:** `http://localhost:8507` · Key sidebar đã nạp (không lưu Key vào repo) · Trạm 5: anh tự nạp ADMIN_PASS

## Kết quả

| Trạm | Kết quả | Bằng chứng |
|---|---|---|
| 1 Soạn bài AI | **PASS** | Spinner → `✓ Đã nhận phản hồi từ AI` · nội dung `PHẦN 1: BÀI HỌC` (đạo hàm / khảo sát hàm số) · metric Tự học (T1)=1 |
| 2 Socratic AI | **PASS** | Chat hỏi cực trị khi `y'=0` · Thầy trả lời Socratic (điều kiện cần/đủ, đổi dấu, ví dụ `y=x³`) |
| 3 Khảo thí | **PASS (shell)** | Vào Trạm 3 + `Bốc ngẫu nhiên (626 đề)` · UI đề hiện (`hasExam`, textLen↑) — chưa chấm full AI |
| 4 Tư vấn AI | **PASS** | Chat áp lực ôn thi → AI đồng hành; `Số lượt tư vấn… Trạm 5: 1` · `tram4_counsel_ai.png` |
| 5 Dữ liệu | **PASS** | Mở khóa OK · UI: Sức khỏe HT, Nhật ký+CSV, WHO-5 block, Xuất nghiên cứu ẩn danh, Hồ sơ cá nhân hóa, Khóa lại · `tram5_data_smoke.json` · `tram5_unlocked_health.png` |

## Vá phát hiện khi live
- AI chào **“ghé thăm Trạm 5”** dù UI là Trạm 4 → sửa `services/school_counseling.py`: `TRAM5_STATION_ID=4`, prompt khóa ghi rõ Trạm 4 tư vấn / Trạm 5 dữ liệu.
- Trạm 5 báo sai MK dù gõ `KHKT@2026`: `ADMIN_PASS` trong secrets là `sha256:…` **của mật khẩu khác** (hash không khớp). Đã ghi lại hash đúng + restart `:8507`; thêm `scripts/make_admin_pass_hash.py`.
- Trạm 5 sau mở khóa: bỏ banner “cần MK” khi đã auth; hiện `Đã mở khóa Trạm 5`; `station_from/to` gói tư vấn/WHO-5 = **4→5**; clear `between_group_result` khi phân tích lại; `csv_safe` cho CSV Pre–Post; không đếm fail khi submit MK trống; thông báo khóa phiên 1 phút vs global 2 phút.
- Mở khóa Trạm 5 bị nhảy về Trạm 1 → pin `_force_selected_station` + bỏ `on_click` nav (Enter/MK form kích nút đầu trang).
- Tối ưu 1–9 (13/11): Cloud checklist; admin_guard file bền; `station_auth` 1 cờ GV; `station_nav` + `ui/stations/`; alias COUNSELING_*; UX Enter/Ẩn danh/privacy; CI smoke T5; `qa_ai_live_matrix.py`.

## Ghi chú
- Streamlit text_input cần **Enter để apply** trước khi bấm Soạn bài.
- Greeting Trạm 2 đôi lúc “Ẩn danh” dù sidebar có tên — nhỏ.
- Metric sidebar: T1=1, T2=1 sau live.
- Cần **reload app** để khóa tư vấn mới có hiệu lực với lượt chat tiếp theo.
