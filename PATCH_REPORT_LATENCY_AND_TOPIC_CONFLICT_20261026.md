# Đo Trạm 1–3 và vá mâu thuẫn nhãn chủ đề

Ngày 26/10/2026. Sửa tại máy, kiểm thử trước khi push. Phạm vi sản phẩm: một cấu hình chạy và một kiểm tra mâu thuẫn đã tái hiện; không đổi bố cục, không cắt tính năng.

## Nguyên nhân và thay đổi

1. **Chi phí biên dịch không cần thiết.** App gọi hiển thị tường minh bằng `st.*`/component, nhưng Streamlit vẫn quét cây cú pháp để thêm hiển thị biểu thức kiểu notebook. Thử `magic.add_magic` trên app mất 2,539 giây; không thêm một lệnh hiển thị ngầm nào. Cấu hình `runner.magicEnabled=false` bỏ bước đó. Ca hồi quy dùng bộ biến đổi thực của Streamlit để phát hiện nếu sau này mã bắt đầu phụ thuộc hiển thị ngầm. Không thay bộ lọc, engine AI hay nội dung học tập.

   AppTest biên dịch lại mã qua từng lượt nên hưởng lợi rõ hơn phiên Cloud đã có bytecode. Không diễn giải mức giảm tại máy là mức giảm tương đương cho mọi nút Cloud. Cold import thư viện và cold load shard vẫn tồn tại.

2. **Nhãn nguồn sai làm câu lệch chuyên đề.** Lượt thử thật trên Cloud chỉ chọn khảo sát hàm số Toán 12 nhưng xuất câu hỏi khoảng biến thiên của mẫu ghép nhóm. Đối chiếu shard tại máy thấy chính câu này được gắn `topic=Khảo sát và vẽ đồ thị hàm số`; tìm thấy ở ít nhất ba bản ghi, gồm `MATH_12_CK1_KHTN_P1_TH_01`. Lọc dựa vào nhãn đã tin dữ liệu sai.

   Thêm kiểm tra xác định, hẹp: nhãn chỉ hàm số/đạo hàm mâu thuẫn với yêu cầu thống kê ghép nhóm rõ ràng, trong khi đề không yêu cầu hàm số/đạo hàm. Loại trước khi chọn từ kho để tránh gọi AI sửa không cần thiết. Cửa phạm vi cuối cũng phát hiện mâu thuẫn để bộ phục hồi hiện có thay **nguyên câu**, kiểm tra lại phương án/khóa chấm và giữ dấu vết. Không tự đổi riêng nhãn, số hoặc đáp án; không sửa/xóa các bản nguồn. Câu thống kê đúng nhãn và bài thực sự kết hợp hàm số được giữ. Quy tắc này không phải bộ hiểu ngữ nghĩa mọi môn.

## Kết quả đo tại máy

Hai ma trận đều 65/65 tổ hợp môn/lớp, Trạm 1 và Trạm 3 đều qua, không có ca lỗi. Dữ liệu AI/kho được giả lập; không gọi Gemini thật trong hai lượt này. Thời gian có AppTest, render phía Python và nạp kho cục bộ, không có trình duyệt/KaTeX thực hay thời gian provider AI.

| Thao tác | Trung vị trước | Trung vị sau | P95 trước | P95 sau |
|---|---:|---:|---:|---:|
| Chọn ngữ cảnh Trạm 1 | 3,348 s | 1,175 s | 3,923 s | 1,714 s |
| Soạn bài với provider giả lập | 3,428 s | 1,378 s | 4,353 s | 2,485 s |
| Mở Trạm 3 | 7,638 s | 5,240 s | 12,598 s | 9,231 s |
| Tạo đề với kho giả lập | 3,279 s | 1,210 s | 4,114 s | 2,371 s |

Toàn lượt: 1.266,03 giây trước, 679,99 giây sau. Không phải thử tải đồng thời hoặc thử nghiệm hiệu năng có kiểm soát máy tuyệt đối. Lượt sau có một lần đọc shard nguồn riêng ngắn trong quá trình đối chiếu, có thể ảnh hưởng một số số đo. `app_start_seconds` là một lần mở mỗi khối, lặp lại trong các dòng của khối đó; không lấy đó làm 65 mẫu độc lập.

Kiểm tra giữ tính năng ở mỗi tổ hợp: đúng môn/lớp phiên bài và đề, 3 MCQ/radio, 2 bài tự luận với nhãn Pólya tiếng Việt, không lộ dữ liệu lời giải riêng trong nội dung, infographic và link video, nút tạo đề duy nhất, cấu trúc riêng Ngữ văn. Đây không phải kiểm tra hết mọi nhánh upload, camera, xuất bản in, âm thanh thực hoặc kiến thức từng câu. Lượt UI sau tối ưu đã bắt đầu trước khi thêm quy tắc mâu thuẫn; quy tắc mới được kiểm tra riêng và trong bộ hồi quy đầy đủ.

Ma trận lưu ở `tests/evidence/latency_all_contexts_before_20261026.json` và `tests/evidence/latency_all_contexts_after_20261026.json`.

**Hồi quy toàn bộ: 285 ca qua trong 266,287 giây** tại máy, sau khi có cả quy tắc mâu thuẫn và cấu hình mới. Nhóm mâu thuẫn ban đầu có 4 ca thất bại trong 5 ca trước sửa; sau sửa nhóm kết hợp phạm vi qua 16 ca, rồi thêm bảo vệ không rò quy tắc sang 65 tổ hợp và chạy bộ đầy đủ. Không có thay đổi source ngoài phạm vi nêu trên để làm test qua.

## Kiểm tra Cloud và giới hạn

- Sau PR23, Cloud đã cập nhật app nhưng tiến trình chưa restart, xuất ImportError với helper mới `lesson_topic_placeholder`. Đã reboot bằng quyền đã được người dùng đồng ý và xác nhận placeholder mới xuất hiện, Trạm 1/3 mở được. Đó là bằng chứng phục hồi lần triển khai này, không phải chứng minh mọi lỗi import đã hết vĩnh viễn.
- Sáu lượt chuyển nóng Toán 12 giữa Trạm 1–3 tới khi nút chính hiện: 1,747–3,592 giây, gồm công cụ điều khiển/mạng. Đây là mẫu nhỏ trước tối ưu mới, không có P95 đại diện cho toàn hệ thống.
- Lượt tạo đề thật một câu mở được đề, phát hiện câu lệch chuyên đề nêu trên. Đến lúc lấy snapshot kết quả đã 46,156 giây từ click, nhưng có khoảng không quan sát giữa hai lần đọc; đây chỉ là cận trên quan sát, không phải thời gian AI hoặc thời điểm hoàn tất chính xác. Không xác nhận số request/token vật lý của provider.
- Một bài học thật Toán 12 về đơn điệu/cực trị hàm bậc ba xuất được ở Trạm 1: 3 nhóm chọn đáp án, hai bài có bốn bước Pólya và link YouTube; không có `.katex-error` trong DOM chính khi kiểm tra. Snapshot đầu có bài sau 35,202 giây từ click, cũng chỉ là cận trên quan sát. Chưa kiểm toàn bộ iframe infographic hoặc mọi kiến thức của bài. Lượt này trên PR23, trước khi triển khai tối ưu mới.

## Đánh giá và bước tiếp

Mở Trạm 3 cold còn chậm; cần xem metadata catalog/shard load theo số đo tiếp theo. Không tăng cache toàn bộ môn vì có nguy cơ bộ nhớ; không cắt bộ lọc hay tính năng để làm đẹp số đo. Chưa có bằng chứng gọi đây là hiệu năng Big Tech hoặc chứng nhận chương trình/SGK/Bộ. Nguồn pháp quy, từng yêu cầu cần đạt và từng nội dung AI vẫn cần đối chiếu; chưa bỏ cảnh báo vàng đồng loạt.

Âm thanh phát thực tế/giọng Nam Bộ/nhân bản giọng và phạm vi các Lab là những phần chưa hoàn tất. Bản này không đổi mã giọng đọc hoặc Lab. Không tăng giới hạn lượt AI hay thêm nhà cung cấp trả phí.
