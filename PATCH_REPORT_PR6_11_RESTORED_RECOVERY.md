# Khôi phục chọn lọc hợp đồng phục dựng cũ — 28/10/2026

## Bằng chứng

Ca Cloud đề 2195 ghi unresolved=2, p1 câu 3 và p2 câu 1 thiếu dữ liệu hình sau hai lượt phục dựng. Log chỉ ghi lý do câu gốc, chưa đủ xác định câu AI thay thế đã thiếu hình, sai schema hay bị từ chối do điều kiện khác. Không quy ca này cho Socratic khi chưa có bằng chứng.

Theo nhắc nhở của người dùng, đối chiếu lịch sử tìm thấy e0dbab1 đã phân biệt yêu cầu lập bảng với bảng cho sẵn; 28db430 đã cung cấp schema cụ thể cho bộ dựng web. Hai phần này đã mất sau phục hồi PR6. Khôi phục đúng các phần nhỏ liên quan, không nhập lại bộ lọc xuất bản quá rộng hay thay UI.

## Thay đổi

- Khôi phục needs_visual từ e0dbab1: lập bảng là nhiệm vụ đầu ra; tham chiếu hình/bảng đầu vào vẫn cần dữ liệu.
- Khôi phục services/web_question_contract.py từ 28db430, chỉ ghép vào prompt thay câu. Schema phân biệt opt/ans với stmts và dữ liệu f/bbt mà renderer hiện có đọc được; giữ yêu cầu đã khóa và giới hạn hai lượt.
- _candidate_issue trả mã lý do; _candidate_ok giữ giao diện boolean cũ. Bỏ lượt kiểm SymPy thứ hai vì _question_issue đã chạy cùng bộ kiểm. Chấp nhận/từ chối về mặt toán không thay đổi.
- Log bổ sung replacement_rejection chỉ nhận danh sách mã cố định; không ghi câu hỏi, đáp án, khóa API, tên hoặc ngoại lệ. Không thêm request AI để lấy chẩn đoán.

## Được, mất và giới hạn

Giảm một lần kiểm toán ứng viên; chưa đo được độ trễ Cloud tiết kiệm. Prompt thay câu dài thêm để mô tả schema; không thêm số lượt gọi. Không tự dựng hình thiếu dữ kiện, không sửa riêng phương án/khóa chấm để ép hợp lệ. Điều kiện giữ nhiệm vụ đọc hình từ câu gốc còn nguyên và được kiểm thử; nếu chính điều kiện này gây từ chối sẽ có mã riêng để xem xét dựa trên bằng chứng.

Không khôi phục vòng retry cũ efef1d5 trong bản này: trường hợp nhiều câu hỏng cần xem phân bổ ngân sách tổng trước, không gộp vào thay đổi schema.

36 kiểm thử liên quan đạt trong 5.217 giây. Có kiểm schema cho 65 cặp môn/lớp, bảo toàn câu nguồn, chặn câu sai, nhận diện bảng đầu ra/đầu vào và an toàn log. Đây là fixture, không phải 65 lượt Cloud hay xác minh chương trình/KNTT. Kết quả toàn bộ và Cloud ghi trong biên bản riêng khi hoàn tất.

Bộ hồi quy đầy đủ: 235/235 đạt trong 153.412 giây. Log ngoài repo: PR6_PATCH11_RESTORED_RECOVERY_FULL_20261028.log. Chưa nghiệm thu Cloud.
