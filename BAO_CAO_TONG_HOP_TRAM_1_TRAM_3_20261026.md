# Báo cáo tổng hợp các bản vá Trạm 1 và Trạm 3

Ngày 26/10/2026 — dự án Gia sư AI, lớp 6–12.

**Phân biệt ba mức bằng chứng:** (1) đã sửa mã và kiểm thử kỹ thuật; (2) đã quan sát một tình huống trên Cloud; (3) đã đối chiếu nội dung với yêu cầu cần đạt và phiên bản SGK. Một mức không tự chứng minh mức tiếp theo. Báo cáo này không xác nhận toàn bộ hệ thống đã chuẩn khoa học/CT2018/KNTT 100%.

## 1. Các thay đổi Trạm 1

| Vấn đề | Nguyên nhân kỹ thuật | Cách vá và hành vi hiện tại | Giới hạn cần biết |
|---|---|---|---|
| Mất ba câu trắc nghiệm/hướng dẫn tự luận | Rút gọn prompt làm mất ràng buộc; thiếu hợp đồng chức năng khi kiểm thử | Cổng xuất bản đòi đúng 3 câu, 4 lựa chọn/câu, khóa chấm riêng; đúng 2 bài tự luận với 4 bước tiếng Việt | Đủ số lượng không chứng minh từng câu đúng khoa học |
| Radio chỉ còn A–D hoặc lệch bố trí | Sửa công thức đã thay cách hiển thị lựa chọn | Khôi phục radio dọc chứa đủ nội dung; giữ lựa chọn và khóa chấm; hóa học qua parser mhchem tương ứng | Không suy ra mọi thiết bị/trình duyệt đã được kiểm |
| Socratic bị dùng lẫn với giải thích | Trường gợi mở không tách khỏi lời giải/metadata | Trường gợi mở riêng theo từng câu; không lấy EXPLAIN làm gợi mở trước chấm; dữ liệu cũ chỉ gọi bổ sung khi bấm, có cache | Bộ dò rò đáp án có phạm vi; chưa chứng minh ngữ nghĩa tuyệt đối |
| Pólya lộ lời giải, tiếng Anh hoặc metadata | Hiển thị bản thô; tiêu đề/body định dạng khác nhau | Dựng lại bốn bước tiếng Việt; bỏ đuôi metadata; chuẩn hóa tiêu đề in đậm/cùng dòng/lặp; giữ câu hỏi hướng dẫn | Chưa tự chứng minh mọi câu gợi mở đúng nghiệp vụ môn |
| Câu yêu cầu lập bảng bị báo thiếu bảng | Bộ dò bắt mọi cụm “bảng biến thiên/bảng xét dấu” | Phân biệt yêu cầu tạo bảng với tham chiếu bảng đầu vào bị thiếu | Bảng/hình thực sự thiếu vẫn phải phục hồi hoặc thay trọn câu |
| Gợi mở hợp lệ bị chặn | Regex coi f'(x)=0 hoặc tiền tố văn xuôi là đáp số tính hộ | Tách vế trái phương trình, chuẩn hóa khoảng trắng; cho phép hỏi điều kiện phương pháp, vẫn chặn một số nghiệm số mới | Không dùng việc qua regex làm chứng nhận gợi mở đúng |
| Câu có hình/hàm số chưa đủ | Không gọi bộ phục dựng trong cổng xuất bản hoặc không đủ dữ liệu gốc | Dựng từ công thức số rõ ràng; một số câu dấu a,d bậc ba dựng hàm đại diện theo điều kiện và kiểm lựa chọn độc lập; nếu không đủ phải biên soạn lại toàn câu | Hình đại diện không phải ảnh gốc; không tự thay một phương án để ép khóa |
| Sai môn/lớp không được tự sửa | Lỗi chính sách trả ValueError, ngoài nhóm lỗi được sửa lại | AcademicPolicyError vào đúng một lượt sửa của Trạm 1; kiểm dòng kết hợp môn/lớp và lớp ngoài phạm vi | Không bắt mọi ngoại lệ để gọi AI vô hạn |
| Nhầm CO/Co, A/a | So phương án sau khi đổi chữ thường | Giữ phân biệt hoa–thường và khoảng trắng có ý nghĩa | Chặn trùng văn bản không chứng minh độc lập duy nhất đáp án đúng |
| Khảo sát bậc bốn trong yêu cầu bậc ba | Prompt không đủ; thiếu kiểm tra phạm vi cụ thể | Bộ kiểm phạm vi Toán 12 áp cho nhiệm vụ khảo sát cơ bản/bậc ba; sửa cả câu khi lệch | Không cấm mọi x⁴ trong tích phân hoặc mọi nội dung toán |
| Bài toán thực tế thiếu giả thiết miền biến | AI có thể áp đạo hàm cho lượng rời rạc mà không nói rõ mô hình | Prompt yêu cầu miền biến, đơn vị, biên và giả thiết liên tục/rời rạc | Đây mới là chỉ dẫn sinh; chưa có bộ chứng minh mọi mô hình thực tế |
| Infographic sai phong cách hoặc lạc nội dung | Trộn ví dụ/hình mẫu theo từ khóa; CSS chưa sát mẫu | HTML giữ nội dung nguồn, hash và ngữ cảnh; giấy kem ô ly, gáy đen, chữ xanh Caveat, tiêu đề đỏ; KaTeX/mhchem thật; nhiều trang | Không sao chép nét chữ ảnh gốc; PDF qua In/Lưu PDF, chưa kiểm mọi cách ngắt trang |
| Video biến mất hoặc bị hiểu là đã thẩm định | Luồng nguồn/trình bày thay đổi | Giữ liên kết tìm YouTube theo môn/lớp/chủ đề, ghi rõ khi chỉ là kết quả tìm kiếm | Liên kết tìm kiếm không chứng minh video đúng kiến thức |
| Speaking lớp 6 hiện Life stories lớp 12 | Hàm nhận lớp nhưng dùng chung bốn mẫu; widget không gắn lớp | Bản vá Speaking tách mẫu theo lớp, giữ bốn mẫu nâng cao ở lớp 12, bỏ số Unit chưa đối chiếu; khóa chọn/audio/text gắn lớp | Mẫu ứng dụng biên soạn, không phải kho toàn bộ Unit/trang KNTT |
| Speaking tự hứa IELTS/Band 8, chấm phát âm từ chữ | Prompt cũ áp giám khảo IELTS cho mọi lớp và cả văn bản thuần | Giữ micro/nhập bài/phản hồi; góp ý đúng lớp và loại bằng chứng, không quy đổi chứng nhận; không có audio thì không giả vờ đã nghe | Chất lượng phản hồi AI vẫn cần đối chiếu; chưa có thẩm định chuyên gia phát âm |

Chi tiết: [khôi phục Trạm 1](PATCH_REPORT_STATION1_RESTORATION_20261025.md), [xuất bài](PATCH_REPORT_LESSON_PUBLICATION_20261025.md), [sổ tay](PATCH_REPORT_NOTEBOOK_INFOGRAPHIC_20261024.md), [Speaking](PATCH_REPORT_ENGLISH_SPEAKING_GRADE.md).

## 2. Các thay đổi Trạm 3

| Vấn đề | Nguyên nhân kỹ thuật | Cách vá và hành vi hiện tại | Giới hạn cần biết |
|---|---|---|---|
| JSON đầy đủ nhưng bị cắt hỏng | Cắt ba ký tự cuối code block dù thiếu dấu đóng | Dùng bộ đọc chung chỉ bỏ dấu thực sự tồn tại; phục hồi có giới hạn dấu nháy/phẩy, giữ LaTeX | Chưa có bản thô của lỗi dòng 558 để khẳng định đã tái hiện đúng lỗi đó |
| Phản hồi dài xử lý tốn công hoặc chấp nhận bản cắt | Quét/cắt chuỗi lặp; tự bù dấu đóng | Quét một lượt; giới hạn 2 triệu ký tự, tối đa tám lần sửa dấu phân cách; chặn khóa trùng và nội dung cắt thật | Không thể sửa mọi JSON; không tạo câu/khóa chấm để lấp thiếu |
| Câu lỗi bị cấm luôn dù còn lượt sửa | Chỉ thử một lần cho câu, không dùng lý do từ chối ở lần tiếp | Ưu tiên phục dựng/tìm câu kho cùng ngữ cảnh; sửa nguyên câu bằng AI, kiểm lại và phản hồi mã lỗi | Tổng tối đa hai lượt sửa logic cho toàn đề; không phải hai lượt cho từng câu hay giới hạn tuyệt đối số request của provider fallback |
| Thay câu đọc LaTeX khác đề chính | Dùng json.loads riêng | Dùng chung safe_json_loads; ghi accepted/rejected/unavailable và pha/loại lỗi an toàn | Lỗi provider chưa được giải quyết chỉ bằng sửa parser |
| Phần sai kiểu bị bỏ qua | Bộ duyệt chỉ đi qua list | Cổng cấu trúc kiểm từng phần hiện diện, kiểu câu/phương án/mệnh đề, số câu; chặn rỗng/trùng và khóa thiếu | Cấu trúc hợp lệ vẫn có thể chứa kiến thức sai |
| Ngữ văn kiểm thiếu khối ngữ liệu | Chỉ kiểm câu con | Kiểm khai báo môn/lớp của đoạn đọc; nội dung không chỉ khoảng trắng, câu hỏi phải là list; không thay lẻ đoạn đọc và giữ rubric cũ | Chưa có phục hồi đồng bộ đoạn đọc–câu hỏi–rubric hoàn chỉnh |
| Hai nút tạo đề gây khó hiểu | UI tách nguồn trước khi người dùng tạo | Một nút Tạo đề luyện tập, ưu tiên kho; AI bổ sung khi được bật; giữ bốn chế độ; bỏ khung hai luồng | Kho chưa đủ và AI tắt thì báo rõ, không tự gọi AI |
| Chế độ đề thật rỗng rơi sang tạo AI | Điều kiện UI ghép mode với danh sách không rỗng | Giữ nhánh đề thật độc lập, kể cả kho rỗng | Không giả đề AI thành đề thật |
| Nguồn AI/mẫu bị gắn là đề thật | Cờ nguồn bị ghi đè ở nhiều đường | Giữ cờ nguồn cấp đề/câu/cache; mẫu biên soạn tách khỏi nguồn thật; đề trộn giữ nguồn từng câu | Nhãn trường/URL vẫn chưa chứng minh tài liệu gốc đã được đối chiếu |
| Mẫu kiểm toán học sai khóa hoặc sai điểm cực trị | Dữ liệu mẫu/giải thích không đồng nhất | Sửa ba khóa Đ/S của mẫu đạo hàm và điểm cực tiểu mẫu phân thức; kiểm độc lập các trường hợp này; so đáp số số học ở audit cực trị | Không suy ra toàn kho đã được giải độc lập |
| Tự sửa phương án C/đáp án để hợp hình | Healer cũ can thiệp payload | Đường xuất giữ câu/phương án/khóa; không gọi healer đoán đáp án/hình mẫu | Cần tiếp tục rà các đường legacy; không khẳng định mọi đường cũ đã được chứng minh |
| Kết quả Anh tự suy A2/B1/B2 | Ngưỡng điểm luyện tập bị biến thành CEFR | Giữ điểm, ghi phạm vi bài luyện tập; không gán CEFR; bỏ 0,25 điểm/câu cho đề tùy biến bất kể độ dài | Chưa có nghiên cứu liên kết bài thi với CEFR |
| Không có dữ liệu lỗi để truy nguyên | Chỉ hiện thông báo đỏ, hoặc chỉ lưu lỗi parse | Giữ bản thô đã che khóa và bối cảnh lỗi parse/kiểm sau JSON; chỉ admin xem/tải | Không có bản thô cũ thì không kết luận biết ký tự/nguyên nhân chính xác |

Chi tiết: [JSON](PATCH_REPORT_STATION3_JSON.md), [lượt sửa](PATCH_REPORT_BOUNDED_QUESTION_RETRY.md), [nguồn kho](PATCH_REPORT_BANK_ORIGIN_AND_AUTHORED_EXAMPLES.md), [một nút](PATCH_REPORT_SINGLE_PRACTICE_BUTTON.md), [diagnostics](PATCH_REPORT_EXAM_VALIDATION_DIAGNOSTICS.md).

## 3. Bộ lọc chung, mức độ và nguồn

- Tên môn dùng danh mục thống nhất: Toán/Toán học; Địa lí/Địa lý; Tiếng Anh/Anh/English… Kiểm đúng tổ hợp môn/lớp; THCS dùng môn tích hợp tương ứng. Sai khai báo được phát hiện trước khi bước chuẩn hóa có thể ghi đè.
- Bỏ mặc định mức độ theo phần, độ dài hoặc ép nhãn cho đủ tỷ lệ. NB/TH/VD/VDC là đề xuất chưa duyệt; từng ý Đ/S giữ căn cứ riêng. Không công nhận cờ tự khai `verified=true` của AI là thẩm định. Xem [báo cáo mức độ](PATCH_REPORT_COGNITIVE_LEVELS_20261024.md).
- Chạy parser KaTeX/mhchem thật trước xuất bản, dùng phông đóng gói; không coi công thức dựng được là công thức đúng khoa học. Giữ omega/đơn vị/công thức theo ngữ cảnh, không thay thành ký hiệu khác để hết lỗi.
- Kiểm các khai báo bộ sách mâu thuẫn ở đề, câu, đoạn đọc và đầu bài học; câu trắc nghiệm mâu thuẫn có đường thay nguyên câu. Không nói thiếu tên sách đồng nghĩa đã đúng KNTT, hoặc ghi KNTT là đã tra trang sách.
- Áp ngày hiệu lực pháp quy theo ngày Việt Nam thay vì đóng băng ngày nguồn được rà soát. Registry vẫn là ảnh chụp có ngày, không có đảm bảo tự cập nhật đầy đủ mọi văn bản mới/được sửa/hết hiệu lực.
- Các URL sách/chủ đề hiện có chủ yếu là điều hướng. Chưa có bộ yêu cầu cần đạt/trang/phiên bản/đính chính đầy đủ cho 65 tổ hợp. Nguồn bổ trợ như OLM không thay thế văn bản của Bộ/NXBGD.

## 4. Tốc độ, trạng thái, giọng đọc và triển khai

- Nút chuyển trạm dùng callback, giảm một lượt rerun thừa; giữ đáp án/deadline khi rời rồi trở lại. Form soạn bài và cache có khóa đủ môn/lớp/chủ đề/nội dung; giới hạn cache để giảm RAM. Không xóa bộ lọc học thuật để tăng tốc.
- Bỏ một lần gọi cổng lọc ngay sau hàm đã kiểm; không nhầm số vị trí gọi hàm với số lần AI. Đo tại máy trước đây cho callback chỉ giảm trung vị khoảng 1,2%, không phải nhanh gấp đôi; chưa có p95/tải lớp học.
- Giọng đọc chung Trạm 1–3, không tải MP3 khi mở trang; nút đọc/chọn chữ/double-click dùng chung luồng Anh–Việt; tránh listener trùng; hiện tên giọng thật. Chưa xác nhận giọng Việt miễn phí đúng Nam Bộ; không hứa thuật ngữ mọi ngành được đọc hoàn hảo.
- Tắt watcher trong bản vận hành để tránh đường gỡ module khi nhiều phiên import. Mỗi lần sửa module cần nạp tiến trình mới và kiểm log; push chưa đồng nghĩa Cloud đã nạp đồng bộ. Không chữa bằng xóa/reload module giữa phiên người dùng.

Chi tiết: [độ trễ](PATCH_REPORT_NAVIGATION_LATENCY_20261025.md), [giọng đọc](PATCH_REPORT_PEDAGOGICAL_SPEECH_20261025.md), [import](PATCH_REPORT_CLOUD_IMPORT_STABILITY_20261025.md), [phát hành](DEPLOYMENT_CHECKLIST.md).

## 5. Bằng chứng đợt kiểm toàn hệ thống hôm nay

1. **65/65 tổ hợp Trạm 1 và 65/65 Trạm 3** qua lượt Streamlit AppTest tại máy. Có sinh bài qua nút với provider giả lập và tạo đề từ kho giả lập, database riêng. Không có lượt Gemini thật trong ma trận này. [Bảng từng tổ hợp](tests/evidence/publication_ui_matrix_20261026.json).
2. Bộ hồi quy trước thay đổi Speaking cuối: **269 ca qua**, cùng ca chấm Anh bổ sung **1 ca qua**. CI của [PR #21](https://github.com/pmtgiaitichk15khkt01-cmd/VIP_DEMO_GSAITHPT2026/pull/21) và main sau merge đạt trên Python 3.10/3.11. Main lúc phát hành #21: `639edeaccb13cc1b6d749b4d1a839f4e415648ad`.
3. Cloud sau #21 có tiến trình mới lúc **14:20:20, 26/10/2026 (Việt Nam)**. Một lượt bài Anh lớp 6 thật sinh đủ ba câu/bốn lựa chọn và hai bộ Pólya tiếng Việt; chính lần này phát hiện nhánh Speaking sai lớp, nên không dùng lần qua ma trận để báo Trạm 1 hoàn hảo.
4. Nhánh Speaking sửa tiếp đã qua **14 ca tập trung**, rồi **34 ca liên quan**, trong đó có giao diện hàm thật của bảy lớp và hồi quy giọng đọc. Trạng thái push/CI/Cloud của nhánh này cập nhật trong biên bản phát hành cuối; không mặc định đã phát hành chỉ từ kiểm thử tại máy.

## 6. Những việc chưa được nghiệm thu

| Hạng mục còn lại | Lý do chưa được gọi là hoàn tất |
|---|---|
| Kiến thức, công thức và mức độ đúng 100% mọi môn/lớp | Chưa có bộ câu chuẩn theo yêu cầu cần đạt cùng kiểm độc lập đủ phạm vi; test kỹ thuật không thay thẩm định môn |
| KNTT/SGV và văn bản hiện hành đầy đủ | Chưa có toàn bộ nguồn chính thức được gắn phiên bản, trang, đính chính và lịch sử hiệu lực; chưa có bảo đảm giám sát cập nhật |
| Lab theo lớp | Cloud cho thấy menu Toán lớp 6 còn gợi ý hàm bậc ba KNTT12. Nhánh mô phỏng cần kiểm riêng; chưa vá trong bản Speaking |
| Mọi lượt AI đều sinh được nội dung đạt | Provider có thể thất bại; còn bản nháp bị giữ sau lượt sửa. JSON dòng 558 chưa có bản thô để kết luận đã tái hiện |
| Phục hồi Ngữ văn hoàn chỉnh | Cần thay đồng bộ ngữ liệu, câu hỏi và rubric; không dùng bộ thay câu trắc nghiệm cho việc này |
| Đề khác thực chất giữa mọi phiên/mọi người | Có fingerprint/cooldown theo phạm vi hiện có; chưa có lịch sử toàn đề bền vững để bảo đảm toàn cục |
| Chi phí và độ trễ thấp nhất | Chưa ghi đủ usage_metadata/token, số request fallback thực, p95 và tải đồng thời; không đưa con số tiền tiết kiệm chưa đo |
| Giọng Nam Bộ chuẩn trên mọi máy | Phụ thuộc giọng thiết bị/dịch vụ và thẩm định vùng giọng; chưa có bằng chứng đầy đủ |

## 7. Đánh giá kỹ thuật và bài học làm việc

Các điểm có bằng chứng: hợp đồng đầu ra, parser thật, bảo toàn nguồn và khóa, kiểm thử âm/dương, lượt sửa hữu hạn, cache có giới hạn, nhật ký lỗi riêng tư và CI trước phát hành. Những điều này là thực hành kỹ thuật có ích, không phải chứng nhận “đẳng cấp BigTech”.

Các lần thay cấu trúc quá rộng trước đây đã gây hồi quy thực tế; nguyên nhân có cả prompt bị rút gọn, thay giao diện khi sửa công thức, và bộ test chưa giữ đầy đủ hợp đồng sản phẩm. Cách ngăn lặp lại: sửa theo lỗi tái lập; ghi rõ phần sẽ đổi; thêm ca bảo vệ giao diện và dữ liệu; kiểm module/CI/Cloud; không báo “xong hết” chỉ từ test xanh; để mục chưa có nguồn đúng trạng thái chưa nghiệm thu.
