# Trạm 1 — mẫu sổ tay theo ảnh tham khảo, 24/10/2026

## Nguyên nhân và thay đổi

Bản xuất HTML cũ đã bảo toàn học liệu và có phông chữ/KaTeX ngoại tuyến, nhưng dùng viền chấm làm gáy, đầu trang chỉ một tiêu đề và thiếu phân cấp giống mẫu sổ tay. Đây là khoảng cách về trình bày, không phải lý do để sinh lại kiến thức bằng ảnh AI.

Sửa trong `services/lesson_export.py`: nền giấy kem với ô ly mảnh và sắc giấy nhẹ; gáy đen kèm lỗ đóng; đầu trang hai khối; thân chữ viết tay xanh; đề mục đỏ gạch chân; số thứ tự đỏ; bảng, ghi chú và dấu kết thúc cùng phong cách. Phông Caveat và KaTeX tiếp tục được nhúng trong HTML. Công thức dùng phông toán để giữ cấu trúc phân số, căn, chỉ số, véc-tơ và kí hiệu hóa học, không chuyển thành chữ viết tay giả bằng ảnh.

Mẫu ảnh đề thi 2002 chỉ cung cấp phong cách. Đầu trang lấy chủ đề, môn và lớp hiện tại; không chép tên cơ quan, năm thi, thời gian hay câu hỏi từ ảnh. Không đổi phần trích xuất nguồn bài, hàm bảo toàn công thức hoặc nội dung bài học. Tất cả môn/lớp hợp lệ dùng chung trình bày này. Prompt tải xuống cũng mô tả rõ phạm vi tham khảo phong cách.

CSS đáp ứng: đầu trang một cột trên điện thoại, hai cột khi in; A4 lề 10 mm, điều chỉnh màu in, giữ bảng/đề mục hợp lý và cho phép nội dung chạy nhiều trang. Trong Trạm 1 bổ sung hướng dẫn tải HTML, mở bằng trình duyệt, In/Lưu PDF và bật đồ họa nền khi cần. Hai chế độ màu và trắng đen vẫn dùng đầu trang thông thường.

## Kiểm tra thực hiện trước push

- 20/20 kiểm thử đạt: bộ `tests.test_academic_exports` và AppTest `test_generated_lesson_export_is_bound_to_subject_and_grade`, 70,825 giây. Kiểm tra bảo toàn nguồn/công thức, nhúng phông, ngữ cảnh môn/lớp và nội dung dài; thời gian này không phải benchmark tốc độ app.
- Xem trực tiếp trên Chrome: Toán 6 phân số; Hóa 10 phương trình `2H2 + O2 -> 2H2O`; Vật lý 12 với `omega`, `Omega`, `Delta`, véc-tơ, căn và phân thức. Trạng thái `renderErrors=0` ở cả ba mẫu.
- 390×844: mẫu Toán không tràn ngang, đầu trang chuyển một cột. Đã trả viewport về mặc định.
- Mẫu dài 25 đề mục giữ đến đề mục 25, không cắt thành một ảnh/trang cố định. Bản màu ẩn đầu trang sổ tay; bản trắng đen có nền trắng và chữ đen; không lỗi KaTeX trong các mẫu này.
- Chưa xác nhận tệp PDF cuối từ hộp thoại in Chrome trong phiên QA này. Không coi kiểm tra HTML dài là bằng chứng đã kiểm tra ngắt mọi trang PDF. Tệp xuất vẫn là HTML có nút In/Lưu PDF, không phải chức năng tải PDF trực tiếp từ máy chủ.

Ảnh xem thử và HTML minh họa được giữ ngoài Git ở `F:\FINAL KHKT 2026\qa_evidence\` và `F:\FINAL KHKT 2026\MAU_INFOGRAPHIC_SO_TAY_TRAM1.html`. Các ví dụ là dữ liệu QA, không đưa vào bài học thực.

## Tối ưu và giới hạn

Trang sổ tay dùng CSS và phông đã có, không thêm ảnh nền lớn, lượt gọi AI hay phụ thuộc mạng. Giao diện phản ánh phong cách mẫu, không phải bản sao ảnh chụp hay nét chữ của một người cụ thể. Dài ngắn phụ thuộc nội dung nguồn; công thức rất rộng vẫn có thể cần đối chiếu khi in. Chất lượng học thuật phụ thuộc bài nguồn và giáo viên duyệt; thay đổi phong cách không chứng minh nội dung chuẩn 100%.

Không có đo tải, p95, nhiều phiên hoặc kiểm định mọi máy in/trình duyệt trong bản vá này; không có căn cứ gọi là đạt quy mô Big Tech. Lợi ích kiểm chứng được là trình bày xác định, bảo toàn nguồn, phông ngoại tuyến và không tốn thêm lượt AI. Có thể hoàn tác bằng `git revert` commit bản vá, không sửa lại kho học liệu.
