# KẾ HOẠCH TỔNG THỂ HOÀN THIỆN GSAI — bản sống (mọi ca AI/mô hình phải đọc và cập nhật)

> Lập 11/11/2026 theo yêu cầu chủ dự án: làm cuốn chiếu, tự động, không chờ nhắc; mọi ca/mô hình
> tiếp nối theo đúng tài liệu này. Quy trình bắt buộc vẫn là LUẬT 09/11/2026 trong `AGENTS.md`
> (đọc đủ → bằng chứng → hồi quy baseline → CI xanh 3.10+3.11 → PR → ghi nhật ký).
> Sau mỗi mốc: đổi trạng thái ở bảng dưới + ghi 1 dòng ở "Nhật ký mốc".

## Hiện trạng đã kiểm (11/11/2026, main `e3b7cd9`)
- CI: 892 test xanh trên Python 3.10 và 3.11. Phân tích tĩnh `ruff` nhóm lỗi chết người (F821, E9…): 0 lỗi.
- Trạm 1 và Trạm 3 đã nghiệm thu cơ chế đủ 13 môn × lớp 6–12 (`tests/test_station1_scope.py`, `tests/test_station3_integrity.py`).
- CSDL: SQLite WAL + hàng đợi `sync_outbox`; tự tạo bảng khi thiếu.
- Gọi AI: có hạn 240 giây, xoay khóa, đổi model dự phòng, che khóa trong thông báo lỗi.

## Rủi ro đã có bằng chứng → việc phải làm
| Mã | Việc | Bằng chứng | Trạng thái |
|---|---|---|---|
| P0-1 | Gỡ mật khẩu quản trị thật khỏi test (kho CÔNG KHAI); **chủ dự án đổi `ADMIN_PASS`** | 3 dòng trong 2 tệp test + `.pyc` cũ | PR đợt 1 |
| P0-2 | Test chặn khóa/URL bí mật lọt vào kho | `tests/test_repo_hygiene.py` | PR đợt 1 |
| P0-3 | Dấu phiên bản ở thanh bên để xác minh Cloud đã cập nhật | `services/build_info.py` | PR đợt 1 |
| P1-1 | Bỏ theo dõi 33 tệp `.pyc` + `data/gsai_learning.db` (đã nằm trong `.gitignore` nhưng vẫn bị track) | `git ls-files` | Đợt 2 — sau khi dấu phiên bản đã lên Cloud; nếu Cloud không tự cập nhật thì Reboot app |
| P1-2 | Chặn trên phiên bản thư viện theo bản CI đã kiểm | CI 3.11 đã tự nhảy `google-genai 3.0.0`, `pandas 3.1`, `pymupdf 2.1`, `pillow 13` — bản lớn mới có thể làm sập app khi Cloud cài lại | Đợt 3 |
| P1-3 | CI chạy thêm Python 3.12, 3.13 + cổng `ruff` lỗi chết người | Máy phát triển dùng 3.13, CI chỉ 3.10/3.11 | Đợt 3 |
| P2-1 | Giới hạn mềm số lượt gọi AI mỗi phiên (bảo vệ hạn mức khóa dùng chung) | Không có giới hạn; `tram*_count` chỉ để thống kê | Chờ chủ dự án chọn ngưỡng |
| P2-2 | Bảng "Sức khỏe hệ thống" trong khu quản trị (phiên bản Python/thư viện, CSDL, hàng đợi đồng bộ, số khóa) | Chưa có | Đợt 4 |
| P3-1 | Nghiệm thu cơ chế Trạm 2 và Trạm 4 đủ môn/lớp như Trạm 1, 3 | Chưa làm | Đợt 5 |
| P3-2 | Đối chiếu nốt chủ đề gợi ý còn theo web (Tin 11/12, GDKT&PL 12, KHTN 9, LS&ĐL 8, GDCD 8/9, Tiếng Anh 8/9) bằng kho XZ/ba nguồn | Kho chưa có sách các môn này | Khi có sách |
| P3-3 | Mở rộng gói căn cứ `reviewed_lesson_packets` (hiện 26 gói) | Cuốn chiếu từng bài | Liên tục |

## Nguyên tắc triển khai an toàn
1. Mỗi đợt một nhánh + một PR; không gộp thay đổi có rủi ro triển khai khác nhau.
2. Thay đổi `requirements.txt` hoặc xóa tệp đang bị track phải đi PR riêng và kiểm dấu phiên bản trên Cloud sau khi merge.
3. Không đổi giao diện/tính năng đã duyệt ngoài phạm vi ghi trong bảng.

## Nhật ký mốc
- 11/11/2026: lập kế hoạch; mở PR đợt 1 (P0-1, P0-2, P0-3).
- 11/11/2026: P3-1 Trạm 2 — vá lỗi thật: ảnh >12MB hoặc >25MP (điện thoại 48–50MP) bị bỏ qua im lặng. Nay `services/upload_images.py` nhận JPEG tới 120MP (giải mã thu nhỏ), xoay đúng chiều EXIF, mọi ảnh bị từ chối đều có thông báo. Test: `tests/test_upload_images.py`. Phần còn lại của Trạm 2 (chấm, bút tích, radar, chat) đã đọc hết, chưa thấy lỗi cơ chế khác.
- 11/11/2026: PR #21, #22 đã merge (main `b3f64ee`). P1-1: gỡ theo dõi 28 `.pyc` + `data/gsai_learning.db` (bản trong Git rỗng 0 dòng ở cả 4 bảng; `database.py` tự tạo lại), thêm luật .gitignore + test chặn tái phạm. Nếu Cloud không lên bản mới sau merge: Manage app → ⋮ → Reboot app.
- 11/11/2026: P3-1 Trạm 4 đã đọc hết. Vá 2 điểm yếu bảo mật: (1) khóa dò mật khẩu quản trị chỉ theo phiên → thêm khóa mức tiến trình (15 lần sai/10 phút → khóa 2 phút) trong `services/admin_guard.py`; (2) CSV nhật ký có thể chứa công thức Excel từ tên học sinh → vô hiệu hóa bằng `csv_safe`. Thống kê (t-test, Hake, Cronbach) không thấy lỗi cơ chế. Còn lại của P3-1: Lab, infographic.
- 11/11/2026: P3-1 Lab ảo — lỗi thật: JSON do AI trả về đi thẳng vào `render_smart_lab`; hệ số ngoài khoảng thanh trượt, chuỗi số, null hoặc không phải object gây lỗi đỏ Streamlit và lặp lại mỗi lần tải. Nay `services/lab_safe.py` làm sạch dữ liệu, 45 thanh trượt trong Lab đưa giá trị về biên kèm thông báo, và có lưới bắt lỗi cuối. Chưa đọc từng dòng ~1.900 dòng công thức trong Lab; chưa rà `lesson_infographic_engine.py`.
- 11/11/2026: Rà infographic — đường chạy thật `services/lesson_export.build_lesson_html`/`lesson_body_html` an toàn (chặn HTML lạ, thoát ký tự, chặn ảnh ngoài); hình Lý/Hóa/Sinh qua `precision_visual_engine` bọc try/except. KHÔNG có lỗi để vá.
- 11/11/2026: PHÁT HIỆN mã chết — `lesson_infographic_engine.py` (2.158 dòng) được import là `lie` nhưng không chỗ nào gọi. Chủ dự án chọn GIỮ NGUYÊN (phương án B), chỉ ghi chú. Ca sau đừng tưởng đây là mã đang chạy.
- 11/11/2026: Chủ dự án xác nhận ĐÃ ĐỔI `ADMIN_PASS` → khép lại rủi ro mật khẩu công khai.
- 11/11/2026: P2-2 XONG — bảng '🩺 Sức khỏe hệ thống' trong Trạm 4 (admin): bản dựng, số khóa Gemini (chỉ số lượng, không lộ giá trị), CSDL + số bản ghi, sự kiện chờ đồng bộ, phiên bản thư viện. `services/system_health.py` + test. PR mới.
