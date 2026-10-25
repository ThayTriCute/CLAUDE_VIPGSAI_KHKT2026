# Bản vá luồng xuất bài Trạm 1 ngày 25 tháng 10 năm 2026

## Sự cố và trách nhiệm

Người dùng nhận bản nháp AI hai lần nhưng không có bài học xuất ra, với lỗi thiếu hình/hàm số hoặc gợi mở Socratic. Kiểm thử của bản trước dùng mẫu tổng hợp quá đều về định dạng, chưa chứng minh luồng sinh bài thực tế hoạt động ổn định. Việc báo hoàn thành toàn bộ khi chưa kiểm chứng sinh bài AI trên Cloud là quá sớm.

## Nguyên nhân kiểm chứng tại mã và kiểm thử

1. needs_visual tìm mọi lần xuất hiện của cụm bảng biến thiên/bảng xét dấu. Câu tự đủ hàm số yêu cầu học sinh lập bảng bị xem như đang tham chiếu một bảng đầu vào bị thiếu.
2. Khi lỗi cấu trúc, lời nhắc sửa yêu cầu vừa biên soạn lại câu thiếu ngữ liệu, vừa giữ nguyên nhiệm vụ, số liệu, ý nghĩa và chỉ sửa cú pháp. Điều này cản trở việc sửa trọn câu theo quyền phục dựng người dùng đã cấp.
3. Parser đòi nhãn không bọc Markdown và mỗi gợi mở đúng một dấu hỏi. Nhãn in đậm, hai câu hỏi dẫn dắt liên tiếp hoặc đường phân cách sau bước Pólya có thể bị từ chối dù chưa có lời giải/đáp án. Đây là các trường hợp hồi quy đã tái hiện bằng kiểm thử; chưa có bản nháp gốc của những lần trong ảnh nên không khẳng định biết đầy đủ từng câu AI đã sinh khi đó.

## Cách sửa

Nhận diện riêng các tham chiếu đầu vào như hình bên, bảng sau, dựa vào bảng; không chặn chỉ vì học sinh được yêu cầu lập một bảng. Các tham chiếu thật đến hình/bảng chưa có vẫn phải phục dựng hoặc biên soạn lại, không cho qua bằng hình mẫu vô căn cứ.

Tách lời nhắc sửa cú pháp toán và sửa cấu trúc bài học. Với lỗi cấu trúc, cho phép biên soạn lại toàn câu, cả bốn phương án và khóa chấm theo đúng môn/lớp/chủ đề, không sửa lẻ đáp án. Giữ giới hạn một lượt sửa bổ sung, không thêm vòng gọi AI vô hạn.

Chuẩn hóa cách trình bày nhãn Markdown và bước Pólya mà không tạo nội dung mới. Cho phép một cụm ngắn tối đa ba câu hỏi dẫn dắt, vẫn chặn chỉ dẫn đáp án, kết quả và các kiểu tính hộ đã kiểm tra. Bỏ đường phân cách Markdown khỏi phần gợi mở. Đầu ra vẫn yêu cầu ba câu trắc nghiệm, hai bài tự luận với đủ bốn bước tiếng Việt. Không đổi radio, infographic, YouTube, giọng đọc hoặc các bản vá điều hướng.

## Giới hạn

Bộ lọc cú pháp và mẫu ngôn ngữ không chứng minh nội dung AI chính xác khoa học tuyệt đối. Không bỏ cổng kiểm tra chỉ để làm mất thông báo đỏ; câu thực sự thiếu dữ kiện hoặc chứa lời giải vẫn có thể bị từ chối. Cần kiểm chứng trên Cloud sau triển khai và khởi động lại tiến trình khi đổi module như DEPLOYMENT_CHECKLIST.md.

## Kiểm thử trước phát hành

58 kiểm thử tập trung đạt; bản cuối đạt 199 kiểm thử toàn bộ trong 239,337 giây. Biên dịch tệp sửa và kiểm tra whitespace theo CRLF đạt. Kiểm thử tự động không thay thế việc soạn bài thật trên Cloud; kết quả bước đó được lưu riêng sau phát hành.
