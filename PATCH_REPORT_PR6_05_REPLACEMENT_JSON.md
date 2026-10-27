# PR6 — bản vá 05: dùng chung bộ đọc JSON cho câu thay thế

Nền: main `61773bd` (PR33). Ngày 27/10/2026. Mục bản kiểm: JSON-02.

## Nguyên nhân đã tái hiện

Đường tạo đề chính gọi `safe_json_loads`, nhưng nhánh AI thay câu lỗi trong `repair_exam_context` lại gọi `json.loads` trực tiếp và tự cắt code fence. Vì vậy một câu thay thế đủ nội dung nhưng thừa dấu phẩy có thể bị bỏ qua, dù hàm sửa cú pháp đã có sẵn. Nhánh bắt ngoại lệ sau đó giữ câu gốc chưa đủ dữ liệu.

Đã tái hiện tại local với câu thay thế Toán12 có công thức đầy đủ. Trước vá, JSON có fence và dấu phẩy cuối không được nhận; sau vá, giữ đúng câu/phương án/đáp án và phục dựng đúng hệ số từ công thức, chỉ một lần gọi generator giả lập.

## Cách vá

Thay một lệnh đọc chuỗi bằng lazy import và gọi `data.socratic_anchors.safe_json_loads`. Nhánh trả object trực tiếp giữ nguyên. Tái sử dụng parser hữu hạn hiện có, không tạo parser khác, không thay tiêu chí môn/lớp/chủ đề/mức độ hay yêu cầu hình.

Hàm chung còn bảo toàn LaTeX trước khi JSON đọc các chuỗi như `\frac` thành ký tự điều khiển. Kiểm thử mới dùng cả cách escape hợp lệ và chuỗi LaTeX một dấu gạch chéo; giữ nguyên công thức và mô hình phân thức đã phục dựng.

JSON bị cắt mất nội dung và khóa trùng vẫn bị từ chối. Không tự đóng nội dung, bù đáp án hay đổi phương án để câu đạt. Câu sai môn vẫn không được nhận sau khi sửa cú pháp.

## Được, mất và phạm vi

Được: tránh bỏ phí câu thay thế có đủ nội dung vì lỗi cú pháp có thể sửa; thống nhất đường đọc JSON. Không thêm AI/API, retry hoặc giao diện. Không đổi công cụ vẽ, bộ đọc hay Trạm2. Chi phí xử lý chuỗi dùng cùng giới hạn kích thước/số lần sửa của parser đang có.

Bản này không giải quyết ràng buộc kế thừa hình từ câu gốc, không tự dựng dữ kiện còn thiếu và chưa chữa mọi nguyên nhân của `missing_source_visual` trên Cloud. Chưa kết luận JSON lỗi là nguyên nhân của lần CloudToán12 đã ghi log.

## Kiểm thử

Bảy test mới kiểm đường phục dựng thật với generator giả lập: sửa dấu phẩy/fence; giữ dữ liệu hợp lệ; bảo toàn LaTeX phân thức; từ chối JSON bị cắt/khóa trùng; giữ chặn sai môn; kiểm58cặp môn/lớp không phải Ngữvăn; kiểm7lớpNgữvăn giữ nguyên hợp đồng ngữ liệu–câu hỏi–rubric và không bị đưa vào đường thay câu đơn.

Các ca58+7 là kiểm đường dữ liệu kỹ thuật, không phải65caCloudAIthật và không chứng nhận kiến thức/chương trình/KNTT. Bộ toàn dự án đang chạy; kết quả chốt sẽ được bổ sung trước commit.

Kết quả chốt local: 191/191 kiểm thử đạt, 91.931 giây. Log: PR6_PATCH05_JSON_FULL_TESTS_20261027.log trong thư mục QA ngoài repo. Bảy test mới và các ca58+7 nêu trên đều đạt; không có lượt API thật trong bộ kiểm thử.

