# Bản vá đọc JSON đề AI Trạm 3

## Hiện tượng và nguyên nhân xác định được

Ảnh người dùng báo JSON không hợp lệ ở dòng 558, cột 51. Không có bản nháp gốc của lần đó nên chưa thể kết luận ký tự cụ thể gây lỗi. Kiểm tra đường nhận phản hồi và kiểm thử tái hiện được các lỗi sau:

- Trạm 3 cắt ba ký tự cuối khi chuỗi mở bằng code block, kể cả khi AI không gửi dấu đóng. JSON đầy đủ bên trong vì vậy có thể bị cắt hỏng.
- Bộ đọc cũ thử sửa dấu nháy và dấu phẩy ở các nhánh riêng; lỗi kết hợp có thể không được sửa cùng nhau. Vòng quét dấu nháy cắt hai nửa toàn bộ chuỗi ở mỗi vị trí, gây chi phí gần bậc hai với phản hồi dài.
- Nhánh cuối tự thêm dấu đóng cho dữ liệu bị cắt, có nguy cơ biến bản nháp chưa đầy đủ thành cấu trúc đọc được nhưng thiếu nội dung.

## Cách vá trong phạm vi luồng JSON

Bỏ thao tác cắt code block tại Trạm 3, chỉ bóc dấu mở và dấu đóng thực sự tồn tại trong bộ đọc chung. Tách bộ phục hồi cú pháp thuần Python để kiểm thử độc lập; chạy kết hợp sửa dấu nháy nội dung, dấu phẩy thừa ở cuối phần tử và một số dấu phẩy ngăn cách bị thiếu tại vị trí mà JSON decoder xác nhận.

Quét dấu nháy theo một lượt, không lặp cắt toàn bộ tiền tố/hậu tố. Giới hạn kích thước 2 triệu ký tự và tối đa tám lần bổ sung dấu phân cách cho mỗi ứng viên. Không gọi AI để sửa JSON. Không tự tạo khóa, đáp án, câu hỏi hoặc dấu đóng cho nội dung bị cắt thật. Khóa JSON trùng bị từ chối để tránh âm thầm mất câu hỏi. Giữ bước đối chiếu số câu, môn/lớp, công thức và điều kiện mở bài thi đã có sau khi đọc JSON.

Không đổi radio, số câu mặc định, tùy biến ma trận, Socratic, giọng đọc, xuất đề hoặc điều hướng. Không tuyên bố bộ đọc có thể phục hồi mọi JSON sai hay chứng minh kiến thức/đáp án đúng.

## Kiểm chứng

13 ca độc lập cho JSON chuẩn, code block thiếu dấu đóng nhưng JSON đầy đủ, dấu nháy cộng dấu phẩy thừa, dấu phân cách thiếu, LaTeX, xuống dòng, chuỗi chứa dấu giống cấu trúc, dữ liệu dài nhiều môn, khóa trùng và dữ liệu cắt thật. Một ca AppTest tạo đề qua nút Trạm 3 xác nhận câu/phương án/khóa chấm giữ nguyên và chỉ một lần gọi AI giả lập. Không dùng API thật trong các kiểm thử này.

Kết quả trước phát hành: 215 kiểm thử toàn bộ đạt trong 280,266 giây; 13 ca JSON độc lập và một ca giao diện nêu trên đều đạt; biên dịch và kiểm tra whitespace CRLF đạt. Chưa có bản nháp lỗi gốc để khẳng định đã tái hiện đúng ký tự ở dòng 558. Cần xác minh triển khai Cloud sau khi nạp lại tiến trình.
