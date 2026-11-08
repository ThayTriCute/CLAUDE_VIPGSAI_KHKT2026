# Kiểm chứng và sửa lỗi cho toàn hệ thống

Áp dụng mọi môn/lớp, Trạm1–2–3, model chính và dự phòng. Bài đang kiểm là ca tái hiện, không phải giới hạn phạm vi bản vá.

Ứng dụng chèn quy tắc cốt lõi từ ACADEMIC_GROUNDING_GUIDANCE qua with_academic_grounding vào cả transport JSON và streaming trước vòng fallback. API không tự đọc file này hoặc ổ F. Nguồn đúng bài phải được ứng dụng đưa vào ngữ cảnh. Hướng dẫn không bảo đảm mọi đầu ra đều đúng.

AI làm việc với repo phải:

1. Đọc checkpoint/queue/owner mới nhất; giữ đóng các mục owner đã duyệt, không kiểm hoặc sinh lại chỉ vì thiếu snapshot cũ.
2. Kiểm local bằng mã và đọc bản lưu trước; đối chiếu kho nén đúng bài, chỉ tra ngoài khi thiếu hoặc cần xác tín điểm cụ thể. Không mặc định gọi thêm AI để chấm AI.
3. Tìm tầng sở hữu lỗi: prompt/parser/kiểm định/trạng thái/renderer/export; sửa tầng dùng chung với phạm vi nhỏ nhất. Kiến thức riêng môn/bài phải giữ phạm vi riêng, không phát tán đặc lệ sang môn khác.
4. Lưu ca thật trước/sau, kiểm đường liên quan và trường hợp phải giữ nguyên. Bảo toàn UI/features; không tăng retry, sinh trùng hoặc tạo lịch/phiên AI.
5. Dùng Chrome khi có nghi vấn, cần xem hình/công thức/bản in hoặc kiểm đại diện sau bản vá chung. Không coi chưa mở UI là đã kiểm UI. Xác nhận in tùy chọn không chặn việc độc lập.
6. Ghi riêng kiểm cơ học, nghiệm thu ngữ nghĩa, phủ chương trình và owner duyệt. Không có cảnh báo không chứng nhận toàn SGK/YCCĐ/pháp luật. Ghi riêng local/push/CI/main/Cloud theo đợt owner cho phép.

Công cụ QA workspace qa_evidence/audit_saved_lesson_local.py dùng parser/validator có sẵn, không API và không sửa bài; kiểm context/hash/cấu trúc câu hỏi và một số cờ nghi vấn, không chứng minh đáp án đều đúng. Không đưa dữ liệu phiên, khóa hoặc DB lên GitHub để chạy công cụ.

Khi nguồn nêu ranh giới đoạn/câu/dòng, dùng đúng phạm vi đó, không lấy bản trích quen thuộc thay thế. Đối chiếu người nói, số câu trong gợi ý, câu hỏi và đáp án; diễn giải không phải nguyên văn. Tự luận cần gợi ý lời giải/rubric có nội dung và chấp nhận lập luận khác có bằng chứng. Ca thật Văn11 Trao duyên (SGK711–758) là bằng chứng lỗi phạm vi, không giới hạn quy tắc ở môn Văn.


Khi dựng đồ thị/Lab, phương trình và nhãn phải dùng cùng hệ số với dữ liệu đang tính; không làm tròn hệ số rồi vẫn ghi dấu bằng. Nếu chỉ trình bày gần đúng, ghi rõ gần đúng và mức chính xác. Đối chiếu đơn vị từng phiên bản nguồn trước ghép số liệu; ví dụ bản mẫu và bản tái bản có thể khác đơn vị trục. Chỉ lấy hình/tình huống đang kiểm làm ca tái hiện, áp dụng quy tắc cho mọi môn/lớp.


Ranh giới bắt buộc cho mọi AI — metadata tác giả: OUTCOME, COGNITIVE_REASON, COGNITIVE_STEPS là trường kỹ thuật của dữ liệu sinh bài/đánh giá, không phải nội dung giao diện, phiếu học hay bản in học sinh. Giữ các trường cần thiết trong JSON gốc để parser/đánh giá dùng; không xóa schema hoặc dịch tên khóa để che lỗi. Các tầng hiển thị/xuất/infographic hướng học sinh phải dùng bộ lọc chung student_essay_text, giữ câu hỏi, bước giải, công thức, đáp án và rubric. Bảo vệ ví dụ mã và xử lí JSON nhiều dòng; không xóa nhầm bài kế tiếp khi metadata hỏng. Áp dụng đa môn/đa lớp, không chỉ bài Vật lí11 tái hiện. Kiểm đường xuất thật, không coi dữ liệu JSON có trường kỹ thuật là giao diện đã sai.
