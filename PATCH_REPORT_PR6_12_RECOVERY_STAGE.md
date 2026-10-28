# Phân biệt bước lỗi câu thay thế — 28/10/2026

Ca Cloud8300 trên PR40 chưa mở đề, unresolved2 và hai lượt AI phục dựng. Một câu thiếu hình, một câu trái yêu cầu chỉ bậc ba; cả hai ứng viên ghi replacement_response_error. Chưa biết exception ở provider, decode, recover hay validate. Không gọi là lỗi Socratic hoặc kết luận hết quota.

Đối chiếu 28db430 thấy đã từng có trường stage và loại ngoại lệ. Khôi phục cơ chế đó ở phạm vi hẹp, không nhập vòng retry hoặc thay bộ lọc. Dữ liệu ứng viên phải là object replacement_question; root/list/None thiếu schema được đánh dấu lỗi decode, không trở thành câu rỗng khó chẩn đoán.

Log chỉ chứa bốn tên bước và nhóm ngoại lệ cố định (ValueError, TypeError, KeyError, AttributeError, ImportError, TimeoutError, RuntimeError, OtherError). Không ghi chuỗi ngoại lệ, tên class tùy biến, raw JSON, câu/đáp án hoặc key. Giới hạn log32events và trần2lượt phục dựng giữ nguyên. Không thêm request để lấy chẩn đoán.

17 kiểm thử liên quan đạt4.995s, gồm lỗi giả lập ở cả bốn bước, root schema sai, bảo toàn câu nguồn và whitelist log. Chưa phải bản chữa nguyên nhân exception Cloud; cần mốc triển khai và log thật để kết luận đúng chỗ hỏng. Không đổi giao diện hoặc lời hướng dẫn Socratic.

Bộ hồi quy đầy đủ: 238/238 đạt179.275s; log PR6_PATCH12_RECOVERY_STAGE_FULL_20261028.log ngoài repo. Chưa có log Cloud với các trường stage/error_type mới.
