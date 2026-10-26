# Một nút tạo đề luyện tập — yêu cầu ngày 26/10/2026

## Yêu cầu và phạm vi

Người dùng yêu cầu gộp hai nút kho/AI trong chế độ luyện tập, bỏ khung giải thích hai luồng, giữ chức năng các chế độ khác. Bản này thay hai nút bằng “Tạo đề luyện tập”, giữ bốn lựa chọn hình thức đề. Các thao tác riêng của đề thật, nạp tệp, quét link và không gian giáo viên không bị gộp hoặc xóa.

## Hành vi

Một lần bấm tìm đề trong kho theo môn/lớp/chủ đề, số câu và tùy biến. Kiểm tra ngữ cảnh khai báo và số câu trước khi đưa bản nháp vào luồng kiểm tra/phục hồi hiện có. Kho đủ thì không gọi AI tạo lại cả đề. Kho không có hoặc chưa đủ cấu trúc: chỉ chuyển sang sinh AI nếu người dùng bật tùy chọn. Khi tắt AI, hiển thị thiếu dữ liệu và không gọi provider. Checkbox giữ nguyên key phiên, đổi nhãn/caption để nói rõ quyền sinh bổ sung và sửa câu.

Bản nháp kho đủ số câu nhưng bị kiểm tra nội dung từ chối vẫn qua ngân sách phục hồi hiện có; nếu chưa đạt, không tự sinh lại toàn đề để che lỗi hoặc tăng thêm lượt AI. Báo lỗi có kiểm soát thay vì để ngoại lệ hiển thị thành lỗi ứng dụng. Gán tùy biến hiện tại trước kiểm tra kho, xóa dấu vết lỗi cũ khi bắt đầu lần mới. Đề mở thành công vẫn dùng cơ chế chấm, lưu bài, thời hạn và chống trùng hiện có.

## Bằng chứng kiểm thử

Sáu ca giao diện tập trung đạt trong 93,076 giây trước hai tinh chỉnh kiểm tra ngữ cảnh kho và xóa dấu vết cũ. Bao phủ: một nút/kho đủ không AI; kho rỗng hoặc thiếu câu và tắt AI; ba chế độ khác giữ điều khiển; fallback AI với JSON thiếu hàng rào đóng; sửa câu hai lượt; chẩn đoán riêng cho quản trị. Các lượt kiểm thử dùng CSDL tạm, ngân hàng/provider mô phỏng, không gọi Gemini thật. Toàn bộ mã cuối tiếp tục được kiểm thử tại máy và CI trước hợp nhất.

Toàn bộ 246 kiểm thử tại máy đạt trong 349,530 giây trước khi tách quyết định nguồn ban đầu thành hàm dùng chung practice_initial_source. Hàm này chỉ quyết định dùng kho/AI/chưa có nguồn, không chứng nhận kiến thức hay mở đề; kiểm tra/phục hồi đầu ra vẫn giữ nguyên. Bảy ca ma trận cuối đạt trong 0,210 giây, gồm kiểm tra quyết định nguồn trên đủ 65 tổ hợp: kho đủ ưu tiên kho kể cả khi bật AI; kho thiếu/sai lớp chỉ chuyển AI khi cho phép; Ngữ văn kiểm tra đoạn đọc và phần viết thay vì áp số câu trắc nghiệm. Tiếp tục chạy ca tích hợp một nút với hàm chung tại máy và toàn bộ CI trên mã cuối trước hợp nhất.

Hai ca tích hợp cuối với hàm nguồn dùng chung đạt trong 62,409 giây: kho đủ mở đề đúng khóa/thời hạn/tùy biến mà không gọi AI; kho rỗng hoặc thiếu câu và tắt AI giữ màn hình cấu hình, không gọi provider. CI phải kiểm tra toàn bộ mã cuối trước hợp nhất. Do thêm hàm được import, cần khởi động lại tiến trình Cloud khi phát hành để tránh trộn app mới và module cũ.

## Giới hạn còn mở

Đổi một nút không tự giải quyết mọi lỗi ngữ liệu. Lượt AI thật trước bản này vẫn bị chặn: một câu tham chiếu đồ thị thiếu hình, một câu có lệnh LaTeX ngoài vùng toán; dấu vết phục hồi ghi unavailable nhưng chưa đủ để xác định nguyên nhân ngoại lệ. Bản nháp đã lưu riêng tại máy để tiếp tục điều tra. Chưa xác minh Trạm 1 và Trạm 3 trên đủ 65 ngữ cảnh về kiến thức/nguồn SGK, không tuyên bố hệ thống hoàn thiện hoặc đúng 100%.
