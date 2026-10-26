# Trạm 3: dữ liệu hình cho web và kiểm khoảng đồng biến

Ngày 26/10/2026. Ưu tiên hiện hành: Trạm 3 phải tạo được đề hợp lệ theo tùy chọn và có thời gian chờ hợp lý, giữ nguyên các tính năng. Không lấy test giả lập thay cho hậu kiểm Cloud.

## Bằng chứng lỗi thật

Sau PR24, thử kho một câu Toán 12, chỉ chọn khảo sát hàm số:

- AI tắt: kho không đủ câu phù hợp, app báo thiếu; không mở câu thống kê nhãn sai như lượt trước.
- AI bật: nhận bản nháp dùng `center/tikzpicture/tkzTab` trực tiếp trong `q`, không phải dữ liệu hiển thị được trên web. Sau hai lượt sửa, vẫn bị giữ. Chẩn đoán tải từ khu vực quản trị cho biết lỗi gốc `invalid_math_markup`, hai lần thay thế `invalid_replacement_json_or_data`. Chưa có nguyên văn hai phản hồi thay thế, nên không kết luận chúng đều sai cùng một chi tiết.
- Bản nháp gốc mô tả tăng trên `(-inf;-1)` và `(1;+inf)` nhưng có cả đáp án `(1;3)` và `(-inf;-1)`. Cả hai đúng: khoảng con cũng thỏa tính đồng biến. Việc chỉ sửa cách vẽ mà giữ phương án sẽ vẫn sai khoa học.

## Thay đổi hẹp

1. Hợp đồng dùng chung cho sinh đề và thay câu: văn bản/công thức KaTeX trong q/opt/stmts; hình/bảng ở các trường `f`, `bbt`, `mslgn_data` đã có renderer. Không chèn tài liệu LaTeX/TikZ vào văn bản web. Giữ công cụ xuất LaTeX/TikZ; chỉ hướng dẫn biểu diễn phù hợp ở dữ liệu web. Yêu cầu tự kiểm cả bốn phương án và chú ý khoảng con.
2. Schema thay thế là một object mẫu cụ thể theo p1/p2/p3, có môn/lớp/chủ đề/mức độ, không còn chuỗi mơ hồ `replacement_question: object`. Đây là cải thiện hợp đồng đầu ra, không phải bằng chứng chắc chắn nguyên nhân hai phản hồi trước là thiếu schema.
3. Kiểm độc lập khoảng đơn điệu trong phạm vi hẹp: hàm đa thức số bậc không quá 3, bốn phương án khoảng mở với đầu mút số/hữu tỉ/vô cực. Tính dấu đạo hàm trên mọi phần của từng khoảng, xét cả khoảng con; đếm phương án đúng và so khóa. Không tự sửa khóa hoặc một phương án.
4. Không hiểu định dạng/phủ định/hàm hữu tỉ/đồ thị đạo hàm thì ghi chưa kiểm chứng, không tự kết luận đúng. Giới hạn bậc, chiều dài và hệ số; kiểm mâu thuẫn công thức với dữ liệu mô hình khi cả hai có mặt.
5. Lưu thêm giai đoạn decode/recover/validate ở nhật ký lần sửa bị từ chối. Không tăng số lượt AI; không thay UI, bộ chấm, xuất đề, video, infographic hoặc bộ đọc.

## Kiểm thử

- Nhóm đầu 34 ca qua; nhóm mở rộng 54 ca qua trong 10,428 giây.
- Replay lỗi thật: bản TikZ bị từ chối; bản thay thế có hai khoảng đúng bị từ chối; toàn câu với đúng một phương án hợp lệ được nhận ở lần thay thứ hai. Nguồn không bị sửa, phản hồi lần sau có nguyên nhân kiểm chứng, số lượt vẫn bằng 2. Nhóm 9 ca chuyên biệt qua trong 0,558 giây.
- Các kiểm thử provider ở máy là giả lập. Kết quả hồi quy đầy đủ và hậu kiểm Cloud phải được ghi riêng, không coi replay là đã chứng minh model thật luôn trả đúng.
- Bộ hồi quy đầy đủ: **293 ca qua trong 151,934 giây**. Ca replay cuối được bổ sung sau khi bộ đầy đủ đã nạp danh sách test, nên được chạy riêng trong nhóm 9 ca nêu trên; không gọi đó là 294 ca đã chạy ở cùng lượt tại máy.

## Chi phí và giới hạn

Prompt cụ thể dài thêm; chưa đo token/request vật lý để hứa giảm chi phí. Mục tiêu là tránh nhiều lần sinh sai biểu diễn, không tiết kiệm bằng cách bỏ kiểm đáp án. Bộ kiểm độc lập này chỉ phủ dạng đã nêu, không chứng nhận toàn đề hoặc mọi môn. BBT chỉ có mã TikZ cũ không tự được đổi thành hình và chấp nhận; phải có câu hoàn chỉnh phù hợp và được kiểm lại.
