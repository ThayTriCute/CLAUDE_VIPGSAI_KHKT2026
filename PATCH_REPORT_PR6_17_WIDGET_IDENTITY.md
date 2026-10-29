# Bản vá 17 — đồng bộ ô yêu cầu và định danh theo ngữ cảnh

## Bằng chứng còn lỗi sau PR45

Trên Cloud sau PR45, đổi Toán12 sang Toán7: banner xác nhận nội dung cũ đã mất, nhưng screenshot vẫn thấy ô nhập chứa yêu cầu lớp12. PR45 mới xác minh trạng thái server; chưa đủ bằng chứng cho giá trị hiển thị trong trình duyệt. Không gọi AI khi phát hiện. Bằng chứng ngoài repo: PR45_GRADE7_VISIBLE_STALE_WIDGET_20261029.png.

Kiểm thử mở rộng bằng nhập widget thật còn phát hiện hai ô yêu cầu học sinh/giáo viên ghi vào cùng model mỗi rerun: ô chưa sửa có thể ghi đè văn bản vừa nhập. Lần targeted đầu của patch17 thất bại ở bước phục hồi bản nháp, log PR6_PATCH17_WIDGET_TARGETED_20261029.log. Không phát hành lần thất bại này.

## Thay đổi có giới hạn

- Key của hai textarea gắn current_context_key, giúp widget ở môn/lớp mới có định danh riêng.
- Callback của mỗi ô đồng bộ model và widget phía còn lại trong cùng context, trước rerun. Giữ nguyên nhãn, vị trí, nút và các tính năng.
- Tái dùng bản nháp riêng của PR45; đổi môn/lớp không mang nội dung cũ sang, quay lại vẫn có bản nháp. Không tăng API hoặc số lần thử.

## Kiểm chứng

6/6 kiểm thử liên quan qua34,088s: nhập từ khu học sinh, chỉnh từ khu giáo viên, đổi key và giá trị hiển thị khi đổi lớp, khôi phục bản nháp; cùng kiểm tra tách trạng thái65cặp môn/lớp. Full suite254/254đãqua152,473s; log PR6_PATCH17_WIDGET_FULL_20261029.log ngoài repo.

Phải thử lại trực quan Cloud sau triển khai; AppTest không thay thế bằng chứng trình duyệt. Các kiểm thử này không chứng nhận kiến thức65ngữ cảnh. Chưa đo lợi ích độ trễ/token; bản vá chỉ thêm đồng bộ trạng thái, không thêm lượt AI.

