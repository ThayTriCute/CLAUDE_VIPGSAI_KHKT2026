# Giải trình bản vá chương trình, pháp lý và phục dựng theo ngữ cảnh

Mốc đối chiếu: **24/10/2026**. Sửa tại thư mục dự án gốc trên ổ F, kiểm tra cục bộ trước Git CLI push. Bản nền: `4a737de7f9e64e15c06d643d3da71bf11cc30044` (PR #3).

## Kết luận có bằng chứng

Đã phát hiện các bộ lọc cũ có những nhánh suy đoán/sửa nội dung theo mẫu; tên gọi nhiều tầng không chứng minh kiểm định chương trình. Bản vá tách kiểm tra cấu trúc/ngữ cảnh, phục dựng có dữ kiện, thay nguyên câu thiếu dữ liệu và duyệt học thuật. Không tuyên bố mọi học liệu AI đã đúng 100% hoặc được Bộ thẩm định.

Quét **toàn bộ 13 shard**, 33.679 bản ghi đề, **948.902 lượt câu hỏi** gồm cả đọc hiểu/viết. Chỉ có **3.165 chuỗi nội dung câu hỏi khác nhau** khi so riêng trường `q`; đây không phải số câu duy nhất nếu xét cả phương án, hình, đáp án và ngữ cảnh. Không tiếp tục quảng bá 948.902 lượt là 948.902 câu độc nhất.

Tất cả 33.679 đề hiện **chưa có trường bằng chứng** đối chiếu yêu cầu cần đạt (`curriculum_evidence`) và trang/phiên bản KNTT (`textbook_evidence`). 1.600 đề không khai báo URL HTTP tại các trường nguồn được quét; mọi lượt câu hỏi thiếu URL riêng tại `source_url`. Các trường đang thiếu không chứng minh bản ghi sai, nhưng cũng không đủ để chứng nhận nguồn gốc/chuẩn chương trình. URL được khai báo chưa được xác minh là tài liệu gốc hoặc chứng minh nguồn trường/Sở được gắn nhãn.

Kết quả máy đọc được: `data/curriculum_source_audit_20261024.json`. Script tái lập: `python scripts/audit_curriculum_sources.py --output <duong_dan.json>`. Không sửa nội dung các shard trong đợt này; giữ nguyên để truy vết và kiểm định tiếp.

## Văn bản và phạm vi đã rà soát

Danh mục có phiên bản và URL: `data/legal_references.json`; gồm thông tư, quyết định và công văn hướng dẫn, phân loại riêng; không coi tất cả đều là văn bản quy phạm pháp luật hoặc chứng nhận cho app.

| Căn cứ | Áp dụng đúng phạm vi |
|---|---|
| TT 32/2018, TT 20/2021, TT 13/2022, TT 17/2025 | Đọc chương trình gốc cùng sửa đổi, không dùng TT 32 riêng lẻ. TT 17/2025 sửa các nội dung LS&ĐL, Lịch sử 10, Địa lí, GDCD theo phụ lục tương ứng. |
| QĐ 3588 ngày 26/12/2025 | KNTT dùng thống nhất từ năm học 2026–2027; còn phải đối chiếu đính chính học liệu trực tuyến theo cuốn/phiên bản. |
| TT 22/2021; CV 7991/2024 | Đánh giá ở THCS/THPT và hướng dẫn tổ chức; không đồng nhất mọi bài luyện tập lớp 6–11 với thi tốt nghiệp. |
| TT 24/2024, sửa bởi TT 13/2026 | Quy chế tốt nghiệp THPT. TT 13/2026 ban hành 09/03/2026, hiệu lực 24/04/2026. Không phải quy chế phòng Lab hoặc ma trận bắt buộc cho mọi lớp. |
| QĐ 764 ngày 08/03/2024 | Đối chiếu ảnh phụ lục bản ký. Địa lí: 18/4/6, 50 phút, điểm 4,5/4/1,5. Tin học: đề in 6 câu Đ/S, thí sinh làm 4 theo định hướng (2 chung + 2 định hướng). App tạo 4 câu theo hướng được chọn; chưa phải bộ đề in đủ cả hai hướng. |
| CV 3175/2022 | Tránh dùng lại văn bản SGK đã học khi đánh giá cuối học kì/năm/cấp; không cấm mọi văn bản SGK khi dạy học ở Trạm 1. |
| CV 5512/2020 | Khung tổ chức kế hoạch giáo dục/bài dạy; tài liệu Bộ dẫn chiếu thiết kế linh hoạt. Không phải bộ chứng minh đúng mọi công thức. |
| TT 10/2025 | Phân định thẩm quyền quản lý; không phải ma trận câu hỏi. Có điều khoản thời hạn và thay thế tương ứng cần theo dõi. |
| **TT 89/2026** | Ban hành **16/10/2026**, hiệu lực **01/12/2026**. Đã lưu riêng là văn bản sắp hiệu lực; **không áp sớm** vào mốc 24/10. |

Không dùng dự thảo sửa chương trình ngoại ngữ được đăng tháng 8/2026 như quy định đã hiệu lực. Danh mục là phạm vi nguồn đã rà soát liên quan bản vá, không phải chứng nhận đã thu thập mọi văn bản ngành. Cần cập nhật khi có sửa đổi mới; không có lời hứa tự động theo dõi hằng ngày.

Nguồn chính: [TT 17/2025](https://vbpl.vn/bogiaoducdaotao/Pages/vbpq-toanvan.aspx?ItemID=183284), [QĐ 3588](https://xaydungchinhsach.chinhphu.vn/quyet-dinh-so-3588-qd-bgddt-ve-bo-sach-giao-khoa-giao-duc-pho-thong-su-dung-thong-nhat-toan-quoc-119251227145448874.htm), [TT 13/2026](https://chinhphu.vn/?classid=1&docid=217189&orggroupid=4&pageid=27160), [TT 89/2026](https://vanban.chinhphu.vn/?docid=220070&pageid=27160&typegroupid=6), [CV 3175](https://xaydungchinhsach.chinhphu.vn/huong-dan-doi-moi-phuong-phap-day-hoc-va-kiem-tra-mon-ngu-van-119220723081034079.htm), [bản ký QĐ 764 lưu tại cơ sở giáo dục](https://thptkrongana.edu.vn/wp-content/uploads/quyet-dinh-764-qd-bgddt-2024-cau-truc-de-thi-ky-thi-tot-nghiep-thpt-tu-2025.pdf).

## Nguyên nhân kỹ thuật → cách vá

1. **Sửa đề bằng mẫu:** đường cuối tự thay phương án C bằng `(-1; 2)`, tạo BBT/hàm có sẵn rồi đổi lời giải/đáp án cho khớp. Đã thay đường gọi bằng kiểm tra trên bản sao; không tự viết lại phương án, số liệu, đáp án gốc.
2. **Dữ liệu thiếu biến thành có vẻ hợp lệ:** validator/parser mặc định A, `True`, 0; `bool('false')` thành True. Nay thiếu/không xác định phải giữ trạng thái thiếu hoặc báo lỗi; chuẩn hóa boolean qua bộ phân tích rõ ràng; số 0 thật vẫn giữ. Không cắt/bù sai số câu âm thầm.
3. **Đổi lớp từ từ khóa:** bộ 7 tầng tự đoán lại lớp, kể cả qua nội dung. Nay kiểm tra metadata trước; không tự đổi lớp người dùng đã chọn. Tiêu đề/môn/lớp khai báo mâu thuẫn bị chặn, có kiểm tra cả cấu trúc đọc hiểu/viết và alias phần thi.
4. **Pháp lý áp quá rộng:** thông tin giao diện, lời nhắc và cấu trúc mặc định được đưa về cùng một policy. Lớp 6–11 hiển thị là luyện tập; Địa lí có TLN và thang điểm đúng bảng tham chiếu; Tin/Công nghệ có chọn định hướng.
5. **Lời nhắc tự mâu thuẫn:** bỏ lệnh tùy biến ghi đè mọi giới hạn, yêu cầu giả vờ đọc hai nguồn chỉ qua URL, cấm tuyệt đối mọi hàm bậc bốn/tên hóa học thông dụng, tỷ lệ Bloom tự chọn nhưng gọi là của Bộ. Yêu cầu mới ghi rõ giới hạn bằng chứng, môn/lớp, mục tiêu bài học và nguồn thật.
6. **Ngữ liệu chỉ mục chưa kiểm định:** danh sách `BIGDATA_CURRICULUM` được ghi là gợi ý biên tập; không gọi là mục lục/ma trận KNTT đã được thẩm định. URL sách/video là công cụ tra cứu, không tự chứng nhận học liệu AI.
7. **Hình PDF bị lẫn phần:** khóa `q_1` cũ ghi đè giữa phần I/II/III hoặc nhiều mã đề. Nay khóa `p1_q_1`/`p2_q_1`/`p3_q_1`, giữ SHA-256 tệp, trang, vùng cắt; chỉ tạo alias cũ khi duy nhất. Trường hợp lặp mã/đa cột không rõ được báo mơ hồ, không gắn hình phỏng đoán.

## Bộ phục dựng mới theo yêu cầu bổ sung

Giữ lại luồng đọc/cắt PDF thật và tái sử dụng bộ dựng TikZ hiện có cho phân thức. `services/context_recovery.py` điều phối:

1. Dùng hình/bảng/mô hình đầy đủ đã có trong dữ liệu nguồn.
2. Nếu thiếu hình mà câu có công thức tường minh, phân tích hệ số số học của đa thức bậc hai/ba hoặc phân thức 1/1, 2/1 được hỗ trợ; không dùng `eval`, không đảo từ đáp án để đoán hình, không trả mẫu khi không đọc được.
3. Nếu vẫn thiếu hoặc có mâu thuẫn đáp án được bộ kiểm chứng hiện có phát hiện: tìm **nguyên câu khác** cùng môn/lớp/chủ đề/phần thi, không dùng lặp cùng nội dung trong một lượt phục hồi. Giới hạn kiểm tra sâu 250 ứng viên khớp ngữ cảnh mỗi câu.
4. Nếu chưa có: có thể gọi AI sinh **nguyên câu thay thế**, giữ dạng bài đọc hình khi câu gốc cần hình; kiểm tra metadata, số phương án/mệnh đề, đáp án, nội dung hình và kiểm tra độc lập trong phạm vi solver hiện có. Không gắn nguồn/trường của câu cũ cho câu AI mới.
5. Tối đa **2 lần gọi AI bổ sung** mỗi lượt tạo đề. Có công tắc trên giao diện. Không gọi AI âm thầm khi chỉ xem trang hoặc xuất bài đã có.
6. Lưu hành động phục dựng/thay thế, lý do, hash câu gốc, nguồn câu thay; không sửa dữ liệu đầu vào tại chỗ. Nếu vẫn thiếu dữ liệu thì **chưa mở lượt làm bài**, hướng dẫn bổ sung nguồn/duyệt bản nháp.

Đây là phục dựng/thay thế có kiểm soát, không phải bằng chứng mọi câu đã đúng học thuật. Solver mới kiểm tra được một số dạng; một lời nhắc “tự giải ngầm” không được coi là kiểm chứng độc lập cho mọi môn.

## Đánh đổi và giới hạn thực tế

- Những hình trước đây chỉ có nhờ mẫu suy đoán sẽ cần hình gốc, công thức hỗ trợ hoặc câu thay thế. Không khôi phục mọi ảnh scan/mọi mô hình 3D/BBT từ dữ liệu không đủ. Đây là giới hạn được hiển thị, không phải chứng nhận 100% phục dựng.
- Quét PDF giới hạn 30 MB, 150 trang và 100 vùng; đọc PDF ảnh không có lớp chữ, nhiều cột hoặc nhiều mã đề còn cần OCR/đối chiếu. Bản cắt là vùng câu gốc; gắn số câu do AI trích vẫn cần đối chiếu.
- Luồng thay thế hiện hỗ trợ các phần p1/p2/p3. Ngữ văn cần thay cả đoạn ngữ liệu + câu hỏi + rubric, nên không thay riêng một câu để làm lệch toàn bộ đề.
- Chưa có kho outcome/trang KNTT đã được giáo viên phê duyệt cho toàn bộ 65 cặp môn/lớp; GDKT&PL lớp 10–12 còn thiếu kho. Không thể gọi toàn bộ 33.679 đề là đã đạt chuẩn KNTT chỉ dựa metadata.
- Chưa kiểm thử tải thực tế, p95, bộ nhớ nhiều phiên hoặc mọi thiết bị/PDF in ra. Các cảnh báo ngừng dùng API Streamlit cũ vẫn còn ở phần ngoài phạm vi.
- Chưa đạt bằng chứng vận hành ở quy mô Big Tech. Những phần cải thiện có thể kiểm tra được: policy chung có phiên bản, chuẩn hóa không đoán đáp án, thay câu nguyên tử có dấu vết, giới hạn tài nguyên/gọi AI, kiểm thử hồi quy. Không dùng các từ SOTA/100% làm thước đo.

## Kiểm thử và hoàn tác

Các kiểm thử bao gồm: Địa lí 18/4/6 và điểm 4,5/4/1,5; TT 89 chưa áp trước 01/12; chặn lớp khai báo sai; không tự gán A/True/0; không sửa phương án C khi xuất; phục dựng hệ số chính xác; từ chối thiếu công thức; thay nguyên câu đúng ngữ cảnh; từ chối câu AI sai lớp/đáp án mà solver phát hiện; giới hạn gọi AI; không dùng lặp câu; PDF cùng số khác phần không ghi đè; từ chối mã đề trùng mơ hồ. Có AppTest cho giao diện lớp 6, Địa lí 12 và chặn yêu cầu Trạm 1 nhắc lớp khác.

Kết quả chạy cuối, ảnh giao diện và commit/PR được ghi trong biên nhận QA của đợt này. Hoàn tác bằng commit `git revert` của bản vá rồi push bình thường; không force-push/xóa lịch sử. Dữ liệu kho nguồn không bị ghi lại trong đợt này.

## Kết quả kiểm tra trước push

- `python -u deep_check_var_project.py`: **126/126 tests đạt**, 44 tệp Python qua kiểm tra tĩnh/dữ liệu; lượt chạy 192,576 giây trên máy cục bộ khi có các tác vụ kiểm thử khác. Không dùng thời gian này làm benchmark tốc độ app.
- Bổ sung AppTest trọn luồng sinh đề thiếu hình → kho không có → AI sinh nguyên câu thay thế → phục dựng hàm tường minh → mở lượt làm bài: **1/1 đạt**, 20,483 giây; dùng mô phỏng phản hồi AI, không phải kiểm định học thuật trên Gemini thật.
- Sau bổ sung giới hạn 250 ứng viên kiểm tra sâu, chạy lại bộ phục dựng/PDF: **15/15 đạt**. Tổng bộ hiện tại 127 tests; CI sẽ chạy thống nhất toàn bộ.
- `git -c core.whitespace=cr-at-eol diff --check`: đạt. Ảnh kiểm tra giao diện: `F:\FINAL KHKT 2026\qa_evidence\context_recovery_local.png`.
- Bản vá loại các đường tự sửa/đoán học liệu cũ khỏi luồng chạy; không xóa các mô-đun quét nguồn hoặc toàn bộ thư viện hình học. Có thể còn hàm tương thích cũ chưa dùng trong luồng mới.
