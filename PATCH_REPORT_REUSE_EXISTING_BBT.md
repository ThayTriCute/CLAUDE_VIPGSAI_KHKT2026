# Nối Trạm 3 vào bộ vẽ BBT đã có, bỏ renderer trùng

Ngày 26/10/2026. Người dùng nhắc đúng: app đã có bộ vẽ BBT `_build_svg_bbt_from_rows`, `_normalize_moet_bbt_grid` và `_render_math_html_token`. Lỗi đường hiển thị Trạm 3 là `question_visual_html` đang xuất bảng thô, không gọi bộ vẽ đó. PR26 đã thêm một renderer song song; dù sửa được căn cột, cách này trùng công cụ hiện có và không phải hướng tích hợp phù hợp.

## Điều chỉnh

- Xóa `services/bbt_display.py`, gồm phần HTML/CSS vẽ mới của PR26.
- Thêm `services/bbt_validation.py` chỉ kiểm dữ liệu BBT đầy đủ và chuẩn ký hiệu đầu vào. Không sinh HTML/SVG, không tự thêm mốc, dấu, nghiệm hoặc giá trị.
- `question_visual_html` đưa ba hàng đã kiểm vào **chính `_build_svg_bbt_from_rows` hiện có**. Giữ phần vẽ/kiểu chữ/mũi tên của công cụ cũ; các hình và kiểu bảng khác vẫn ở đường xử lý đã có.
- Giới hạn dữ liệu đầu vào của adapter vì bộ chuẩn hóa cũ có nhánh đoán khi thiếu dấu/mốc. Đường mới chỉ gọi bộ vẽ khi có đầy đủ mốc, dấu và giá trị nhất quán, nên không dựa vào các nhánh tự bù này. Dữ liệu ngoài dạng hỗ trợ giữ fallback escaped cũ; không sửa nội dung nguồn cho vừa renderer.

## Kiểm thử

**6 ca tích hợp nhẹ qua trong 4,726 giây**. Ca thử trích chính các hàm bộ vẽ cũ từ app, kiểm đủ 8 ô mỗi hàng và ba mũi tên SVG, ký hiệu vô cực, giá trị nguồn không đổi, dữ liệu thiếu/mâu thuẫn/HTML không đi vào adapter, bảng số liệu và đồ thị đi kèm vẫn còn. CI đầy đủ và hậu kiểm Cloud trên đề lưu 8551 được xác nhận riêng sau push.

Không đổi engine sinh đề, số lượt AI, câu hỏi/phương án, chấm điểm hoặc các trạm khác. Bài học triển khai: tìm đường gọi đúng công cụ đã có trước khi thêm một bộ thực hiện cùng nhiệm vụ; sửa chỗ tích hợp thay vì xây lại.
