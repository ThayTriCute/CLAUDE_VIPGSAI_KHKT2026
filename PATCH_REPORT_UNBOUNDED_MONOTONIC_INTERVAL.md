# Kiểm chứng độ dài khoảng đồng biến vô hạn

Ca Cloud PR55/1267 P3q6 cho f’(x)=(x−1)(x−2)^2(x−3)^3, hỏi khoảng đồng biến tối đại trong x>2 và tính b−a. Dấu đạo hàm dương trên (−∞,1) và (3,+∞); sau giao x>2 chỉ còn (3,+∞). Đề không có độ dài hữu hạn như ô nhập số thông thường yêu cầu.

Nguyên nhân: bộ kiểm điều kiện chưa chứng minh miền dấu của đạo hàm để đối chiếu yêu cầu độ dài khoảng. Bản vá chỉ nhận đúng cấu trúc câu đã quan sát, đạo hàm đa thức số bậc1–8 có các nghiệm thực hữu tỉ. Kiểm dấu trên từng đoạn, nối các đoạn dương qua nghiệm chẵn (đạo hàm bằng0 cô lập không phá đồng biến), giao với x>r. Nếu chỉ có một khoảng tối đại và không bị chặn trên thì đánh dấu câu có đáp số hữu hạn là mâu thuẫn, chuyển bộ phục dựng/thay toàn câu hiện có.

Không chỉnh khóa/câu gốc, không đổi UI/capAPI/retry. Đáp án vô hạn đã nêu rõ được giữ; điều kiện thêm, công thức tham số, nghiệm không hữu tỉ, hướng miền khác, môn khác không bị đoán. Đây là proof hẹp, không phải chứng nhận toàn bộ nội dung toán/chương trình/sách.

Targeted cuối21/21 qua0.274s (UNBOUNDED_INTERVAL_TARGETED_FINAL_20261030.log); full282/282 qua222.895s (UNBOUNDED_INTERVAL_FULL_20261030.log). Có ca hợp lệ khoảng hữu hạn, vôhạn được nêu, nghiệm chẵn, đạo hàm không nghiệm thực, các ngữ cảnh không hỗ trợ, và bank replacement khôngAI/giữ nguồn.

Được: tái dùng công cụ hiện có thay nguyên câu sai, không thêm lượt AI riêng. Chi phí: phép toán ký hiệu có giới hạn bậc/độ dài; chưa đo overhead Cloud. Không giảm cảnh báo nguồn khi chưa đủ đối chiếu và không coi mở app là nghiệm thu câu này.

