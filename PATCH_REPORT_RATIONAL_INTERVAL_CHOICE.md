# Kiểm chứng phương án khoảng biến thiên chồng lấn

Ca Cloud PR55/1267 MCQ2: y=(x+1)/(x-2), hỏi khoảng nghịch biến. Đạo hàm -3/(x-2)^2 âm ở mỗi nhánh; A nêu cả hai nhánh và C nêu một nhánh đều đúng theo câu hỏi hiện tại. Không thể giữ câu trắc nghiệm một đáp án như vậy.

Nguyên nhân: kiểm tra điều kiện toán trước đây chưa đối chiếu cả bốn phương án khoảng mở của phân thức tuyến tính. Bản vá dùng dấu ad-bc và cực -d/c để kiểm từng khoảng; nếu không đúng một phương án, chuyển luồng phục dựng/thay toàn câu hiện có. Không sửa khóa hay phương án gốc, không tăng retry/API, không đổi giao diện.

Phạm vi có chủ ý: chỉ công thức phân thức tuyến tính số và câu hỏi chính xác về khoảng đồng/nghịch biến. Điều kiện phụ, tham số, miền chưa hiểu hoặc môn khác trả unknown. Không chứng nhận mọi câu toán hay chương trình KNTT. Phương án chứa nhiều khoảng nối bằng “và” được kiểm từng khoảng; không áp đặt tính cực đại khi đề không yêu cầu.

Kiểm thử: targeted20/20 qua0.295s; full277/277 qua128.139s, log RATIONAL_INTERVAL_TARGETED_FINAL_20261030.log và RATIONAL_INTERVAL_FULL_20261030.log trong qa_evidence. Có kiểm dấu dương/âm, cực ở biên, biểu thức nhân ngoặc, phương án hợp lệ, ngữ cảnh ngoài phạm vi và bank replacement không gọi AI/giữ nguồn. Đây là kiểm thử cấu trúc và các ca toán cụ thể; chưa nghiệm thu mọi môn/lớp hay Cloud trigger.

Được: phát hiện một dạng nhiều đáp án bằng chứng minh xác định, tái dùng bộ phục dựng có sẵn. Chi phí: xử lý SymPy giới hạn độ dài cho dạng câu hẹp; không đo được mức tăng độ trễ Cloud từ test này. Còn mở riêng: P3q6 đề1267 hỏi độ dài khoảng vô hạn, gợi mở chung chung và thẩm định nguồn chương trình/sách.
