# Giải trình bản vá: ngữ cảnh môn/lớp, nguồn học liệu và bản xuất bài học

Ngày kiểm tra: 24/10/2026. Thư mục sửa mã: `F:\FINAL KHKT 2026\VIP_DEMO_GSAITHPT2026-main\VIP_DEMO_GSAITHPT2026-main`.

## Kết quả và phạm vi

Bản vá ngăn các đường trộn sai ngữ cảnh đã tái hiện được, bỏ nội dung mẫu chèn thêm vào infographic, xuất phiếu chữ viết tay từ chính nội dung bài học và sửa các liên kết hỏng đã phát hiện. Đây không phải chứng nhận mọi câu AI sinh đều đúng kiến thức hoặc đúng từng trang SGK. Bộ lọc cú pháp không thể thay thế giáo viên duyệt học thuật.

## Nguyên nhân kỹ thuật và cách sửa

| Vấn đề | Nguyên nhân trước vá | Cách vá | Kiểm chứng |
|---|---|---|---|
| Nhận dạng môn không thống nhất | Nhiều bảng bí danh riêng; GDCD bị gộp vào GDKT&PL | Tập trung tên môn/lớp tại `services/academic_context.py`; giữ GDCD THCS và GDKT&PL THPT là hai môn riêng | Bí danh có/không dấu, Unicode NFD, 65 tổ hợp môn/lớp, từ chối cặp sai cấp học |
| Xuất bài cũ dưới môn/lớp mới | Nội dung phiên thiếu thông tin nguồn ngữ cảnh | Gắn môn/lớp ngay lúc sinh; cô lập bài cũ chưa khớp trước khi cho xuất | AppTest sinh bài lớp 6, đổi lớp 7; bài phiên cũ bị chặn |
| Infographic sai nội dung bài | Bộ chưng cất tự bù các ô thiếu bằng ví dụ/công thức mẫu, gồm giải tích lớp 12 | Bỏ phần bù; bản HTML lấy toàn bộ phần bài học đã qua bộ lọc; SVG cũ chỉ trích câu từ nguồn | Bài Phân số lớp 6 không tự thêm đạo hàm/Bayes; mã SHA-256 gắn với nội dung xuất |
| Công thức Vật lý bị đổi nghĩa | Regex sửa OCR biến omega thành vô cực, áp dụng chung đa môn | Bỏ quy tắc này; bảo vệ đoạn mã trước chuẩn hóa | Giữ `omega`, `Omega`, mã nguồn; kiểm tra thực tế công thức dao động |
| Công thức bản xuất bị xấp xỉ hoặc phụ thuộc CDN | SVG cũ diễn dịch một số TeX bằng regex | Đóng gói KaTeX 0.19.0 + mhchem và phông; tách công thức trước Markdown; lỗi cú pháp hiện rõ và vô hiệu nút in | Trình duyệt dựng phân số, omega, phương trình este, đơn vị; lệnh sai bị chặn, giữ chuỗi lỗi để sửa |
| Mã SGK/video được trình bày như đã xác minh | Suy số chương/bài/tập từ từ khóa, mặc định chương 1; URL tìm kiếm mang nhãn video thẩm định | Mã nội bộ GSAI; không suy chương/trang; ghi rõ link tra cứu và kết quả tìm kiếm | Test không bịa Chương 1, thoát HTML ở tên chủ đề |
| Liên kết không truy cập | Cổng tập huấn cũ lỗi TLS, trang Sinh học 10 trả 404 | Chuyển tới cổng NXBGD đang hoạt động, nhãn “Tra cứu” thay vì giả là trang sách cụ thể | 101 URL duy nhất / 120 mục, GET trả HTTP 200 trong lần kiểm tra; không tắt TLS |
| Đề trộn lệch chủ đề | Không đủ câu khớp thì bù câu từ cả kho; nhánh Ngữ văn bỏ qua chủ đề | Không bù ngoài bộ lọc chủ đề; kiểm tra metadata chủ đề; nhánh Văn cũng lọc trước chọn đề | Test thiếu câu Phân số không lấy Hình học; chọn nghị luận không lấy đề thơ |
| Đề bị đổi nhãn sau sinh | Chuẩn hóa ghi đè môn/lớp trước phát hiện mâu thuẫn | Kiểm tra metadata đề và từng câu trước chuẩn hóa; sao chép dữ liệu trước làm giàu | Test từ chối đề/câu khai báo môn hoặc lớp khác |
| Header đề xuất sai | Word cố định 90 phút, thiếu lớp; tên môn chưa thống nhất | Lấy đúng môn/lớp/thời lượng từ đề, áp dụng TXT và DOCX | Test Địa lí lớp 11, 25 phút; không xuất 90 phút |
| Rủi ro tăng RAM khi thiếu shard | Rơi về kho master rất lớn | Trả kho trống có cảnh báo thay vì nạp master hoặc mượn môn khác | Test kho GDCD thực; GDKT&PL 12 không nhận nhầm dữ liệu |

## Kiểu chữ viết tay

Đọc tài liệu tham chiếu `C:\Users\pmtgi\Downloads\PROMPT DE VIET TAY.docx` như mẫu phong cách. Chỉ lấy giấy kem ô ly, chữ xanh, tiêu đề đỏ, chữ Việt có dấu và gáy trái. Không lấy môn/lớp/nội dung hay danh tính trong mẫu làm dữ liệu bài học.

Bản HTML là phiếu bài học có bố cục chữ viết tay, không phải ảnh do AI vẽ. Nội dung dài được giữ trong luồng nhiều trang; phông chữ viết tay cho văn bản, bộ chữ toán chuyên dụng cho công thức. Có thêm bản màu, trắng đen, tải Markdown và prompt JSON chứa đúng nội dung. Nếu dùng prompt đó với mô hình tạo ảnh, ảnh vẫn cần đối chiếu; không được coi ảnh tạo sinh là bản công thức có thẩm quyền.

## Bằng chứng và số đo

- Kiểm tra tĩnh toàn bộ 38 tệp Python; kiểm tra dữ liệu/tài sản và suite hiện có đã qua 84 tests trước bổ sung kiểm thử nhánh Văn. Kiểm thử chuyên biệt sau bổ sung: 19/19 đạt. Lần chạy phát hành cuối được ghi ở phần cuối báo cáo.
- AppTest dùng phản hồi AI giả lập để kiểm tra luồng và tránh phụ thuộc chi phí/mạng. Không coi đây là đánh giá chất lượng học thuật của Gemini thật.
- Trình duyệt Chrome: Toán 6 có 4 biểu thức, Vật lý 11 có 3, Hóa học 12 có 2; không có lỗi dựng công thức trong các mẫu đó. Mẫu lệnh không hợp lệ khóa nút In / Lưu PDF.
- Bằng chứng ảnh: `F:\FINAL KHKT 2026\qa_evidence\lesson_math6_handwritten.png`.
- Bản HTML mẫu: 1.223.801–1.224.127 byte trước bổ sung giữ nguyên công thức lỗi. Thời gian dựng ba mẫu trên máy này: 17,57 / 7,80 / 6,72 ms. Không phải benchmark Cloud hay kiểm thử tải.
- Tài sản render chỉ đọc và base64 một lần với LRU 1 phần tử; hỗ trợ ngoại tuyến. Đổi lại mỗi file/preview khoảng 1,22 MB; chưa đo heap trình duyệt và băng thông nhiều người dùng. Không nên kết luận đã tối ưu tuyệt đối.
- Quét tuần tự các shard hiện có: 62/65 cặp môn/lớp có bản ghi; thiếu GDKT&PL lớp 10, 11, 12. Dữ liệu có nhãn môn/lớp không chứng minh nguồn gốc hoặc mọi câu đúng kiến thức. Không tự tạo đề gắn nhãn đề thật để lấp khoảng trống.
- Kết quả HTTP chỉ phản ánh lúc kiểm tra; chưa đối chiếu nội dung từng trang SGK, quyền truy cập sâu hoặc video cụ thể.
- Đã kiểm tra hiển thị HTML; chưa kiểm tra trực quan mọi trang PDF in ra trên mọi trình duyệt/máy in. DOCX đề thi đã kiểm tra metadata; chưa chuyển toàn bộ TeX thành công thức Word OMML.

## Đánh giá mức độ kỹ thuật

Chưa đủ căn cứ gọi toàn hệ thống đạt mức vận hành Big Tech. Những cải thiện cụ thể là một nguồn danh tính môn/lớp, từ chối dữ liệu lệch, xuất có thể truy vết nội dung, thư viện render đóng gói có giấy phép, kiểm thử hồi quy và quy trình sửa cục bộ rồi kiểm tra trước push.

Các khoảng trống cần hoàn thành tiếp theo:

1. Chuẩn học thuật: bộ dữ liệu chuẩn được giáo viên duyệt theo môn/lớp/chủ đề và phiên bản chương trình; đo tỷ lệ sai/thiếu công thức, sai kiến thức, dẫn nguồn sai. Cổng tra cứu chưa phải trích dẫn bài/trang.
2. Dữ liệu đề: bổ sung GDKT&PL 10–12 có nguồn hợp lệ; kiểm định nguồn gốc bản ghi, nhãn chủ đề và đáp án. Không thay bằng GDCD.
3. Độ tin cậy AI: kiểm tra nội dung thực tế với bộ bài chuẩn đa môn; kiểm tra ý nghĩa công thức, không chỉ cú pháp; chặn xuất chính thức khi chưa đạt tiêu chí học thuật được định nghĩa.
4. Hiệu năng/vận hành: đặt mục tiêu đo được cho độ trễ p95, bộ nhớ, số phiên đồng thời, tỷ lệ lỗi, phục hồi sau timeout; đo trên môi trường triển khai. Chưa có bằng chứng app không còn giật hoặc văng.
5. Quan sát và phục hồi: theo dõi lỗi theo phiên/bản phát hành nhưng không ghi khóa API/thông tin học sinh; cảnh báo, sao lưu/khôi phục, quy trình rollback; kiểm thử đồng thời dữ liệu ghi.
6. Tương thích: thay dần API Streamlit đã cảnh báo ngừng dùng, kiểm tra điện thoại, PDF nhiều trang, Word công thức và khả năng truy cập. Bản vá này chưa xử lý hết cảnh báo cũ của toàn app.

## Tài liệu kỹ thuật tham chiếu

- KaTeX: https://katex.org/docs/supported
- mhchem: https://github.com/KaTeX/KaTeX/blob/main/contrib/mhchem/README.md
- Phông Caveat và giấy phép OFL: các tệp giấy phép/provenance trong `assets/fonts` và `assets/vendor/katex`.
- Cổng NXBGD: https://truonghocsoquocgia.nxbgd.vn/
- Chương trình tổng thể GDPT 2018: https://moet.gov.vn/content/tintuc/Lists/News/Attachments/8421/chuong-trinh-tong-the-ctgdpt-2018.pdf

## Mẫu giải trình bắt buộc cho các bản vá sau

Mỗi bản vá cần ghi: hiện tượng và bước tái hiện; nguyên nhân kỹ thuật; thay đổi mã; kiểm thử cùng kết quả thực tế; số đo hiệu năng và điều kiện đo nếu có; đánh đổi; giới hạn chưa xử lý; phương án quay lại bản trước; commit/PR và trạng thái triển khai. Không dùng số test đạt để suy ra “đúng học thuật 100%” hoặc “không còn lỗi”.

## Xác nhận trước push

- Lần chạy phát hành: `python -u deep_check_var_project.py`, 85/85 tests đạt trong 76,833 giây; 38 tệp Python qua kiểm tra tĩnh/dữ liệu. `git -c core.whitespace=cr-at-eol diff --check` đạt.
- Kiểm tra trình duyệt bổ sung sau sửa nhánh lỗi KaTeX: giữ nguyên `\\notARealCommand{x}`, báo 1 lỗi, nút in bị vô hiệu.
- Hoàn tác: nếu triển khai phát sinh lỗi, tạo commit `git revert` cho commit bản vá và push bình thường; không force-push hoặc xóa lịch sử. Bản nền trước vá là `7aae150ef1bcb1a17695297756c9e9ba023bd5aa`.
