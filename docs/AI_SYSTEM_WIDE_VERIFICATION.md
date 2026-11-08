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
