# PR6 — bản vá 01: trạng thái chọn đề Trạm 3

Ngày 27/10/2026. Nền PR6: b47c08c. Chỉ thay kiểm tra trạng thái trước selectbox, không thay giao diện hoặc luồng AI.

## Nguyên nhân và cách vá

Chrome trước vá ghi nhận TypeError khi so sánh `sel_cached_exam_t3` dạng chuỗi với số nguyên. Bản vá giữ chỉ số nguyên trong giới hạn; các kiểu khác và chỉ số ngoài danh mục được đặt về phần tử đầu. Không ép chuỗi thành chỉ số vì có thể chọn nhầm đề sau khi đổi danh mục. Nguồn tạo ra chuỗi chưa được xác định đầy đủ; đây là bảo vệ ranh giới widget, không phải khẳng định đã xử lý mọi lỗi trạng thái.

## Kiểm chứng local

- 3 kiểm thử mới đạt: chỉ số hợp lệ, các kiểu cũ không hợp lệ, danh sách thu hẹp/rỗng.
- Bộ toàn dự án chạy 141 ca: 140 đạt, 1 thất bại do cache chứa dữ liệu giả lập QA-PR6 của lượt kiểm trước. Đã chuyển riêng 65 tệp có mã và dấu nhận diện QA sang thư mục bằng chứng ngoài repo. Nhóm 19 kiểm thử chứa ca thất bại được chạy lại và đạt. Giữ nguyên log thất bại để đối chiếu.
- 65/65 ngữ cảnh môn/lớp hỗ trợ: đưa nhãn chọn đề sai kiểu vào phiên, render Trạm 3 với danh mục fixture, kiểm phục hồi chỉ số 0 và đúng môn/lớp, rồi chuyển về Trạm 1. Không gọi AI thật; không xác nhận chất lượng nội dung học thuật.
- Chrome MCP mở localhost cổng 8526, chuyển Toán 12 → Toán 9 → GDCD 9 và thấy đúng tiêu đề/cấu hình. Không dùng kết quả này để khẳng định hết lag hoặc hết mọi lỗi.
- Lượt kiểm toàn luồng đầu bị timeout 90 giây ở khởi động AppTest; lượt thử lại toàn luồng dừng có chủ đích để chuyển sang ca hồi quy sát phạm vi bản vá. Không tính các ca chưa chạy là đạt.

## Được / mất / chi phí

Được: không còn phép so sánh chuỗi/số ở ranh giới chọn đề cache đã vá. Giữ lựa chọn hợp lệ. Không cắt tính năng, không đổi bố cục, không thêm lượt AI. Chi phí chỉ là kiểm kiểu và giới hạn; chưa có phép đo đủ để tuyên bố tối ưu BigTech hoặc độ trễ Cloud giảm.

Các lỗi công thức, Explain/Socratic, metadata tự luận, giữ đáp án khi chuyển trạm, phạm vi Speaking/Lab và giải mã JSON vẫn là các mục tiếp theo. Chưa triển khai lên nhánh chạy Cloud.

Bằng chứng đầy đủ trên máy: `F:/FINAL KHKT 2026/qa_evidence/PR6_PATCH01_GUARD_65_20261027.json`, các log `PR6_PATCH01_*`, ảnh `PR6_PATCH01_CHROME_GDCD9.png` và manifest cách ly QA. Không đưa dữ liệu cache hoặc bản ghi học sinh lên Git.
