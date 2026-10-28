# Bản vá 08: hai mâu thuẫn toán học quan sát trên Cloud

## Bằng chứng

Đề7798, Trạm3 Toán12 sau PR36, ngày28/10:

- PhầnI câu1 khẳng định hàm bậc ba đi qua A(0;2), B(1;0), C(-1;6), D(2;0). Nội suy chính xác cho a=0,b=1,c=-3,d=2; giả thiết không thể là hàm bậc ba.
- PhầnIII câu1 yêu cầu biên lớn nhất của m để x^3-3x^2+mx+1 không có cực trị. Đạo hàm có biệt thức36-12m, điều kiện m>=3; tập không có biên lớn nhất hữu hạn.

## Nguyên nhân và sửa

Verifier cũ ưu tiên phân tích công thức tường minh với hệ số số; các hệ số chưa biết và tham số chưa được kiểm tra bằng hai phép chứng minh này. Thêm helper hữu hạn vào verifier đang có, chỉ báo mâu thuẫn đã chứng minh; cơ chế phục dựng hiện tại sẽ tìm/thay nguyên câu. Không đổi phương án hoặc đáp án của câu gốc, không thêm vòng AI, không đổi UI.

Phạm vi được nhận diện: khẳng định hàm bậc ba đi qua bốn điểm có tọa độ số rõ ràng; và dạng tham số tuyến tính ở hệ số x của đa thức bậc ba hỏi biên không tồn tại khi không có cực trị. Không đánh đồng nội suy bậc hai với bậc ba. Biểu thức phân tích bằng parser AST đã có; không eval. Chỉ đọc tối đa10.000ký tự, bốn điểm, tối đa ba biểu thức160ký tự. Ràng buộc bổ sung chưa hiểu không được suy đoán là sai.

## Kiểm và giới hạn

Tám ca riêng gồm hai ca thật, hàm bậc ba hợp lệ, điểm ngoài danh sách, thiếu điểm/câu hỏi tồn tại, hai hướng nửa khoảng, ràng buộc bổ sung, đầu vào không phân tích được và tích hợp thay câu từ ngân hàng không gọi AI. Toàn bộ hồi quy chạy trước phát hành, kết quả lưu ngoài repo trong QA evidence.

Đây không phải chứng nhận mọi công thức, mọi đáp án hoặc CT2018/KNTT. Chưa xử lý yêu cầu số lượng đồ thị hoặc anchorSocratic lệch mục tiêu câu hỏi, đang ghi riêng trong checklist. Câu bị phát hiện có thể cần lượt phục dựng vốn trước đây bỏ sót; trần vẫn giữ hai lượt bổ sung.

Chốt kiểm thử local: 220/220 đạt trong 113.843 giây; tám ca riêng đạt. Chưa coi Cloud đã nghiệm thu bản08 trước triển khai.
