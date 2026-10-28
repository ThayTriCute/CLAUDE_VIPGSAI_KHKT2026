# Bản vá 15 — phục hồi hướng dẫn dữ liệu web ở lần sinh đề đầu

## Nguyên nhân và bằng chứng

Đối chiếu commit 28db430 cho thấy exam_prompt từng nối WEB_QUESTION_INSTRUCTION vào lần tạo đề ban đầu. Sau phục hồi PR6, bước này bị thiếu; PR40 đã phục hồi hướng dẫn ở bước thay câu lỗi nhưng chưa phục hồi bước tạo đầu tiên. Hai bước vì vậy không cùng biết cấu trúc dữ liệu hình/bảng mà renderer đang nhận.

Thiếu hướng dẫn có thể làm phát sinh câu thiếu dữ liệu và lượt phục dựng. Chưa có bằng chứng rằng đây là nguyên nhân duy nhất của lỗi mở đề 8300 hoặc toàn bộ độ trễ.

## Phạm vi sửa

Khôi phục đúng hai dòng trong services/curriculum_policy.py: import và nối hướng dẫn dùng chung. Không thay giao diện, renderer, dữ liệu nguồn, cơ chế chấm, ngân sách API hoặc số lần thử. Không khôi phục các bộ lọc cứng khác từ commit cũ.

Hướng dẫn chỉ quy định dạng dữ liệu khi câu có hình/bảng; không yêu cầu môn khác phải sinh bài toán hàm số. Các trường hint và explain vẫn tách biệt. Ngữ văn giữ ngữ liệu đọc hiểu và rubric viết riêng.

## Kiểm chứng và giới hạn

31 kiểm thử liên quan đã qua trong 4,570 giây. Kiểm tra cấu trúc prompt và schema của đủ 65 cặp môn/lớp, giữ yêu cầu người dùng, bốn phương án, trường đáp án và hint/explain; không coi đó là kiểm định kiến thức của 65 ngữ cảnh.

Full suite: 251/251 kiểm thử qua trong 159,218 giây. Log qa_evidence/PR6_PATCH15_INITIAL_CONTRACT_FULL_20261029.log. Chưa có đo A/B Cloud cho bản vá này.

## Được và chi phí

Lần sinh đầu có cùng hướng dẫn dữ liệu với bước phục dựng; tránh yêu cầu mô hình đoán schema renderer. Prompt tăng thêm phần hướng dẫn đã có, nhưng không thêm lượt API. Khả năng giảm lượt sửa và tổng token cần đo thực tế, chưa tuyên bố đã giảm. Đây là khôi phục phạm vi hẹp, không phải chứng nhận BigTech hoặc chuẩn chương trình/KNTT toàn bộ.

