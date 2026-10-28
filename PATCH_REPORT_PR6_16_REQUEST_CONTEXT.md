# Bản vá 16 — yêu cầu tùy biến riêng theo môn/lớp

## Lỗi thực tế và nguyên nhân

Sau PR44, đổi Toán lớp12 sang lớp7 trên Cloud: chủ đề và đề cũ được reset, nhưng ô yêu cầu cùng khung xác nhận vẫn chứa yêu cầu khảo sát hàm bậc ba lớp12. Chưa bấm sinh đề khi thấy mâu thuẫn, không tiêu thêm API để tái hiện.

Block đổi ngữ cảnh đã xóa dữ liệu đề/bài học nhưng bỏ sót các khóa yêu cầu và widget dùng chung. Đây là lỗi trạng thái cấu hình, không phải bằng chứng mô hình đã sinh kiến thức lớp7 sai.

## Cách sửa và được–mất

Dùng module widget_state có sẵn, thêm helper lưu bản nháp theo context. Trong block đổi môn/lớp hiện có, trước render widget: giữ bản nháp context cũ, bỏ các khóa yêu cầu đang hoạt động và custom_request_text thuộc lần thi cũ, phục hồi bản nháp của context mới nếu có. Đổi trạm cùng context không reset yêu cầu.

Giữ UI, nút xác nhận, công cụ và ngân sách API. Khi đổi sang môn/lớp chưa có bản nháp, ô yêu cầu sẽ trống thay vì mang nội dung của lớp trước. Quay lại sẽ khôi phục bản nháp đã lưu trong phiên. Bộ nhớ tăng theo số context đã ghé trong phiên, chỉ lưu các trường văn bản cấu hình; không ghi DB hoặc dữ liệu học sinh.

## Kiểm chứng

- AppTest trước sửa thất bại đúng điều kiện yêu cầu lớp12 còn ở lớp7: 1/1 thất bại trong17,249s, log PR6_PATCH16_CONTEXT_REPRO_20261029.log ngoài repo.
- Sau sửa: 6/6 kiểm thử liên quan qua18,087s, gồm luân chuyển65cặp môn/lớp, phục hồi bản nháp, giữ tùy chọn không liên quan và đổi lớp trên app local.
- Full suite254/254qua119,886s; log PR6_PATCH16_CONTEXT_FULL_20261029.log ngoài repo. Không chạy lại khi mã chưa đổi.

Chưa xác minh chuyển context trên Cloud sau bản vá này. Kiểm thử65cặp ở đây chứng minh cách ly trạng thái văn bản, không chứng nhận chương trình/KNTT hoặc kiến thức của65ngữ cảnh. Không đoán lỗi mở đề8300 đã hết từ bản vá trạng thái này.

