# Hiển thị bảng biến thiên đủ dữ liệu ở Trạm 3

Ngày 26/10/2026. Sau PR25, hai lượt thật mở được bài làm: một câu dùng đạo hàm và một câu bắt buộc có BBT. Lượt BBT dùng hàm yêu cầu x^3-3x+1, mốc -1/1, giá trị 3/-1, dấu +/−/+ và đúng một phương án đồng biến. Kiểm bằng tính đạo hàm và giá trị tại hai điểm; chưa phải nghiệm thu mọi đề/môn/lớp.

## Lỗi hiển thị đã quan sát

Hàm `question_visual_html` xuất từng dòng BBT thành bảng thô. Hàng mốc x/y có 4 giá trị, hàng dấu có 5 token (+,0,−,0,+), dẫn đến cột không thẳng nhau. Các chuỗi -inf/+inf còn hiện nguyên dạng. Đề đã mở được nhưng biểu diễn này chưa đạt độ rõ cần thiết.

## Sửa hẹp

Thêm renderer cho đúng dạng BBT ba hàng đầy đủ có mốc số, dấu xen kẽ và giá trị giới hạn/cực trị. Dàn lưới điểm/khoảng cùng số cột, đổi ký hiệu vô cực sang Unicode, vẽ mũi tên theo dấu đạo hàm đã cung cấp. Không đổi dữ kiện, khóa chấm hoặc nội dung câu; không đoán dấu/giá trị còn thiếu. Kiểm độ dài/số lượng, thứ tự mốc và hướng biến thiên giữa các giá trị trước khi dùng cách trình bày mới. Các dạng phức tạp/không hiểu vẫn đi theo renderer escaped cũ, không bị bỏ mất. Không sửa engine sinh đề, bộ đọc hoặc giao diện radio.

Kiểm tra tại máy: **6 ca qua trong 3,046 giây**, gồm căn cột, giữ dấu/giá trị, vô cực, dữ liệu không đầy đủ/mâu thuẫn, chống HTML thô ở fallback và tích hợp đúng hàm app trong khi giữ bảng số liệu/đồ thị kèm theo. Không chạy lại bộ nặng trên laptop sau khi máy báo nóng; CI đầy đủ và hậu kiểm Cloud được theo dõi riêng.

Hậu kiểm dự kiến dùng lại đúng phiên đề BBT đã sinh để so trước/sau, không gọi thêm AI. Chỉ app.py và module mới thay đổi ở mã sản phẩm, không cập nhật một module dịch vụ cũ đang cache. Phải xác nhận CSS/lưới mới trên Cloud trước khi ghi đã triển khai; nếu không nạp được thì restart tiến trình theo quy trình đã thống nhất.
