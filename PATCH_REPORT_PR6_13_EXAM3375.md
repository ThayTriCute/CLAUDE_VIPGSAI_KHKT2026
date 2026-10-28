# Hai lỗi thực tế từ đề3375 — 28/10/2026

## Bằng chứng Cloud

Sau PR41 và restart20:48:08VN, một lượt Toán12, ma trận3/1/1, cubic-only đã mở đề3375. Lần đầu quan sát có kết quả khoảng45s, gồm khoảng giữa các lần đọc, không phải p95. Hai hint trục tung/tọa độ cực tiểu bám câu hỏi và chưa tiết lộ đáp án. Ba MCQ và bốn ý đúng/sai được đối chiếu thủ công rồi nhập qua UI; chấm đúng3/3 và4/4.

Ca vẫn KHÔNG ĐẠT: phương án D câu3 hiện nguyên (0; +\infty); câu ngắn quy định nhập999 nếu tập nghiệm là khoảng nhưng khóa chấm0. Thử nhập999 bị chấm0/3, tổng7/10; chính explain cũng kết luận khoảng(-1;1) và nhắc999. Không lấy việc mở được đề hoặc điểm của các phần khác làm chứng nhận toàn bộ đề.

## Cách sửa và phạm vi

1. Thêm module nhỏ parameter_interval_contract, gọi từ bộ kiểm toán hiện có. Chỉ đưa kết luận với mẫu nhiệm vụ đã quan sát, không có thêm điều kiện chưa hiểu, hàm bậc3 và đạo hàm bậc2 có discriminant hằng dương, hệ số tham số không quá bậc2 ở tích nghiệm. SymPy chứng minh tập tham số là một khoảng không rỗng; nếu khóa số khác mã khoảng được câu hỏi quy định thì trả cờ mâu thuẫn. Bộ phục dựng hiện có xử lý thay nguyên câu. Không sửa ans, explain hoặc đáp án học sinh.
2. Với biểu thức/nhiệm vụ/điều kiện khác, trả chưa có kết luận. Không dùng keyword999 làm lệnh cấm chung, không nhận định mọi bài tham số hay câu khác môn đã được chứng minh. Không tự gọi quy ước999 là chuẩn Bộ; chất lượng thiết kế câu này vẫn phải rà.
3. Tái dùng preserve_math_and_code để chỉ bọc khoảng số chứa \infty còn trần vào math Markdown. Gắn format_func cho radio trắc nghiệm T1/T3, giữ options gốc, key widget, lựa chọn và scoring identity. Không thay bố cục/radio, không sửa đoạn English, mã lập trình hay math đã có dấu phân cách.

## Chi phí và kiểm thử

Không thêm thư viện hay request AI. Kiểm toán chỉ chạy cho mẫu hẹp có bằng chứng; một câu sai thật có thể dùng lượt thay câu trong trần hiện có. Không giảm kiểm chứng để ép mở đề.

13 kiểm thử liên quan đạt1.123s; mẫu thêm điều kiện lạ, MCQ, môn khác, khóa đúng không bị quy tắc mới đoán kết luận. Kiểm hiển thị gồm65cặp môn/lớp qua fixture và giữ giá trị lựa chọn gốc. Đây không phải65lượtCloud hay chứng minh mọi công thức chuẩn chương trình/KNTT. Kết quả hồi quy đầy đủ và nghiệm thu Cloud ghi sau khi hoàn tất.

Bộ hồi quy đầy đủ: 245/245 đạt190.245s, log PR6_PATCH13_3375_FULL_20261028.log. Chưa nghiệm thu Cloud bản13.
