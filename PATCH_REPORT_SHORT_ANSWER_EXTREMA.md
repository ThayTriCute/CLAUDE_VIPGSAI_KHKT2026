# Sửa chặn nhầm đáp số cực trị

Tái hiện tại máy ngày 26/10/2026: câu `Hàm số y=x^3-3x có bao nhiêu cực trị?`, đáp số `2`, không có danh sách phương án. SymPy tìm được hai cực trị nhưng bộ audit báo `hallucination_detected=True`, với thông báo tự mâu thuẫn “AI gán đáp án 2 nhưng SymPy giải ra chính xác 2 điểm cực trị”.

Nguyên nhân: nhánh đối chiếu chỉ nhận khóa chữ cái qua bốn phương án; câu trả lời ngắn không có phương án luôn rơi vào nhánh sai. Đồng thời, một phương án mà bộ đọc số chưa hỗ trợ cũng bị coi là sai thay vì chưa xác minh.

Bản vá chỉ đổi cách lấy giá trị đáp án để đối chiếu: nhận đáp số nguyên trực tiếp khi không có phương án; nhận khóa A–D hoặc nguyên văn phương án hợp lệ khi có bốn phương án. Đáp án số khác số cực trị thực vẫn bị chặn. Nếu không đọc được một giá trị số, trả trạng thái chưa xác minh, không gắn nhãn sai hay đã xác minh. Không sửa đáp án nguồn, không tự giải hộ học sinh, không đổi prompt/giao diện/ngân sách AI.

Kiểm thử: 43 ca liên quan kiểm chứng, dữ liệu và phục hồi đạt trong 10,325 giây, gồm đáp số đúng/sai, phương án nguyên văn, phương án bằng chữ chưa hỗ trợ và ca đáp án sai trắc nghiệm cũ. CI toàn bộ phải đạt trước hợp nhất. Lỗi này đã được tái hiện chắc chắn; chưa có bằng chứng nó là nguyên nhân duy nhất của lượt đề Cloud bị chặn. Lỗi JSON dòng 558/cột 51 cần bản nháp thực tế để kết luận riêng.
