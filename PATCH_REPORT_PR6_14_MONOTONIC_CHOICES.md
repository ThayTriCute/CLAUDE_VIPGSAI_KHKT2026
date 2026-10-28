# Bản vá 14 — kiểm tra tính duy nhất phương án đơn điệu

## Bằng chứng và nguyên nhân

Đề Cloud 8696, Toán 12, Trạm 3 mở được sau PR42 nhưng câu trắc nghiệm 3 có hai phương án đúng: x³+x−5 và x³−3x²+3x đều đồng biến trên R. Đạo hàm phương án sau bằng 3(x−1)²; bằng 0 tại một điểm không làm mất tính đồng biến nghiêm ngặt. Không nộp ca này như một đề hợp lệ.

Kiểm tra cũ chưa chứng minh tính đúng của cả bốn phương án trong dạng câu này. Đây là lỗi chất lượng đề, khác với lỗi kết nối hoặc lỗi không mở được đề.

## Cách vá và phạm vi

Thêm bộ chứng minh hẹp cho câu hỏi chọn hàm đồng biến/nghịch biến trên toàn R, với bốn đa thức số bậc không quá ba. Chỉ kết luận khi đọc được đầy đủ cả bốn phương án; dạng khác hoặc có điều kiện thêm được để chưa xác định. Phát hiện không có đúng một phương án hoặc khóa sai thì chuyển vào cơ chế phục dựng toàn câu hiện có. Không sửa khóa, không tăng số lần gọi AI, không thay giao diện hay cấu trúc câu hỏi.

## Kiểm chứng

- 16 kiểm thử liên quan qua trong 0,447 giây, gồm hồi quy đề 8696, nghiệm đạo hàm kép, khóa sai, điều kiện ngoài phạm vi và phục dựng nguyên câu bảo toàn dữ liệu gốc.
- Toàn bộ 249 kiểm thử local qua trong 310,346 giây. Log ngoài repo: qa_evidence/PR6_PATCH14_UNIQUENESS_FULL_20261028.log.
- Chưa có kết quả CI hoặc Cloud cho bản vá này tại thời điểm viết báo cáo.

## Được, mất và giới hạn

Chặn một lỗi khoa học đã chứng minh bằng tính toán local, không thêm API cho câu đạt. Câu sai có thể dùng ngân sách phục dựng đã có. Phép tính thêm có chi phí CPU nhỏ; chưa đo độ trễ Cloud sau bản vá, không suy ra từ thời gian unit test.

Đây không phải chứng nhận toàn bộ chương trình 2018/KNTT hoặc mọi câu hỏi đều đúng. Còn phải kiểm chứng triển khai, tính ổn định mở đề và các ô môn/lớp chưa thử. Hợp đồng dữ liệu hình cho lần sinh đề ban đầu còn cần đối chiếu với bản vá cũ; không gộp thay đổi prompt chưa kiểm thử vào lần phát hành này.
