# Làm rõ tạo đề và phục hồi câu

Ảnh người dùng chỉ ra checkbox cho phép AI thay câu cùng nút khởi tạo đề AI. Hai chức năng không loại trừ nhau: nút tạo bản nháp ban đầu, checkbox chỉ cho phép lượt AI sửa bổ sung. Tuy nhiên tooltip cũ khẳng định đề AI không lấy bất kỳ câu nào từ kho trong khi enrich_exam_data vẫn dùng ngân hàng để thay câu lỗi; tiêu đề “hai luồng độc lập” vì thế không mô tả đúng hành vi.

Bản sửa chỉ đổi caption, tooltip và nội dung hộp giải thích: hai nguồn khởi tạo cùng đi qua kiểm tra/phục hồi, câu thay được ghi nguồn; bỏ tuyên bố xác minh tuyệt đối và làm rõ giới hạn hai lượt AI sửa cho cả đề. Giữ nguyên nhãn/nút/checkbox, khóa widget, bố cục, thuật toán và ngân sách gọi AI.

Kiểm tra cú pháp đạt. AppTest trên mã mới xác nhận giữ hai nút tạo đề, checkbox mặc định bật; bỏ chọn AI sửa vẫn giữ nút tạo đề ban đầu; nội dung hướng dẫn mới có mặt; mở trang và bật/tắt không gọi provider. Dùng CSDL tạm và provider mock, không gọi Gemini thật. Kết quả lưu ngoài Git tại qa_evidence/generation_recovery_copy_ui_20261026.json. Không thêm kiểm thử riêng cho từng câu chữ tĩnh. Chưa dùng bản sửa diễn đạt này làm bằng chứng hệ thống đã đúng kiến thức hoặc hết lỗi tạo đề.
