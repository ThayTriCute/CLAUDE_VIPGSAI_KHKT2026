# Bản vá 07: câu thống kê bị gắn nhãn khảo sát hàm số

## Bằng chứng và nguyên nhân

Ngày 28/10, sau reboot, Trạm3 mở đề Toán12 theo yêu cầu chỉ hàm bậc ba nhưng có câu khoảng biến thiên của mẫu số liệu ghép nhóm. Truy vấn ngân hàng local thấy đúng văn bản câu này mang topic “Khảo sát và vẽ đồ thị hàm số” trong nhiều bản ghi. Chưa có phản hồi AI gốc hoặc nhật ký thay câu thành công để chứng minh riêng ca Cloud đi qua nhánh nào.

Các bộ chọn câu tin nhãn topic; bản06 kiểm công thức sai dạng nhưng chưa nhận mâu thuẫn của câu không có công thức hàm số. Vì vậy câu thống kê bị gắn nhãn sai vẫn có thể qua.

## Sửa trong phạm vi hẹp

Thêm kiểm mâu thuẫn nội dung mẫu số liệu ghép nhóm với phạm vi chỉ hàm số/đạo hàm ở câu đầu vào và ứng viên thay thế. Ràng buộc cubic-only đã khóa cũng nhận mâu thuẫn này trước khi xuất đề. Câu sai được đưa qua cơ chế thay nguyên câu hiện có; dùng chủ đề giáo viên chọn thay cho nhãn sai của câu gốc.

Không sửa bản ghi nguồn hoặc đáp án, không phân loại bằng từ chung “khảo sát”, không đổi giao diện hay renderer. Câu thống kê vẫn được dùng với chủ đề thống kê/hỗn hợp. Câu có mô hình hóa bằng hàm số không bị loại chỉ vì nhắc số liệu. Các môn khác giữ nguyên. Không tăng trần hai lượt AI bổ sung; có thể dùng lượt sửa đó khi phát hiện câu sai vốn từng lọt qua.

## Kiểm thử và việc còn mở

Sáu kiểm thử riêng gồm văn bản và nhãn sai quan sát được; chọn câu cubic sau ứng viên thống kê gắn nhãn sai; từ chối ứng viên AI sai chủ đề; bảo toàn đề nguồn; chủ đề thống kê/hỗn hợp vẫn mở; kiểm hợp đồng65ngữcảnh. Kết quả hồi quy toàn bộ lưu ngoài repo trong QA evidence, cập nhật sau khi hoàn tất.

Đây là kiểm mâu thuẫn cụ thể có bằng chứng, chưa phải bộ phân loại đầy đủ cho mọi chủ đề/môn hoặc kiểm định chương trình2018/KNTT. Yêu cầu tối thiểu một câu đọc đồ thị chưa được thực thi thành hợp đồng số lượng trong bản này, vẫn ghi riêng để tiếp tục sửa và kiểm.

Kết quả chốt local: 212/212 kiểm thử đạt trong 121.071 giây (28/10/2026). Đây là kiểm hồi quy/fixture, không phải 130 ca Cloud thật.
