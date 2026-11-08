# Phát hành bản vá local khối 10 — 08/11/2026

Chủ dự án yêu cầu phát hành các bản vá đã kiểm của đợt khối 10. Đây là phát hành mã và hồ sơ nguồn, không phải xác nhận đã nghiệm thu toàn bộ chương trình hoặc mọi môn/lớp.

## Thay đổi

- Dùng chung quy tắc xuống dòng các bước, giữ công thức và sửa nội dung theo hồ sơ đúng môn/lớp/bài trong hiển thị, câu hỏi và bản xuất.
- Cải thiện kết bài Socratic khi học sinh đã hiểu và không còn hỏi; bài học nhân sinh theo ngữ cảnh có nguồn và chú thích diễn nghĩa, với lịch sử luân phiên lưu trên máy chủ.
- Thêm các hoạt động Lab local theo dữ kiện và nguồn: ném ngang, tốc độ phản ứng, thẩm thấu, ngưỡng điều khiển, đối chiếu tư liệu và công cụ đổi giờ/ngày UTC. Giữ các tính năng hiện có.
- Bổ sung hồ sơ nguồn và sửa bài mẫu Vật lý, Hóa học, Sinh học, Lịch sử, Địa lý, GDKT&PL 10; bảo toàn các mục chủ dự án đã duyệt.
- Đọc gói nguồn XZ đã đối chiếu trước khi sinh bài nếu máy chủ có kho phù hợp. Request giữ căn cứ nguồn và kiến thức, bỏ dữ liệu sửa bản nháp/đáp án chỉ dùng local để giảm ngữ cảnh thừa.

## Phần còn mở

- Công nghệ 10: kiểm giao diện bài Thiết kế sau bản vá và phân trang in nhánh Trồng trọt. Không đưa hunk sửa chưa kiểm của luồng này vào đợt phát hành.
- Địa lý 10/GDKT&PL 10: phân trang in chưa có xác nhận chủ dự án; nguồn NXBGD và VniTeach đã đọc đúng bài, danh mục THSQG đã kiểm nhưng chưa thấy liên kết đúng hai cuốn. Không coi là đã đọc đủ ba bản sách.
- Các bài mẫu không thay cho nghiệm thu toàn bộ SGK/YCCĐ. Bộ lọc CT2018/KNTT/KNTT thống nhất/pháp quy hoàn chỉnh và phủ lớp11–12 vẫn là công việc tiếp theo.
- Kho sách lớn, kho đề, DB, dữ liệu học sinh, khóa và cache local không nằm trong đợt push này. Cloud không tự truy cập ổ F; thiếu kho XZ phải báo thiếu thay vì giả vờ có căn cứ. Triển khai dữ liệu cho cả ba trạm cần đợt riêng.
- Không thay provider/nguồn/cache giọng nữ; không tuyên bố dịch vụ giọng nam đã hoàn tất.

## Kiểm chứng

Hai bài Địa lý/GDKT&PL đã kiểm quiz3/3, hoạt động đối chiếu, lượt gia sư có nguồn và ba kiểu HTML thực tải từ ứng dụng. Lab UTC kiểm đổi ngày/năm, độ lệch lẻ phút và dữ kiện biên; không suy giờ pháp định/DST từ tên thành phố. Test cấu trúc không phải chứng nhận kiến thức toàn chương trình. Bằng chứng chi tiết và nhật ký gốc lưu tại ổ F của chủ dự án, không đưa dữ liệu phiên làm việc hoặc bí mật lên GitHub.
