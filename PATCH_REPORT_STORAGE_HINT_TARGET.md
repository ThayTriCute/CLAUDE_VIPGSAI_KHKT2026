# Sửa đại lượng cần tìm trong gợi mở dung lượng

Ca Cloud Tin10/3317 hỏi số thẻ nhớ, fallback PR52 lại hỏi số tệp. Nguyên nhân: nhánh dung lượng dùng chung một câu gợi mở cho mọi yêu cầu, chưa phân biệt đại lượng đích.

Sửa hẹp: khi câu hỏi nêu bao nhiêu thẻ nhớ/thiết bị/ổ đĩa, gợi mở hỏi số thiết bị và kiểm tra điều kiện chia tệp; không tự giả định tệp có thể chia, không tính kết quả. Câu hỏi số tệp và hint hợp lệ giữ luồng cũ. Không đổi giao diện, EXPLAIN, key, câu gốc hoặc ngân sách API.

Kiểm local không API:16/16 targeted qua0.009s, có mẫu3317 qua lớp6–12, bảo toàn hint hợp lệ ở65ngữ cảnh và kiểm giữ fallback số tệp. Diffcheck qua. Không chạy lại toàn bộ AppTest vì không đổi UI; CI kiểm bộ hồi quy trước merge. Chưa Cloud tại mốc ghi này.

Giới hạn: lỗi câu gốc thiếu giả định chia tệp vẫn mở, không được coi sửa hint là xác minh đề. Tính đúng phạm vi VonNeumann/CU/ALU theo KNTT lớp10 chưa đối chiếu đủ. Đây là sửa lỗi cụ thể, không chứng nhận chuẩn học thuật toàn hệ thống.
