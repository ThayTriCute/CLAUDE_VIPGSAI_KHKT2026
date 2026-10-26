# Kiểm tra đường xuất bản Trạm 1 và Trạm 3 trên toàn bộ môn/lớp

Ngày 26/10/2026. Phạm vi: 65 tổ hợp đang được ứng dụng hỗ trợ, lớp 6–12. Đây là kiểm thử phần mềm và một số tình huống ký hiệu khoa học; không chứng nhận mọi ngữ liệu AI đúng CT2018/KNTT.

## Nguyên nhân và bản vá

1. **Trạm 1 không sửa lại một số lỗi chính sách.** Bộ kiểm trả `ValueError` cho sai môn/lớp hoặc dữ liệu địa lí hiện hành mâu thuẫn, nhưng hàm sinh chỉ bắt lỗi công thức/cấu trúc/phạm vi. Thêm `AcademicPolicyError`, đưa đúng nhóm lỗi bản nháp này vào **một** lượt sửa đã có. Không bắt mọi lỗi lập trình/nhà cung cấp để gọi AI lại; bản sửa vẫn phải qua cùng bộ kiểm.
2. **Dòng kết hợp môn và lớp có thể lọt kiểm tra lớp.** Ví dụ `Môn: Toán học; lớp: 12` khi đang chọn lớp 6. Kiểm tra cả trường lớp trên dòng khai báo môn, kể cả số lớp ngoài phạm vi. Không quét mọi số lớp trong một trích đoạn như khai báo môn/lớp.
3. **Trạm 1 nhầm phương án khác nhau vì đổi thành chữ thường.** `CO`/`Co`, `A`/`a`, chuỗi mã phân biệt hoa–thường phải giữ ý nghĩa. Kiểm tra trùng giữ nguyên hoa–thường và khoảng trắng nội dung; chỉ bỏ khoảng trắng đầu/cuối. Trạm 3 áp dụng cùng nguyên tắc khi so phương án sau khi bỏ nhãn A–D.
4. **Trạm 3 có thể bỏ qua phần sai kiểu.** `question_groups` chỉ duyệt danh sách; một phần dạng object có thể bị bỏ qua khi phần khác vẫn hợp lệ. Cổng cấu trúc nay yêu cầu đúng kiểu danh sách cho từng phần hiện diện; phương án phải là chuỗi có nội dung, không nhãn rỗng/trùng; mệnh đề Đ/S phải là chuỗi.
5. **Ngữ văn cần kiểm cả ngữ liệu bao ngoài.** Kiểm khai báo môn/lớp của khối đọc hiểu, không chỉ câu con. Chặn đoạn đọc toàn khoảng trắng hoặc danh sách câu hỏi sai kiểu/rỗng. Không tự thay riêng đoạn đọc rồi giữ các câu hỏi/rubric cũ.
6. **Khai báo bộ sách ở từng câu chưa được kiểm nhất quán.** Kiểm các trường bộ sách ở đề, khối đọc hiểu, câu hỏi và dòng khai báo đầu bài học. Một câu trắc nghiệm khai báo bộ khác đi vào cơ chế thay nguyên câu có giới hạn, rồi kiểm lại. Chỉ phát hiện khai báo mâu thuẫn; thiếu khai báo hoặc ghi KNTT không chứng minh đã đối chiếu trang sách. Nhắc tên sách khác trong văn xuôi để so sánh không tự bị cấm.
7. **Bài toán thực tế có thể thiếu giả thiết mô hình.** Bổ sung chỉ dẫn miền biến, đơn vị, rời rạc/liên tục và kiểm tra biên. Đây là cải thiện prompt, **chưa phải** bộ chứng minh ngữ nghĩa mọi bài toán thực tế.
8. **Điểm Tiếng Anh đang bị đổi thành chứng nhận năng lực không có cơ sở.** Mọi đề, kể cả lớp 6/tùy biến rất ngắn, từng được suy A2/B1/B2 từ ngưỡng 6/8 điểm và gắn "Bậc 6 Việt Nam". Giữ nguyên điểm, tỷ lệ chính xác và bố trí ba ô; thay kết luận bằng phạm vi bài luyện tập, chưa quy đổi CEFR. Nhãn điểm 0,25/câu cũng không còn áp cho đề tùy biến bất kể số câu. Tham chiếu phương pháp, không phải chứng nhận app: [Council of Europe — Relating examinations to CEFR](https://www.coe.int/en/web/common-european-framework-reference-languages/relating-examinations-to-the-cefr).

## Kiểm thử và giới hạn bằng chứng

- `tests/test_all_context_publication.py`: chạy toàn bộ 65 ngữ cảnh qua cổng bài học, Pólya, xuất HTML/infographic, bảo toàn nội dung/khóa chấm, ngữ cảnh đề thi và các tình huống sai cấu trúc. Kiểm lượt sửa không lặp vô hạn, không nuốt lỗi nhà cung cấp. Với 58 ngữ cảnh ngoài Ngữ văn, kiểm thay nguyên câu và ngân sách sửa; 7 ngữ cảnh Ngữ văn kiểm cấu trúc/ngữ liệu, **không nhận là đã có bộ phục hồi văn bản + câu hỏi + rubric tự động hoàn chỉnh**.
- Kiểm KaTeX/mhchem thật cho phân số, đơn vị, omega, hóa học; giữ IPA/mã Tin học. Kiểm thành công cú pháp không chứng minh đúng định luật hoặc đáp án.
- `scripts/verify_all_context_ui.py`: thao tác Streamlit AppTest tại máy, sinh bài học qua nút Trạm 1 bằng phản hồi giả lập; tạo đề Trạm 3 từ kho giả lập. Database riêng trong thư mục tạm; không dùng khóa thật, không gọi Gemini thật. Kết quả mỗi môn/lớp và lỗi/thử lại được ghi JSON ở đường dẫn người chạy cung cấp. Không phải kiểm tra 130 lượt sinh AI thật trên Cloud.
- Tái lập trước vá: các nhóm kiểm mới phát hiện lỗi sai môn không được sửa, sai kiểu phần bị bỏ qua, phương án rỗng/trùng và ngữ liệu đọc hiểu bị bỏ sót. Sau vá, nhóm kiểm tập trung qua; số lượng toàn bộ hồi quy/giao diện cập nhật trong phần kết quả bên dưới.

## Kết quả nghiệm thu kỹ thuật

- Hồi quy toàn bộ: **269 ca qua**, 650,858 giây tại máy. Ca giao diện bổ sung chấm Tiếng Anh lớp 6 sau chỉnh nhãn: **1 ca qua**, 85,488 giây. Các kiểm chức năng tập trung cuối trước đó: **68 ca qua**.
- Ma trận giao diện hoàn tất: **65/65 Trạm 1 + 65/65 Trạm 3**, không còn ca lỗi trong kết quả cuối. Kết quả chi tiết: [publication_ui_matrix_20261026.json](tests/evidence/publication_ui_matrix_20261026.json). Có lần AppTest quá hạn 60 giây trong lần quét đầu; nhật ký giữ lỗi/thử lại, không gọi đây là lỗi nội dung đã được sửa hoặc bằng chứng Cloud bị treo. Chỉ tính các ca sau khi thao tác hoàn tất. Đây là dữ liệu mô phỏng và không có lượt gọi Gemini thật trong ma trận.

## Tối ưu và phạm vi giữ nguyên

Các kiểm tra thêm là thao tác chuỗi/cấu trúc tại máy, không tự thêm một lượt gọi AI khi bản nháp đã hợp lệ. Trạm 1 vẫn tối đa một lượt sửa; ngân sách thay câu Trạm 3 hiện có không tăng. Giữ bố trí giao diện, số bài/câu, radio, infographic, video, giọng đọc và điều hướng; riêng nhãn kết quả Tiếng Anh được sửa để tránh kết luận năng lực không có chứng cứ.

Không có chứng nhận "BigTech". Có bằng chứng tái lập lỗi, kiểm thử âm/dương, bảo toàn dữ liệu, ngân sách hữu hạn và nhật ký theo từng ngữ cảnh. Vẫn thiếu kho yêu cầu cần đạt/trang và phiên bản KNTT đã đối chiếu đầy đủ cho cả 65 ngữ cảnh, bộ kiểm độc lập mọi kiến thức, kiểm chứng mức độ nhận thức chuyên môn, và đo hiệu năng tải đồng thời. Không nâng trạng thái `academic_verified` hoặc đổi ngày rà soát pháp quy chỉ vì các test xanh.
