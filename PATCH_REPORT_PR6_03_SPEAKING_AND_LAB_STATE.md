# PR6 — bản vá 03: Speaking theo lớp và trạng thái Lab

Nền `352b9b1`, ngày 27/10/2026. Chưa triển khai lên nhánh chạy Cloud.

## Nguyên nhân và cách vá

1. Speaking dùng chung các bài mang tên Unit lớp 12 ở lớp dưới. Chọn riêng phần PR22 (`bdc6bb3`) để có ví dụ biên soạn theo lớp 6–11, giữ bốn ví dụ lớp 12 và ghi rõ nguồn biên soạn. Không giả chúng là trích SGK hoặc mục lục KNTT đã kiểm định.
2. Khóa widget ghi âm/nhập bài/chủ đề gắn thêm lớp để tránh dùng lẫn trạng thái. Giữ ghi âm, nhập văn bản, từ vựng, đoạn đọc, bốn nhóm góp ý và mẫu diễn đạt tham khảo. Chỉnh lời hứa Band 8.0 thành góp ý phù hợp lớp; chỉ có văn bản thì không giả vờ đã nghe hoặc chấm phát âm. Nhãn nút/tiêu đề đổi cho đúng nghĩa; không thay bố cục.
3. Thư viện Lab có các mẫu mở rộng khác lớp đang chọn. Ghi rõ đây là ví dụ độc lập, không tự lấy dữ kiện của bài học; hiển thị nhãn mở rộng nếu ghi chú lớp của mẫu khác lớp hiện tại. Nhãn lớp lấy từ cấu hình cũ, không phải bản đồ chương trình đã xác minh.
4. Đã tái hiện lỗi trạng thái: học sinh chỉnh a=2, sau đó nạp nguồn mới a=3 nhưng điều khiển vẫn giữ a=2, không báo exception. Bản vá dùng namespace cho 43 khóa điều khiển theo nguồn mô hình/ngữ cảnh/lượt yêu cầu. Cùng nguồn vẫn giữ thao tác khám phá; nạp nguồn mới hoặc mở lại mẫu thì điều khiển được khởi tạo theo nguồn. Kiểm thử UI sau vá đã nhận đúng a=3.

## Giữ gì, thay gì

Giữ nguyên 12 nhánh định nghĩa `available_labs`, dữ liệu và công cụ vẽ. Có kiểm thử hash AST chống thay/làm mất cấu hình mẫu ngoài ý muốn. Không xây renderer mới. Đổi nhãn trình bày Lab, thêm giải thích nguồn và đổi khóa trạng thái; không sửa CSS/font hay cắt công cụ.

Các mẫu vẫn cần thẩm định khoa học riêng. Ví dụ Tin học có tên “Sơ đồ thuật toán & Cây nhị phân” nhưng payload là `oxyz`, renderer tương ứng vẽ điểm/vectơ OM. Việc ghi nhãn minh họa không sửa được sai khác này và không được coi là Lab đã đúng hết. Bản này không âm thầm đổi payload để che cảnh báo.

## Kiểm chứng

- 176/176 kiểm thử toàn dự án đạt: `PR6_PATCH03_FINAL_TESTS_20261027.log`.
- Ca lỗi hệ số gốc: `PR6_PATCH03_LAB_RESELECTION_20261027.json` ghi a mới yêu cầu 3 nhưng sau render còn 2. Ca hồi quy UI sau vá trong `test_lab_state.py` đã đạt, đúng a=3. Hash phạm vi ổn định khi chỉ đổi thứ tự khóa dữ liệu, đổi khi nguồn/ngữ cảnh/lượt yêu cầu đổi.
- Kiểm Speaking UI đủ bảy lớp, giữ ghi âm và nhập văn bản; ca góp ý văn bản không tự nhận đã nghe âm thanh.
- Ma trận 65 cặp T1/T3 đã chạy hết: lượt đầu 63/65 đạt, Tin9/Công nghệ9 timeout với khoảng đo hàng nghìn giây. Hai ca này đã chạy lại bằng tiến trình mới, cùng mã nguồn và đều đạt (45.119s/31.969s cho toàn ca khởi động + nhiều thao tác, không phải độ trễ một click). Kết quả cuối đủ 65 ngữ cảnh đạt ca QA; giữ riêng hai lỗi đầu, chưa kết luận nguyên nhân và không gọi chúng là đã được vá. JSON tổng hợp lưu cả first_attempt và final.
- Ma trận bản03 kiểm cấu hình hai trạm, mở mẫu Lab mặc định, phạm vi Speaking/ghi âm/nhập bài. Không sinh lại bài/đề vì đường sinh không đổi từ bản02 đã nghiệm thu 65 cặp. Không gọi AI thật trong ma trận.

## Chi phí và giới hạn

Không thêm lượt AI cho kiểm phạm vi hay chuyển nguồn Lab. Hash dữ liệu là phép tính local, không lưu thêm lịch sử mô hình không giới hạn. Góp ý Speaking vẫn là thao tác người dùng bấm; không tự gọi khi đổi lớp/mở trang.

Chưa chứng nhận SGK, chương trình hoặc mọi mô hình Lab. Chưa nghe kiểm thực tế toàn bộ giọng đọc và chưa chứng minh hết lag. Cần profile riêng đường mở Trạm 3 và chạy CI đúng phiên bản trước quyết định triển khai Cloud.
