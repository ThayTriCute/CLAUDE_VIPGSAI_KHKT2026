# PR6 — bản vá 04: chẩn đoán lỗi phục dựng đề

Nền: main `0755040`. Ngày 27/10/2026.

## Vấn đề thực tế

Trạm 3 Toán 12, đề thử 3/1/1, hiện hai thông báo phản hồi AI rồi báo còn câu thiếu dữ liệu/đáp án. Ứng dụng chỉ lưu `context_recovery` trong phiên và đưa thông báo chung; nhật ký chưa chỉ được phần, số câu và lý do của lỗi thật. Cần bằng chứng này trước khi thay đổi bộ lọc.

Ca Ngữ văn 6 sau đó bị đóng WebSocket 1006, bộ đếm về 0 và quay lại Trạm 1. Kết quả tạo đề của ca đó chưa xác định; không coi đây là lỗi kiến thức hay đã chứng minh Cloud sập toàn hệ thống. Người dùng trước đó xác nhận vẫn vào được nội dung ở phiên khác.

## Thay đổi

Thêm `services/recovery_diagnostics.py` và hai dòng tại nhánh `enrich_exam_data` có `unresolved`. Mỗi lần phục dựng thất bại ghi một bản ghi `GSAI_RECOVERY_UNRESOLVED` gồm:

- Môn và lớp thuộc tập hỗ trợ; phần p1/p2/p3; số câu bắt đầu từ 1.
- Action/reason thuộc danh sách cố định; số lượt AI phục dựng; số câu chưa đạt.
- Tối đa 32 sự kiện; có cờ báo phần bị cắt khỏi log.

Không ghi nội dung câu hỏi, đáp án, hash câu, ngoại lệ dạng văn bản, API key hay thông tin học sinh. Giá trị ngoài danh sách cố định trở thành `unknown`. Nếu logger lỗi, quyết định xuất đề và thông báo lỗi ban đầu vẫn giữ nguyên.

## Phạm vi và đánh đổi

Giữ nguyên giao diện, prompt, câu hỏi/đáp án, tiêu chí kiểm định, model, retry và giới hạn phục dựng. Không thêm lượt gọi AI hay widget. Đề đạt tiếp tục đi theo nhánh cũ và không ghi cảnh báo này. Chi phí bổ sung là tạo một cấu trúc nhỏ và một dòng log có giới hạn khi phục dựng thất bại.

Bản vá không thay công cụ vẽ, bộ đọc hay Trạm 2. Chưa nhập cấu hình tối ưu cũ trong cùng bản này để tránh trộn nhiều yếu tố.

## Kiểm thử local

- 184/184 kiểm thử toàn dự án đạt, 102.755 giây. Log: `PR6_PATCH04_DIAGNOSTICS_FULL_TESTS_20261027.log` trong thư mục QA ngoài repo.
- 8 kiểm thử mới: không lộ nội dung, lọc mã ngoài danh sách, giới hạn log, logger lỗi không ảnh hưởng luồng, nhánh xuất đề đạt/không đạt.
- Hàm `enrich_exam_data` thực lấy từ AST của app được chạy ở cả hai nhánh cho đủ 65 cặp môn/lớp hỗ trợ. Nguồn/AI được mock; kiểm chứng này dành cho ranh giới chẩn đoán, không phải 130 ca sinh nội dung thật trên Cloud hay chứng nhận học thuật.
- Kiểm thử giữ nguyên giới hạn hai lượt phục dựng và xác nhận logging không tự gọi AI.

## Giới hạn và bước đo tiếp

Chưa có dữ liệu gốc đủ để xác định lỗi Toán 12 là thiếu hình, sai đáp án hay sai cấu trúc. Bản ghi mới sẽ phân biệt các nhóm nguyên nhân đó khi lỗi lặp lại; chưa đủ để tự xác nhận mọi đáp án đúng.

Mỗi hàm gọi AI hiện có deadline 240 giây, và Trạm 3 có thể thêm hai lượt phục dựng. Cấu hình có thể cộng dồn thời gian chờ; chưa đo usage và thời gian từng request thật, chưa chứng minh đây là nguyên nhân mất phiên. Bản 04 không đổi ngân sách này.

Ma trận Cloud thật vẫn chưa đủ 65 cặp. Không dùng kết quả local để điền đạt cho ca Cloud chưa chạy. Việc đạt kiểm thử không phải chứng nhận chương trình, KNTT, pháp quy hay hết lag.
