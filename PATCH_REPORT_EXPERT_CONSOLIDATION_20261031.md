# Bản ghép kiểm chứng từ gói chuyên gia (31/10/2026)

Không chép đè ZIP. Gói Full và Full(1) giống nhau (193 file); V78 là gói khác (190 file). Đã so sánh diff, giữ nguyên giao diện/nút/cấu trúc học tập và các bản sửa local đã kiểm.

## Đã ghép

- Chuẩn hóa số mũ ngoặc trong phân thức trước SymPy; phục dựng hệ số phân số ở đúng entry point; giữ đồ thị/BBT nguồn và renderer hiện có.
- Bổ sung mã chẩn đoán; JSON đủ root nhưng dư dấu đóng được xử lý có giới hạn, không tự bù nội dung thiếu.
- Bỏ thay thế mù đạo hàm bậc hai; shuffle giữ danh tính đáp án; giải thích không bị nối vào chuỗi mặc định.
- Chấm/xem lại/xuất Đúng–Sai cùng normalize_bool; MCQ review dùng cùng helper grader. Không diễn giải key chưa hiểu thành Đúng hoặc Sai.
- Hết giờ đồng bộ widget của đúng câu trong đề trước chuyển graded; không lấy widget ngoài đề.
- Chú thích ảnh theo page, xử lý page không hợp lệ không crash; prompt yêu cầu số trang; dùng font Unicode một lần/ảnh.
- Ghép cặp Pre/Post qua tên môn đồng nghĩa, giữ bộ lọc lớp/phase/status.
- DOCX kiểm tổng dung lượng giải nén 25MiB; tải URL kiểm public-target và từng redirect, tối đa4request; ghi ngân hàng chung dùng quyền quản trị Trạm4 hiện hữu.
- Nhánh ngân hàng xử lý lỗi draft trước thay trạng thái; không làm văng toàn trang. Câu sai chủ đề không ép nhãn mức độ đề xuất của nó sang câu thay thế. Không tự gán nhãn mức độ mới.
- Từ V78: bỏ câu đã dùng trước giới hạn250candidate, giữ ngân sách kiểm, không tăng lượt AI.
- Giữ luồng system instruction local đã kiểm và link nguồn đã đối chiếu; không đưa framework/corpus pilot chưa tích hợp vào runtime.

## Vì sao không dùng nguyên V78

Đã tái hiện trực tiếp,0API: grade_part1/3 được gọi với point_per_question không có trong signature; grade_part2 trả3giátrị nhưng V78 nhận2; tâm đối xứng trảdict3key nhưng bị unpack2; kiểm tiệm cận x=1 bằng substring chấp nhận nhầm x=10.

Không áp thay đổi công thức thống kê, khóa admin dùng chung mọi người, tăng tải TTS18→48chunk, fallback json.loads toàn shard khi thiếu ijson hoặc tái cấu trúc module chưa có bằng chứng lợi ích. Các helper stations/ui của V78 chưa phải sự tách hoàn chỉnh của app. Không xóa kho/DB/logo trên máy hoặc ghi đè dữ liệu đang dùng.

## Kiểm chứng và giới hạn

- Workspace full345/345 qua227.151s sau các sửa bank boundary/level; sau cải tiến budget V78,43targetedqua2.111s. Ghi rõ mốc: full345 trước budget3line, targeted43 phủ budget mới. CI cần chạy lại đúng commit phát hành.
- Chrome local thật Toán12/KSHS1MCQ/0ĐS/0TLN,AIbổsungtắt/keytrống: mở đề vào làm bài, hiện đồ thị và4radio (snapshot74). Không submit,không ghi kết quả học sinh,0API. Yêu cầu screenshot element bị treo,không lưu ảnh/không nhận đã kiểm pixel.
- Replay ngân hàng thật: câu sai chủ đề→câu đúng chủ đề cóvisual,unresolved0;không đổi source/key và không kế thừa nhãnTH sai.
- Kết quả kỹ thuật không chứng nhận mọi câu hỏi/SGK/KNTT/CT2018/mứcđộmọimôn/lớp. Chưa benchmark latencyCloud,p50/p95;chưa kiểm tiếng thực tế của voice hoặc upload6ảnhT2.
- PublicURLguard không pinDNS,không tuyên bố chống DNSrebinding tuyệt đối; DOCXbudget không chứng nhận mọi file an toàn. Metadata nguồn chưa kiểm không biến thành chứng nhận đề thật.

Checklist cũ được giữ để tham chiếu; ưu tiên đợt này là ghép nhận xét chuyên gia có kiểm chứng. Không tăng API retry/cap. Các số liệu này không phải chứng nhận “Bigtech” hay bảo đảm tuyệt đối không lỗi.
