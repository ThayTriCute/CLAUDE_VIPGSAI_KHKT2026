# Giữ bằng chứng khi đề bị từ chối sau bước đọc JSON

Ngày 26/10/2026, sau khi triển khai PR16 và xác nhận tiến trình Cloud khởi động lúc 23:21:51.202 UTC ngày 25/10, lượt thử Toán 12 với bốn chuyên đề và số câu 12/4/6 đọc được JSON nhưng bị chặn do còn câu chưa đủ dữ liệu hoặc đáp án. Đây là bằng chứng khác với lỗi JSON dòng 558/cột 51 trong ảnh người dùng; chưa được coi hai lỗi là cùng nguyên nhân.

Công cụ chẩn đoán PR16 chỉ giữ ValueError có chữ JSON nên bỏ qua lỗi kiểm tra sau khi phân tích JSON. Bản bổ sung giữ bản nháp cho mọi ValueError của đúng đường tạo đề này, kèm dấu vết context_recovery. Xóa dấu vết lần trước ngay khi bắt đầu lần tạo mới để không gán nhầm lý do. Nhãn mục quản trị được đổi cho đúng phạm vi; không thay bộ lọc, đáp án, số lần gọi AI, giao diện câu hỏi hay ngân sách phục hồi.

Bản nháp vẫn chỉ có một bản trong phiên, giới hạn hai triệu ký tự, che key đang cấu hình và chỉ tải được sau xác thực Trạm 4. Không tự lưu lên kho đề hay dịch vụ khác. Kiểm thử giao diện dùng provider giả xác nhận lỗi JSON và JSON hợp lệ nhưng sai cấu trúc đều được giữ, dữ liệu cũ được xóa, không lộ nút tải ở Trạm 3 hoặc Trạm 4 chưa đăng nhập; một lần gọi provider cho mỗi lần bấm. Ca kiểm thử mở rộng đạt trong 46,726 giây. CI kiểm tra toàn bộ trước khi hợp nhất.

Đây là bổ sung bằng chứng để sửa nguyên nhân, chưa phải kết luận đã sửa dứt điểm lỗi tạo đề hay chứng nhận kiến thức mọi môn/lớp. Tiếp theo phải lấy bản nháp thực tế, tái hiện tại máy và chỉ sửa lỗi đã xác định được.
