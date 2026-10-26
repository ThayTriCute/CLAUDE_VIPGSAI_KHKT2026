# Chẩn đoán bản nháp Trạm 1 và gợi ý nhập bài theo lớp

Ngày 26/10/2026. Ảnh người dùng mới gửi có dòng “Gợi mở không được tính toán ra số thay học sinh”. Đây là thông báo kiểm tra Socratic, không chứng minh hệ thống đã diễn giải chữ HS thành học sinh và không đủ bằng chứng kết luận chưa push mã.

## Nguyên nhân còn thiếu bằng chứng

Trước bản này, khi cả bản đầu và bản sửa bị từ chối, Trạm 1 chỉ hiện thông báo lỗi; không giữ được nguyên văn bản sửa và vị trí câu/bước bị chặn cho quản trị đối chiếu. Vì vậy chưa phân biệt được gợi mở thực sự giải hộ với trường hợp bộ dò bắt nhầm ở lần lỗi trong ảnh. Không thể lấy một lượt sinh bài khác thành công để kết luận lỗi đó đã được sửa.

## Thay đổi

- Khi lần kiểm sau lượt sửa thất bại, giữ đúng loại ngoại lệ/thông báo đã có và đính kèm bản nháp tối đa 250.000 ký tự cùng số lượt kiểm. Không đưa bản nháp vào chuỗi lỗi công khai, không tăng lượt AI, không nới bộ lọc khi chưa có dữ liệu.
- Lỗi gợi mở ghi vị trí trắc nghiệm câu nào hoặc tự luận bài/bước nào. Vị trí không chứa gợi ý, khóa chấm hoặc đáp án.
- App che các API key đang dùng trong bản nháp, thông báo và chủ đề của chẩn đoán. Chỉ giữ dữ liệu trong phiên; nút tải nằm sau xác thực quản trị Trạm 4. Bắt đầu lượt soạn mới xóa chẩn đoán cũ. Không gửi chẩn đoán sang dịch vụ khác.
- Gợi ý trong ô nhập bài Trạm 1 từng cố định theo môn, dùng ví dụ lớp 12 cả khi chọn lớp 6. Nay lấy hai chủ đề biên tập của đúng tổ hợp môn/lớp; thiếu chủ đề thì ghi môn/lớp đang học. Không nhận các chủ đề này là mục lục SGK đã thẩm định.

## Kiểm thử

**46 ca tập trung qua**, 47,155 giây tại máy. Bao gồm lỗi còn giữ đúng kiểu, bản nháp không lọt vào thông báo; vị trí câu/bước; hai lượt kiểm không thành vòng lặp vô hạn; che key; không có nút tải ở Trạm 1 hoặc Trạm 4 chưa đăng nhập; admin xem được; lượt soạn mới xóa bản cũ; placeholder đúng cả 65 tổ hợp; hồi quy công thức/Pólya/xuất bản.

Trong lúc xây ca thử có một lỗi đặt vị trí hàm test làm biến `calls` ra ngoài phạm vi. Đã sửa bố trí test, chạy lại nhóm liên quan và lượt 46 ca cuối đều qua; lỗi này ở mã kiểm thử tại máy, chưa được push thành bản vận hành.

Các provider trong ca kiểm thử được giả lập. Chưa có bản nháp gốc của ảnh lỗi cũ để tái hiện nguyên văn. Chẩn đoán giúp điều tra lần lỗi tiếp theo; bản này **không được gọi là đã sửa dứt điểm mọi lỗi Socratic**. Dữ liệu chỉ ở trong phiên nên mất khi đóng phiên/khởi động lại; quản trị cần tải trước nếu cần giữ lâu dài.
