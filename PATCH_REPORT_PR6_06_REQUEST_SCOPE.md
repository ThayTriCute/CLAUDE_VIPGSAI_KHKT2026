# Bản vá 06: giữ phạm vi yêu cầu khi thay câu

## Lỗi quan sát

Cloud main 996a280: yêu cầu đã khóa chỉ hàm bậc ba nhưng đề mở được lại có câu tiệm cận của hàm phân thức. Không lưu được phản hồi AI gốc nên chưa quy lỗi riêng cho lần sinh đầu hay lần thay câu.

## Nguyên nhân và cách sửa

Đường phục dựng chưa nhận yêu cầu tùy biến đã khóa; việc kiểm môn/lớp/chủ đề không đủ kiểm phạm vi đó. Truyền yêu cầu vào đường tạo đề luyện tập và câu thay thế, lặp ràng buộc đã nhận diện trong prompt, kiểm mâu thuẫn trước khi chọn câu ngân hàng/AI và trước khi xuất đề. Câu không đạt đi qua cơ chế thay nguyên câu hiện có. Giữ giới hạn hai lần gọi bổ sung; không thêm vòng lặp vô hạn.

Kiểm xác định chỉ áp dụng yêu cầu rõ ràng chỉ hàm bậc ba trong môn Toán. Phân biệt dạng hàm với tính đồng/nghịch biến; không nhận đường tiếp tuyến hay đạo hàm là hàm gốc. Không rút gọn mất điều kiện xác định của phân thức. Biểu thức chưa phân tích được không bị cấm hàng loạt và không được coi là đã xác minh.

Không đổi bố cục, radio, infographic, video, Polya, Socratic, giọng đọc hay công cụ đồ thị/BBT. Đề nguồn nguyên bản/cached/import không nhận yêu cầu tùy biến cũ qua tham số mặc định.

## Kiểm thử và giới hạn

- 15 kiểm thử riêng đạt; gồm hàm bậc ba đồng/nghịch biến trên R, phân thức, bậc nhất/bốn, tiếp tuyến, đạo hàm, mẫu có lỗ miền xác định, thay câu rồi xuất đề, truyền yêu cầu qua hàm app thật.
- Toàn bộ 206 kiểm thử local đạt trong 104.549 giây. Các ca 65 ngữ cảnh là kiểm hợp đồng dữ liệu bằng fixture, không phải 65 ca sinh AI thật hay chứng nhận kiến thức.
- Local Chrome localhost:8526 mở được Trạm 1 trước triển khai.
- Chưa kết luận Cloud đạt cho bản này trước khi triển khai và kiểm lại.

Chi phí: đề sai phạm vi có thể cần một lượt sửa vốn trước đây bị bỏ sót; prompt thay câu dài thêm phần yêu cầu. Không tăng trần gọi bổ sung. Không tuyên bố mọi tùy biến tự do, toàn bộ chương trình 2018/KNTT hoặc kiến thức đã được kiểm chứng. Các mục đó vẫn cần nguồn đối chiếu và kiểm chuyên môn riêng.
