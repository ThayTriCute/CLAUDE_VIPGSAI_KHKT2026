# Cổng kiểm tra công thức trước khi hiển thị — 25/10/2026

## Lỗi gốc và cách vá

Trước bản vá, phần lớn đường hiển thị chính chỉ làm sạch chuỗi LaTeX rồi giao cho KaTeX trong frontend; bộ lọc cuối không chạy parser thật trên toàn bộ trường nội dung. Khả năng mhchem/phiên bản frontend cũng có thể khác bản HTML xuất. Vì vậy “đã làm sạch” không chứng minh công thức dựng được.

Kiểm tra trực quan còn phát hiện `deep_clean_pua_and_artifacts` dùng biểu thức xóa `$` + khoảng trắng + `$` trước khi nhận diện khối toán. Nó xóa luôn `$$` mở/đóng của công thức hợp lệ, hoặc nối nhầm hai công thức inline đứng cạnh nhau. Đã đổi sang đọc token toán/code rồi chỉ bỏ khối thực sự rỗng; giữ nguyên công thức khối, cặp inline liền nhau và code mẫu. Không chỉ dựa việc không có ô lỗi đỏ để kết luận công thức hiển thị đúng.

`services/math_publication.py` nạp **đúng tệp KaTeX/mhchem đóng gói trong dự án** bằng `mini-racer==0.14.1`. Không tải công thức lên dịch vụ khác. Kiểm tra dấu phân cách, lệnh trơ ngoài vùng toán, lệnh không hỗ trợ và chạy `renderToString` với `throwOnError`. Không dùng eval Python hoặc tự đổi công thức thành Unicode gần đúng. Code mẫu và ký hiệu dollar được escape không bị hiểu nhầm là công thức.

Cổng Trạm 1, Trạm 3 và xuất HTML gọi kiểm tra trước khi công bố. Các trường câu hỏi, phương án, đáp án, giải thích, từng ý Đúng/Sai và ngữ liệu đọc được kiểm tra; không quét chuỗi ảnh base64 hoặc coi cú pháp BBT riêng là LaTeX thông thường. Phiên đề cũ đang làm được kiểm tra lại trước khi mở câu hỏi. Nguồn lỗi trả trạng thái rõ và có đường quay lại cấu hình.

Các phần chính của bài học/câu hỏi, phương án trắc nghiệm, gợi ý và giải thích Trạm 3 dùng HTML công thức dựng từ cùng renderer. Phương án hiển thị tách khỏi nút chọn A/B/C/D; vẫn lưu phương án gốc để chấm, không đổi đáp án sau khi đảo lựa chọn. Markdown nguồn mặc định không cho raw HTML; chỉ bố cục/hình cục bộ đã thêm sau bước escape nguồn mới dùng nhánh bố cục tin cậy. Không để việc hỗ trợ HTML công thức mở thêm đường HTML thô từ câu hỏi.

Trạm 1 thử sửa cú pháp tối đa một lượt thêm. Trạm 3 đưa câu có lỗi công thức vào luồng thay nguyên câu có sẵn, giới hạn hai lượt AI cho toàn đề, giữ môn/lớp/chủ đề và mục tiêu mức độ khai báo. Không bảo đảm AI sửa thành công và không mặc định nội dung sau sửa đã đúng khoa học. Phép chuẩn hóa alias tập số thực có dấu phân cách rõ, không tạo `mathbb` trơ ngoài toán hoặc sửa code mẫu.

Đồng thời bỏ đường tự chèn hình mẫu Lý/Hóa/Sinh/Toán vào bài học chỉ vì trùng từ khóa. Dữ liệu gốc/BBT có dữ kiện, công cụ phục dựng câu hỏi và các mô phỏng người dùng chọn trong Phòng Lab được giữ. Một sơ đồ mẫu không tự chứng minh khớp số liệu/ngữ cảnh bài hiện tại.

## Giới hạn tài nguyên và tối ưu

- Một V8 context cho mỗi tiến trình, có khóa; bộ nhớ heap V8 giới hạn 96 MiB (**không phải giới hạn RSS toàn bộ Python**), timeout khởi tạo/gọi parser và chờ khóa.
- Tối đa 500 công thức mỗi khối, 4096 ký tự mỗi công thức, 250.000 ký tự mỗi khối văn bản, 500.000 ký tự các trường nội dung một đề. Vượt giới hạn phải chia/kiểm tra lại bản nháp.
- Cache tối đa 128 công thức dựng ngắn, không cache không giới hạn cả bài. Thử lại AI có giới hạn, không lặp vô hạn. Không tăng thêm lượt AI cho công thức hợp lệ.
- Thêm runtime V8 có chi phí bộ nhớ/khởi tạo và phụ thuộc mới. Chưa có benchmark p95/tải đồng thời Cloud; không khẳng định hết lag hoặc đạt quy mô Big Tech. Khi parser chưa chạy được hoặc đang bận, không giả thành kiểm tra thành công.

## Kiểm tra và giới hạn kết luận

Kiểm thử gồm lệnh lỗi, dấu sai, căn/phân thức/hệ phương trình, omega/Ohm/véc-tơ, tiếng Việt trong math, mhchem, từng trường đáp án/giải thích, nguồn HTML thô, giới hạn, cạnh tranh cache, cache eviction, phục hồi có giới hạn và AppTest chọn đúng công thức nước sau đảo phương án. Kết quả toàn bộ bộ kiểm thử được ghi theo lượt chạy cuối trong biên nhận QA; các lượt phát hiện lỗi được giữ trong log, không coi là bản phát hành đạt.

Lượt cuối sau khi cố định mã: `python -u deep_check_var_project.py` **155/155 tests đạt**, 49 tệp Python qua kiểm tra, 99,701 giây. Xem trực tiếp Chrome trên Streamlit cục bộ với phiên QA nạp sẵn, DB riêng, không gọi Gemini: Trạm 1 có đạo hàm hiển thị dạng khối; Trạm 3 có phân số/căn/phương án A–D và chọn B được ghi nhận. Không thấy phần tử `.katex-error`/`.formula-error` trong các mẫu; đã kiểm tra cả biểu thức thô không bị mất dấu `$$`, không chỉ số lỗi. Viewport 390 px không tràn ngang trong phép đo DOM; không chứng nhận trải nghiệm trên mọi điện thoại. Ảnh ở `F:\FINAL KHKT 2026\qa_evidence\math_gate_station1_local_20261025.png` và `math_gate_station3_local_20261025.png`. Đã trả viewport về mặc định.

Kiểm tra cú pháp **không chứng minh** một phương trình đúng, đáp án đúng, kiến thức đúng lớp, mức nhận thức đúng hoặc trang sách KNTT tương ứng. Có những đường hiển thị phụ, bảng/đồ họa riêng và mọi thiết bị vẫn cần rà soát/kiểm tra. Không tuyên bố đã đạt tiêu chí “mọi thứ hoàn hảo”. Bảng nghiệm thu và các khoảng trống tại `QUALITY_ACCEPTANCE_STATIONS_1_3.md` là một phần của bàn giao.

Ngày 25/10/2026 đối chiếu lại [nguồn Chính phủ về TT89/2026](https://chinhphu.vn/?classid=1&docid=220070&orggroupid=4&pageid=27160): hiệu lực 01/12/2026, không áp sớm. Registry pháp quy vẫn là ảnh chụp có ngày kiểm tra, không phải chứng nhận đã rà toàn bộ văn bản mới trong ngày.

Hoàn tác bằng `git revert` commit bản vá và push thông thường. Không sửa shard học liệu nguồn hoặc bí mật truy cập.
