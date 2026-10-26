# Sửa ngữ cảnh lớp trong Speaking Trạm 1

Ngày 26/10/2026. Phát hiện từ lượt kiểm tra Cloud sau PR #21: bài học đã là Tiếng Anh lớp 6, nhưng khu Speaking vẫn chọn `Unit 1: Life stories & Inspiring People` và từ vựng nâng cao.

## Nguyên nhân kỹ thuật

Hàm nhận `current_grade` nhưng dùng chung một dictionary bốn mẫu nâng cao cho mọi lớp. Khóa widget chọn chủ đề, audio và văn bản chỉ có tên trạm, không có lớp. Nhãn giao diện và prompt tự gọi những ví dụ này là SGK dù không có chứng cứ trang/bài; phần đánh giá cũng yêu cầu IELTS/Band 8.0 ngay cả khi chỉ có văn bản.

## Cách sửa

- Thêm kho mẫu luyện nói biên soạn riêng cho lớp 6–11, với từ vựng, đoạn đọc và câu hỏi tương ứng. Giữ bốn mẫu nâng cao hiện có ở lớp 12, bỏ số Unit không được đối chiếu. Đây **không phải** bổ sung toàn bộ chương trình hay trích nguyên văn KNTT.
- Giữ bố trí hai cột, danh sách chọn, từ vựng/IPA, đoạn đọc, micro, ô nhập và nút gửi. Khóa widget chứa lớp để không lấy bài nói lớp trước làm dữ liệu lớp mới. Các mẫu cố định là nội dung của thư viện luyện nói riêng, không tự nhận được trích từ bài AI đang hiển thị.
- Giữ chức năng phản hồi AI nhưng dùng đúng lớp và loại bằng chứng. Không có audio thì không đánh giá phát âm/ngữ điệu/độ trôi chảy thực tế. Có audio thì yêu cầu ghi rõ phần không nghe được; không hứa chép lời chính xác tuyệt đối. Không tự quy đổi IELTS/CEFR hoặc hứa Band 8.0.
- Không phát sinh lượt gọi API lúc render hoặc đổi lớp. AI chỉ chạy khi người dùng gửi bài có dữ liệu.

## Kiểm thử

- **14 ca tập trung qua** tại máy, 68,639 giây: kiểm thư viện đủ bảy lớp; mẫu lớp 12 được giữ và không bị mutate; kiểm guard trên các ngữ cảnh ngoài Tiếng Anh trong đủ 65 tổ hợp; thao tác hàm giao diện thật qua lớp 6–12, giữ audio input, chống lẫn bài nhập; kiểm prompt khi có/không audio; hồi quy giọng đọc, radio Hóa học và điểm Tiếng Anh.
- Không gọi Gemini thật trong các ca này. Thay đổi tập trung vào nhánh Speaking; ma trận 65 tổ hợp của PR #21 vẫn là bằng chứng cho các tiêu chí đã ghi trong báo cáo đó, không phải giấy nghiệm thu toàn bộ các nhánh phụ của Trạm 1.

## Giới hạn còn lại

Các mẫu là học liệu biên soạn, cần giáo viên duyệt; chưa có kho toàn bộ Unit/trang và phiên bản KNTT đối chiếu nguồn chính thức. Lượt kiểm Cloud cũng thấy menu Lab Toán lớp 6 còn đề xuất hàm bậc ba KNTT12; đây là hạng mục riêng chưa sửa trong bản vá Speaking này. Không kết luận Trạm 1 đã hoàn thiện toàn bộ chỉ từ kiểm thử phần bài học/trắc nghiệm.
