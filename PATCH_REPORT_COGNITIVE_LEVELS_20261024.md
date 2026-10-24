# NB–TH–VD–VDC ở Trạm 1 và Trạm 3 — 24/10/2026

## Kết luận kiểm tra

Trước bản vá, chưa có căn cứ xác nhận câu hỏi ở cả hai trạm đúng mức nhận thức. Phát hiện cơ chế tự gán nhãn theo dạng câu hoặc đổi nhãn để khớp yêu cầu mà không sửa nhiệm vụ tư duy. Bản vá bỏ các đường gán này, bổ sung căn cứ tự khai và báo cáo đối soát; **không biến nhãn AI thành kết quả thẩm định**.

## Căn cứ và phạm vi

- [CV 7991/BGDĐT-GDTrH, 17/12/2024 — bản lưu tại cơ sở giáo dục](https://c3nguyencongphuong.quangngai.edu.vn/van-ban/so-7991-bgddt-gdtrh), [bản PDF gốc được trang trường dẫn](https://c3nguyencongphuong.quangngai.edu.vn/wp-content/uploads/2024/12/20241210-Cong-van-7991-huong-dan-KTDGDK.pdf). Đọc trực tiếp nội dung ba trang qua bản sao cùng văn bản tại [đây](https://cdn.thuvienphapluat.vn/uploads/Hoidapphapluat/2024/NTH/20122024/20241210-Cong-van-7991-huong-dan-KTDGDK.pdf).
- Phụ lục có Biết/Hiểu/Vận dụng ở **từng dạng câu**, bản đặc tả gắn yêu cầu cần đạt. Bảng mẫu thể hiện tỷ lệ **điểm** 40/30/30; không phải tỷ lệ số câu và không chứng minh mọi bài luyện tập/thi tốt nghiệp phải áp mẫu đó.
- Đoạn triển khai ma trận định kì của công văn nêu cơ sở giáo dục cấp THPT, tham khảo phụ lục và theo hướng dẫn Sở; không tự áp chung mọi môn, mọi lớp. Cần hướng dẫn địa phương/nhà trường và ma trận được duyệt cho từng bài. Không nhập hướng dẫn tỉnh khác làm quy định của An Giang.
- VDC được giữ như nhãn phân hóa mở rộng trong app; khi đối chiếu ba mức, báo cáo quy chiếu vào VD và vẫn giữ chi tiết VDC. Không tự tuyên bố VDC là cột bắt buộc riêng của CV 7991.
- Mức nhận thức phải đánh giá nhiệm vụ tư duy so với yêu cầu cần đạt và nền kiến thức đã học. Độ khó thực nghiệm là kết quả quan sát sau khi học sinh làm bài, không đồng nghĩa một-một với NB/TH/VD/VDC.

## Nguyên nhân kỹ thuật và cách sửa

1. **Trạm 1:** parser mặc định thiếu nhãn thành “Vận dụng”. Đổi thành chưa xác định. Prompt yêu cầu nhãn đề xuất, yêu cầu cần đạt, căn cứ phân loại và thao tác tư duy ở cả trắc nghiệm và tự luận; parser trắc nghiệm tách các dòng căn cứ khỏi đề/phương án. Giao diện ghi rõ chưa duyệt. Phần tự luận vẫn là Markdown, chưa có parser/rubric cấu trúc hoàn chỉnh để đối soát ma trận điểm.
2. **Trạm 3:** pipeline, parser PDF/text và schema từng mặc định P.I=NB, P.II=TH/TH-VD, P.III=VD/VD-VDC. Bỏ các mặc định; chuẩn hóa tên gọi, giữ nhãn nguồn riêng, nhãn thiếu/ghép là chưa xác định. Không đoán bằng độ dài, từ khóa hoặc số bước tính.
3. **Trộn đề:** bỏ ép nhãn P.I về TH hoặc P.III về VD để đáp ứng prompt; bỏ ưu tiên độ nhận thức chỉ dựa phần đề. Giữ thứ tự khớp chủ đề/tùy biến và cooldown. Lựa chọn theo nhãn nguồn vẫn không chứng minh mức độ; chưa có bộ giải phân loại ngữ nghĩa độc lập cho toàn bộ môn/lớp.
4. **Mệnh đề Đúng/Sai:** schema từng dựng lại `stmts` chỉ còn nội dung và đáp án, làm mất nhãn/căn cứ. Giữ metadata riêng cho `stmts`, `items` dạng object và `statements`; không đổi False thành True. Báo cáo đếm câu và từng ý riêng, không lấy nhãn câu cha gán cho a/b/c/d.
5. **Phục dựng/thay câu:** nếu câu gốc có nhãn đơn xác định, câu thay phải khai báo cùng nhãn; không âm thầm đổi mục tiêu nhận thức. Đây chỉ là kiểm tra tính nhất quán khai báo, chưa chứng minh câu mới thực sự đạt mức đó.
6. **Prompt tương thích cũ:** bỏ quy tắc vô căn cứ 60% NB/40% TH ở P.I, mặc định mức theo vị trí ý và 100% VD/VDC ở P.III; bỏ lời tự nhận nguồn đã được duyệt.
7. **Bộ lọc cuối:** thêm báo cáo nhận thức bên cạnh dữ liệu đề, giữ nguyên câu/phương án/đáp án. Báo cáo có nhãn, căn cứ tự khai có/không, trạng thái cần giáo viên duyệt và hash nội dung. Không chấp nhận trường `verified=true` do AI tự gửi. Báo cáo trong phòng luyện tập không hiển thị lời giải/căn cứ chi tiết có thể làm lộ đáp án.

## Quét kho nguồn (không sửa tệp kho)

`scripts/audit_cognitive_sources.py` đọc tuần tự toàn bộ 13 shard; kết quả tại `data/cognitive_source_audit_20261024.json`:

| Chỉ tiêu | Số lượt |
|---|---:|
| Bản ghi đề | 33.679 |
| Câu hỏi | 948.902 |
| Câu thiếu nhãn đơn rõ ràng | 71.801 |
| Ý Đúng/Sai | 458.216 |
| Ý thiếu nhãn đơn rõ ràng | 244.776 |
| Câu thiếu bộ metadata yêu cầu cần đạt/căn cứ/thao tác | 948.902 |
| Câu không có metadata duyệt mức độ của giáo viên | 948.902 |

Các số là lượt xuất hiện, không phải số câu duy nhất. Thiếu metadata không chứng minh mọi câu sai. Không có phép kiểm tự động nào ở đây xác nhận ngữ nghĩa mức độ của toàn bộ kho. Các nhãn trong kho không được viết lại hàng loạt để tạo cảm giác đã chuẩn hóa học thuật.

## Kiểm thử và tối ưu

- `python -u deep_check_var_project.py`: **138/138 tests đạt**, 47 tệp Python qua kiểm tra; 90,945 giây, không dùng làm benchmark tốc độ app.
- Bộ 11 kiểm thử mức độ riêng chạy sau cập nhật metadata: **11/11 đạt**, 28,749 giây. Bao gồm không suy mức từ dạng/độ dài câu, không mặc định VD ở Trạm 1, không công nhận căn cứ AI tự khai là duyệt, bảo toàn nhãn/căn cứ từng ý, đối soát Ngữ văn, giữ mục tiêu khi thay câu, giữ nguyên câu/đáp án ở cổng cuối.
- AppTest toàn luồng tạo đề/thay câu mở phòng làm bài không phát sinh exception, báo cáo mức độ có mặt và luôn ghi chưa thẩm định. Không có cuộc gọi Gemini thật trong các ca kiểm thử này.
- Các kiểm tra cũ bảo toàn phương án C và nguyên học liệu tiếp tục đạt. Báo cáo nhận thức nằm ngoài payload câu hỏi ở cổng xuất cuối.
- Không thêm lượt AI để giả lập một “giám khảo độc lập”. Runtime xử lý tuyến tính trên đề đã chọn, không quét toàn kho mỗi lần tương tác. Audit kho là lệnh ngoại tuyến, đọc streaming. Không có đo tải/p95 trong đợt này, chưa có bằng chứng vận hành quy mô Big Tech.

## Công việc cần để xác nhận chất lượng phân loại

Cần bộ câu chuẩn do giáo viên từng môn/lớp duyệt, gắn yêu cầu cần đạt và lời giải, đối chiếu hướng dẫn An Giang cùng ma trận/đặc tả từng bài; sau đó đánh giá trên tập câu giữ riêng, đo nhầm lẫn NB↔TH↔VD/VDC và mức đồng thuận giữa người chấm. Chỉ mở trạng thái “đã duyệt” qua quy trình giáo viên xác thực gắn với phiên bản nội dung. Cần thí điểm học sinh để đo độ khó và khả năng phân biệt. Hiện chưa triển khai quy trình duyệt này; bản vá **chưa đủ để tuyên bố mọi câu đúng mức chuẩn Bộ**.

Hoàn tác bằng `git revert` commit bản vá và push thông thường; không force-push hoặc đổi nội dung shard nguồn.
