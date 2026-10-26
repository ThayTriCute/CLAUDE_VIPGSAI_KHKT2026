# Sửa bắt nhầm gợi mở Socratic — 27/10/2026

## Nguyên nhân tái hiện
Ảnh người dùng cho thấy T1 bị giữ sau hai phản hồi, lỗi “Gợi mở không được tính toán ra số thay học sinh”. Chưa có bản nháp gốc của đúng phiên trong ảnh để xác định bước/câu cụ thể. Đã thực thi chính hàm ở commit HEAD trước sửa: cả y=2x+b, y=2.5x+b và y=2 x+b trong câu hỏi gợi mở đều bị hiểu thành kết quả số y=2 hoặc y=2.5. Đây là lỗi ranh giới token của regex, không phải công thức sai.

Điều kiện từ khóa còn chặn cụm nhắc chung “các đáp án” và từ solution/therefore được trích từ chính câu tiếng Anh. Từ xuất hiện không tự chứng minh lời giải bị tiết lộ.

## Sửa hẹp
Regex nhận trọn giá trị số, không nhận tiền tố hệ số của biểu thức có biến. Nhận cả phân số số học để vẫn giữ chặn nghiệm mới x=7/2. Nhận diện tuyên bố “đáp án là/B/:” thay cho chặn mọi lần nhắc “đáp án”. Từ solution/therefore được nhắc làm ngữ cảnh nếu đã có trong câu nguồn; các kiểm chữ cái phương án, giá trị số mới và phương án đúng vẫn hoạt động.

Giữ nguyên phân tách: Phần 1 được có ví dụ/lời giải và kết quả; kiểm Socratic áp vào gợi mở MCQ và Pólya. Không thêm yêu cầu ví dụ số, không bật lại PR29, không đổi nội dung nguồn, bố cục hoặc lượt sửa.

## Kiểm chứng và giới hạn
39 kiểm thử tập trung qua trong 2,865 giây: nhận biểu thức tương đương, nhắc phương án chung, ngữ cảnh Anh; chặn tuyên bố đáp án, chữ cái, nghiệm mới nguyên/thập phân/phân số và nhắc phương án đúng. Kiểm phần lý thuyết có số được giữ ở đủ 65 tổ hợp môn/lớp là kiểm hợp đồng kỹ thuật, không thẩm định khoa học các môn. Đối chứng thực thi hàm cũ tái hiện cả ba ca hệ số bị chặn. Không gọi AI trong các kiểm này.

Chưa thể khẳng định đúng bản nháp trong ảnh chỉ có lỗi này. Các cách diễn đạt khác vẫn cần đối chứng; regex không chứng minh ngữ nghĩa mọi gợi mở. Bản sửa phải qua CI, kiểm Cloud trước khi nghiệm thu. Chưa triển khai; lỗi kết nối tab Chrome/Cloud được theo dõi riêng, không quy cho điều kiện kiểm nội dung.
