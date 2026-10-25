# Bản vá giọng đọc theo yêu cầu — 25/10/2026

## Nguyên nhân

Luồng cũ gọi tải MP3 ngay khi dựng nội dung ở Trạm 1/2, thay vì đợi người dùng bấm nghe. Mỗi đoạn có giao diện/logic riêng; dữ liệu bị cắt ở ngưỡng ký tự và mô tả giọng Nam Bộ không được đối chiếu với giọng thực tế trên máy. Điều này vừa ảnh hưởng độ trễ vừa làm người dùng hiểu sai khả năng giọng đọc.

## Thay đổi

Dùng một bộ điều khiển giọng đọc cho Trạm 1–3; không tải âm thanh khi mở trạm. Nút nghe, double-click và kéo tô chọn dùng cùng bộ phân tích Anh–Việt, cùng nút dừng. Nạp lại giao diện không nhân đôi listener; đổi trạm/môn/lớp dừng nội dung cũ. Các bản vá điều hướng trước được giữ nguyên; không sửa cấu trúc radio, Socratic, Pólya, infographic hoặc liên kết YouTube của bản khôi phục.

Ưu tiên giọng thiết bị theo đúng ngôn ngữ; hiển thị tên và mã ngôn ngữ thực tế. Nếu thiếu giọng Việt, không lấy giọng Anh đọc thay. Lựa chọn giọng miễn phí trực tuyến phải được bật rõ ràng, thông báo nội dung đọc được gửi Google Translate TTS; có giới hạn đoạn, timeout, bộ nhớ đệm và tần suất. Thất bại một đoạn không ghép âm thanh thiếu rồi báo thành công. Thành phần relay chạy fragment để yêu cầu âm thanh không dựng lại toàn bộ trang. Streamlit tối thiểu 1.64 để hỗ trợ thành phần v2 đang dùng.

Cách đọc công thức được xử lý theo cấu trúc cho một tập ký hiệu hỗ trợ, thuật ngữ và đơn vị được áp dụng theo môn; ký hiệu chưa hỗ trợ báo cần đối chiếu, không tự đoán. Có tùy chọn ngôn ngữ thủ công cho từ ngắn không dấu/tên riêng mơ hồ. Bộ luật này không phải từ điển hoàn chỉnh của mọi ngành; không cam kết âm thanh luôn chính xác khoa học 100%. Giọng English là giọng en-US/en-GB của thiết bị/nhà cung cấp, không phải kết quả thẩm định phát âm chuyên gia. Giọng Việt miễn phí chưa xác nhận vùng Nam Bộ; chỉnh tốc độ/cao độ không biến giọng bất kỳ thành giọng Nam Bộ.

## Kiểm thử

- 191 kiểm thử Python đạt trong 189,373 giây, bao gồm kiểm thử hồi quy giao diện và giữ đáp án/thời hạn khi chuyển trạm.
- 19 kiểm thử JavaScript đạt: nhận diện ngôn ngữ, công thức, chọn đúng giọng, chống listener trùng, dừng hàng đợi, thiếu giọng và yêu cầu đồng ý dùng dự phòng.
- Trình duyệt thật tại máy: double-click Perseverance và kéo tô chọn cụm trong đoạn văn kích hoạt Microsoft David en-US; double-click nghĩa tiếng Việt dùng Google Translate TTS và báo đọc hết. Nút Dừng báo đã dừng. Máy kiểm thử không có giọng Việt cài sẵn.
- Không thẩm định bằng chuyên gia chất lượng âm sắc/ngắt nghỉ từng môn; chưa kiểm tra tải đồng thời hoặc tất cả trình duyệt/thiết bị.

## Sự cố phát hành trước và cách ngăn lặp lại

Sau PR #10, Cloud kéo mã nhưng giữ tiến trình Python cũ, phát sinh ImportError native_radio_label. Đã reboot Cloud, ghi nhận Uvicorn khởi động 04:17:46 UTC; mở phiên mới vào Trạm 1→2→3→4 (màn hình đăng nhập)→1 thành công. Xem DEPLOYMENT_CHECKLIST.md: mọi bản thay module cần xác minh khởi động sạch và kiểm tra Cloud trước khi báo hoàn tất. Không dùng reload module trong phiên người dùng để né vấn đề triển khai.
