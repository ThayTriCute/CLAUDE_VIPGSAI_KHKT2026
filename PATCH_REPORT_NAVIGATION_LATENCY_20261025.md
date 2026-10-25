# Bản vá độ trễ và chạy lại giao diện — 25/10/2026

## Nguyên nhân đã kiểm chứng

- Nút chuyển trạm phía trên đổi session_state rồi gọi st.rerun trong thân trang. AppTest đo được hai lần thực thi module cho một lần bấm. Đây là chạy lại hữu hạn, không phải vòng lặp vô tận.
- Trạm 1 gọi bộ lọc sau generate_checked_text, dù hàm này đã trả về nội dung qua chính bộ lọc đó; rồi tiếp tục lọc toàn bài và phần lý thuyết khi dựng trang. Trước vá, một lượt sinh thành công thường đi qua bốn lời gọi bộ lọc ở đường này, chưa tính kiểm tra công thức trong xuất/hiển thị. Đây là bốn lời gọi tại các vị trí mã, không đồng nghĩa bốn lần gọi AI hoặc bốn lượt quét thực: bộ lọc đã có st.cache_data tối đa 256 kết quả từ trước. Cache hit không chạy lại thân hàm; việc đếm lời gọi đơn thuần không chứng minh đây là nguyên nhân chính gây lag.
- Streamlit chạy lại trang khi thay đổi widget; nhập tên bài và bấm soạn có thể phát sinh hai sự kiện riêng. Xuất HTML cũng dựng lại cùng nội dung.
- Widget bị Streamlit dọn khi rời trạm; khi quay lại, giá trị trống có thể ghi đè đáp án đã lưu.
- Đường AI còn ngân sách chờ tổng 180/240 giây tùy hàm; một lần sửa cú pháp có thể gọi thêm AI. Đây là nguồn chờ độc lập với bộ lọc. Không đổi ngân sách hoặc giảm kiểm tra học thuật trong bản vá này.

## Cách vá

1. Dùng callback cho nút chuyển trạm, cập nhật trạm và radio trước lượt dựng trang, bỏ rerun bổ sung.
2. Bỏ lần lọc ngay sau generate_checked_text; hàm này đã lọc và chỉ sửa AI tối đa một lần khi lỗi công thức.
3. Bộ lọc Trạm 1 đã dùng st.cache_data từ trước; giảm giới hạn 256 xuống bốn kết quả để hạn chế giữ nhiều bài trong RAM, giữ một lớp cache duy nhất. Khóa chứa đầy đủ văn bản, môn, lớp và chủ đề; nội dung/ngữ cảnh đổi phải kiểm tra lại. Lỗi không trở thành kết quả được duyệt. Cache chỉ ghi nhận kiểm tra kỹ thuật hiện có, không chứng nhận khoa học hay chuẩn Bộ.
4. Cache HTML bất biến tối đa bốn bản, khóa đủ nội dung/môn/lớp/chủ đề/kiểu in.
5. Gom tên bài và nút soạn vào form; chọn gợi ý điền đúng trường theo ngữ cảnh.
6. Khôi phục lựa chọn T1 và đáp án T3 từ trạng thái độc lập với vòng đời widget. Xóa lựa chọn cũ khi sinh bài mới hoặc đổi môn/lớp.
7. Cách ly metadata form do kiểm thử import app ở bare mode để không làm bẩn các phiên AppTest. Đây là lỗi môi trường kiểm thử; không bỏ kiểm tra để làm xanh.

## Số đo và giới hạn

- Đếm thực thi module: 2 xuống 1 trên 12 lần chuyển trạm được đo.
- AppTest không gắn profiler, phép đo xen kẽ: trung vị 1791,505 ms trước và 1769,435 ms sau callback, giảm khoảng 1,2%. Đây là phép đo máy cục bộ, chưa phải độ trễ trình duyệt/Cloud và chưa bao gồm lợi ích cache bộ lọc bổ sung sau phép đo. Không tuyên bố nhanh gấp đôi.
- Xuất HTML lặp lại 40 lần: khoảng 9,745 ms/lần trước, 0,011 ms/lần khi cache ấm. Đây là vi đo của hàm, không phải toàn bộ thao tác người dùng.
- Bản vá chưa phải kiểm thử tải đồng thời hoặc cam kết p95; không chứng minh mọi màn hình hết lag. Không có cơ sở gọi đây là chứng nhận công nghệ Big Tech.
- Các while đã đọc có bước tiến/điều kiện dừng: đệm đủ số phần tử, đọc tới EOF, giảm bộ nhớ đệm, tìm từ khóa tăng vị trí và thoát khi hết kết quả. Chưa phát hiện vòng vô tận ở các đoạn này; đây không phải chứng minh toàn bộ chương trình luôn kết thúc với mọi đầu vào.

## Kiểm chứng

Bộ kiểm tra tĩnh/dữ liệu 49 tệp Python và 159 kiểm thử đạt (138,185 giây) trên mã cuối cùng. Kiểm thử riêng bộ nhớ đệm cũng đạt sau khi kiểm tra thay đổi môn/lớp/chủ đề/nội dung. Các kiểm thử bao gồm chuyển trạm giữ đáp án/deadline, gợi ý bài không gọi AI, xuất không lẫn lớp/kiểu in, và bộ lọc chỉ dùng lại đúng văn bản cùng môn/lớp/chủ đề. Các chức năng còn phụ thuộc Cloud, mạng và nhà cung cấp AI cần đo riêng trước khi kết luận nguyên nhân toàn bộ độ trễ.


## Sự cố Cloud được ghi nhận riêng

Log sau lần khởi động lại ghi KeyError khi import services.academic_context/context_recovery. Trong cấu trúc hiện tại, services là gói có __init__.py; chưa có bằng chứng đây là thiếu file. Cần điều tra cơ chế reload/import đồng thời; bản vá độ trễ này chưa được coi là đã sửa lỗi import. Một phiên kiểm thử Cloud có giao diện bình thường trở lại nhưng không thu được bài AI, nên chưa xác nhận luồng AI Cloud hoạt động đầy đủ.
