# Bản vá nhãn nguồn danh mục Trạm 3 — 27/10/2026

## Nguyên nhân
`get_baseline_full_exams` trả cả kho nền, đề giáo viên tải lên và đề AI tích lũy. `get_cached_exams` lại gắn đồng loạt “[Đề thật]”, đồng thời tự điền năm 2025–2026 khi không có năm. Tiêu đề phòng thi còn tự nhận “chuẩn hóa” và gán trường mặc định khi dữ liệu thiếu tiêu đề. Đây là lỗi trình bày nguồn, không phải bằng chứng bộ sinh đề sai.

## Cách sửa và phạm vi
Chọn nhãn từ dấu nguồn đã khai báo: AI tích lũy, phối hợp nguồn, giáo viên tải lên; trường hợp còn lại dùng nhãn trung tính “Đề lưu trong kho”. Không coi vị trí lưu hoặc cờ nguồn là chứng nhận đã kiểm định. Thiếu thời điểm thì ghi chưa có; thiếu tiêu đề thì ghi “Đề luyện tập”. Giữ nguyên tiêu đề được cung cấp, câu hỏi, đáp án, bộ lọc, các nút và renderer. Không gọi AI, không thêm truy vấn mạng, không duyệt nội dung toàn kho.

## Kiểm chứng
18 kiểm thử cục bộ qua: 3 ca nguồn/tiêu đề (có thực thi hàm danh mục app.py), 6 ca BBT, 9 ca hợp đồng sinh đề. Kiểm tra dữ liệu câu hỏi và đầu vào không bị đổi. Chưa kiểm giao diện Cloud sau triển khai; chưa giải quyết danh mục trùng và lưu cache bền qua reboot. Không chứng nhận toàn bộ nguồn hoặc nội dung chương trình từ kiểm thử nhãn.
