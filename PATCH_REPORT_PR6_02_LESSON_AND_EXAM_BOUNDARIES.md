# PR6 — bản vá 02: công thức, Socratic và bài làm khi chuyển trạm

Ngày 27/10/2026. Nền: PR6 cùng bản vá trạng thái chọn đề `42ed73c`. Chưa nhập các thay đổi giao diện đời sau PR6.

## Nguyên nhân và thay đổi

| Vấn đề | Cách vá | Phạm vi được giữ |
|---|---|---|
| Bộ chuẩn hóa gộp `$x$ $y$` thành `$xy$`, đổi công thức khối thành nội dòng | Bảo vệ riêng công thức và đoạn mã trước khi chuẩn hóa văn bản. Chỉ đổi dấu bọc `\(...\)` / `\[...\]` sang dấu dollar tương ứng cho web, giữ thân công thức | Dùng lại bộ nhận diện token đang có của bộ xuất bài học; không thay bộ vẽ hoặc CSS |
| Trắc nghiệm Trạm 1 dùng `EXPLAIN` dưới nhãn Socratic; Trạm 3 cũng đưa explain/ans vào hàm gợi ý | Tách trường `HINT`/`hint` khỏi Explain và đáp án ở cả hai trạm. Giữ giải thích/chấm bài ở luồng xem kết quả | Giữ radio và phần xem kết quả; không xóa Explain khỏi dữ liệu |
| Gợi ý dự phòng cho môn khác Toán vẫn yêu cầu lập phương trình/thế số | Chọn câu hỏi phương pháp theo môn. Ưu tiên câu hỏi gợi mở riêng nếu qua kiểm tra cấu trúc | Không chặn bài học, không gọi AI lại khi gợi ý cần dùng phương pháp dự phòng |
| Prompt thiếu số câu và cấu trúc tự luận đã thống nhất | Nêu rõ 3 trắc nghiệm và 2 tự luận × 4 bước Pólya tiếng Việt; gợi mở không giải hộ. Phần lý thuyết vẫn được giải thích và minh họa | Không áp lệnh giấu lời giải của Socratic lên lý thuyết; không bắt buộc ví dụ phải ra số |
| Metadata tác giả xuất hiện trong tự luận | Bỏ các trường dành riêng OUTCOME/COGNITIVE_REASON/COGNITIVE_STEPS trước khi hiển thị phần tự luận; đọc được giá trị JSON nhiều dòng hoàn chỉnh | Giữ câu hỏi và các bước Pólya; dữ liệu gốc vẫn ở phía máy chủ |
| Streamlit dọn widget khi chuyển trạm làm mất lựa chọn/bài viết | Lưu riêng và phục hồi lựa chọn hợp lệ của Trạm 1, trắc nghiệm/Đúng-Sai/đáp số và phần viết Ngữ văn của Trạm 3 | Giữ kiểu radio toàn văn hiện có; ngữ cảnh và đề mới vẫn dùng cơ chế đặt lại bài làm |
| Nút chuyển trạm yêu cầu thêm một lượt chạy lại | Cập nhật trạm bằng callback trước lượt chạy do click, bỏ `st.rerun()` dư ở thanh điều hướng | Giữ nhãn, vị trí và kiểu nút |
| Cắt ba ký tự cuối JSON khi chỉ có dấu mở code fence; tự đóng nội dung bị cắt | Lấy riêng parser và kiểm thử từ `20d838a` (PR14), bỏ thao tác cắt mù. Sửa cú pháp có giới hạn; không tự bổ sung câu/đáp án bị thiếu | Giữ LaTeX và nội dung đầy đủ; không nhập cả PR14 hoặc các thay đổi UI khác |

Ý tưởng giữ state/callback lấy từ PR8 và điều chỉnh cho giao diện PR6. Không nhập renderer radio chữ cái của các nhánh đời sau. Phần giảm nhiều dòng ở `data/socratic_anchors.py` là thay parser JSON cũ bằng parser có kiểm thử riêng, không phải bỏ HTML/CSS hay chức năng làm đề.

## Kiểm chứng

- Bộ kiểm thử chốt: **164/164 đạt**, gồm ca bảo toàn biểu thức/code, dấu bọc công thức, metadata nhiều dòng, gợi mở theo môn, alias Tiếng Anh/Toán và 13 ca JSON đã chọn từ PR14.
- Ma trận 65 cặp môn/lớp Trạm 1/3: **đã chạy đủ 65/65**, cả hai trạm mở/sinh fixture thành công; 3 radio, hai bài có đầu/cuối Pólya, infographic, liên kết YouTube và giữ bài làm Trạm 3 đều đạt ca QA. Không ghi nhận lại ba lỗi riêng tư/lựa chọn Trạm 1 đã tái hiện trước vá, không lộ Explain tại các vị trí thử của Trạm 3.
- Vẫn còn 6 cảnh báo phạm vi Lab và 6 cảnh báo Speaking theo lớp từ PR6. Không cộng chúng thành đã sửa; không gọi kết quả này là mọi nội dung đều đúng.
- Dữ liệu AI trong ma trận là giả lập. Chặn mạng, chặn ghi cache sản phẩm và chặn nhập dữ liệu giả vào ngân hàng. Tắt pha trộn ngân hàng riêng trong lượt fixture để kiểm được chính xác đường đi của hint/explain. Luồng chọn đề ngân hàng có kết quả kiểm riêng ở bản vá 01 và các kiểm thử hiện có.
- Ma trận kiểm bài học, 3 radio, hai bài có đầu/cuối Pólya, infographic, liên kết YouTube; khởi tạo đề đủ các phần theo môn; trả lời mẫu và chuyển Trạm 3 → 1 → 3 để đối chiếu bài làm. Đây không phải kiểm mọi cấu hình đề hoặc mọi dạng file nhập/xuất.
- Chrome MCP localhost cũng hoàn tất vòng T1 → T2 → T3 → T4 (khóa quản trị) → T1 ở trang cấu hình; không đăng nhập quản trị hoặc gọi AI trong vòng này. Không ghi thời gian vòng Chrome thành số đo độ trễ vì chưa đặt phép đo đồng nhất.
- Giữ các lượt thử dừng sớm thành bằng chứng riêng; không cộng chúng vào số ca nghiệm thu của mã chốt.

## Được / mất / token / độ trễ

Không đổi bố cục, font, assets infographic hoặc công cụ vẽ so với PR6. Không sửa bộ đọc trong bản vá này. Các chức năng chỉ có ở những PR sau PR6 chưa được nhập lại không được coi là đã nghiệm thu theo bản này.

Không thêm lượt gọi AI hoặc vòng lặp sinh lại. Trường hint riêng có thể làm tăng số token của một phản hồi; chưa đo usage thật nên không báo số tiết kiệm token. Callback loại bỏ một lượt chạy lại dư theo cấu trúc mã; số đo AI giả lập không đại diện độ trễ Cloud hoặc tốc độ mô hình thật.

## Giới hạn còn phải xử lý

- Chưa xác nhận toàn bộ kiến thức, đáp án duy nhất, mức độ nhận thức, yêu cầu cần đạt, SGK/SGV KNTT và hiệu lực từng văn bản tại ngày dùng. Giữ cảnh báo thẩm định.
- Kiểm tra gợi ý là kiểm cấu trúc và dấu lộ đáp án rõ ràng; không chứng minh mọi cách diễn đạt đều không gợi ra đáp án. Gợi ý phương pháp dự phòng theo môn không thay được gợi ý riêng cho mọi câu.
- Prompt nêu số câu/4 bước chưa phải bằng chứng mọi phản hồi AI thật đều tuân thủ. Không đặt thêm cổng cứng làm trống toàn bài.
- Công thức đã hỏng cú pháp bên trong hoặc metadata JSON hỏng cần kiểm riêng; không tự đoán kiến thức hay nuốt câu hỏi tiếp theo để sửa.
- Các cảnh báo phạm vi Lab và Speaking của PR6 được giữ riêng trong kết quả; chưa coi là đã sửa. Bộ đọc, mọi ảnh/BBT, tải file, xuất bản in và tải đồng thời nhiều người dùng chưa được nghiệm thu toàn bộ bằng ma trận này.
- Chưa triển khai nhánh này lên Cloud. CI Python 3.10/3.11 cần chạy trên PR; không suy từ kết quả local Python 3.14.

Những việc trên là thực hành kiểm thử và quản lý thay đổi có bằng chứng, không phải chứng nhận “đẳng cấp BigTech” hoặc “chuẩn Bộ 100%”.

## Bằng chứng trên máy

Thư mục `F:/FINAL KHKT 2026/qa_evidence/`: `PR6_PATCH02_FINAL_ACCEPTANCE_TESTS_20261027.log`, `PR6_PATCH02_ALL_CONTEXTS_20261027.json`, `PR6_PATCH02_FINAL_ACCEPTANCE_65_20261027.log` và các lượt thử riêng. JSON lưu hash mã nguồn để đối chiếu phiên bản chạy. Không đưa cache hoặc bản ghi học sinh lên Git.
