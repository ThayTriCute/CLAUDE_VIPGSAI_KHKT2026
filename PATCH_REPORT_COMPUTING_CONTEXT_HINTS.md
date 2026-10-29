# Gợi mở Tin học theo ngữ cảnh câu hỏi

Ca Cloud Tin7/8511: gợi mở CPU lặp lại ẩn dụ bộ não từ phương án đúng; phần đúng/sai kết nối và trả lời ngắn dung lượng dùng câu hỏi chung đầu vào/đầu ra.

Nguyên nhân: guiding_question chỉ loại dấu đáp án và chuỗi phương án nguyên văn, không nhận mọi diễn đạt lại; fallback Tin học chỉ có một câu chung. Không phải lỗi câu hỏi/khóa chấm (ca8511 đã đối chiếu10/10).

Sửa hẹp services/socratic_context.py: fallback theo câu hỏi CPU, dung lượng tệp/thẻ nhớ, kết nối thiết bị số. Riêng câu nêu CPU có hint bộ não thì thay bằng gợi mở phân biệt vai trò. Hint hợp lệ khác giữ nguyên. Không thay giao diện, EXPLAIN, câu hỏi, phương án, khóa, cách chấm hay số gọi AI.

Đánh đổi: nhận diện có phạm vi và từ khóa, không phải bộ kiểm chứng ngữ nghĩa toàn diện. Câu ngoài phạm vi giữ luồng cũ; chưa chứng nhận mọi hint không lộ đáp án hoặc đúng KNTT. Mất ẩn dụ CPU quá trực tiếp, được gợi mở theo nhiệm vụ và không cần API bổ sung.

Kiểm chứng: 15/15 targeted qua0.008s, có vòng65ngữcảnh giữ hint hợp lệ, CPU lớp6–12, kiểm không ra số dung lượng. Fullsuite264/264 qua231.276s (COMPUTING_HINTS_FULL_20261029.log), khôngAPI. Chưa push/CI/Cloud ở mốc ghi này. Evidence ca gốc ở qa_evidence/PR51_TIN7_8511_*.
