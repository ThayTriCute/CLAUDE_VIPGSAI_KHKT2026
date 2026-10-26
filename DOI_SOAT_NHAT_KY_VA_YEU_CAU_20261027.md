# Đối soát nhật ký và yêu cầu ngày 27/10/2026

## Căn cứ và trạng thái
Đã đọc bản checklist người dùng gửi trong tệp đính kèm, đối chiếu báo cáo bản vá và lịch sử Git. Đây là đối soát hồ sơ và bằng chứng hiện có, không phải xác nhận đã đọc lại từng dòng toàn hệ thống hoặc nghiệm thu mọi kiến thức.

GitHub main hiện ở a7ef9d1, đã hoàn tác PR29; cây mã tương đương 9026d96 trước PR29. Nhánh sửa Socratic đang ở 37d6100, chưa nhập main. Các PR30 và PR31 cũng chưa triển khai. Không được hiểu mã trên nhánh kiểm thử là mã Cloud hiện hành.

## Những sai sót được nhật ký xác nhận

1. PATCH_REPORT_STATION1_RESTORATION_20261025.md ghi rõ lần rút gọn prompt làm mất ràng buộc ba trắc nghiệm và hai tự luận; thay cách hiển thị công thức làm lệch radio đã được chấp nhận. Đây là thay đổi vượt nhu cầu sửa ban đầu; kiểm thử thiếu hợp đồng sư phạm đã không ngăn được hồi quy.
2. PATCH_REPORT_LESSON_PUBLICATION_20261025.md xác nhận bộ dò hình bắt nhầm yêu cầu học sinh tự lập BBT thành thiếu bảng đầu vào; nhãn Markdown và số dấu hỏi cũng bị kiểm quá cứng. Lời nhắc sửa cấu trúc còn mâu thuẫn với quyền biên soạn lại toàn câu.
3. PATCH_REPORT_SOCRATIC_BOUNDARIES.md tái hiện regex bắt tiền tố y=2 trong y=2x+b thành kết quả tính hộ; chặn mọi chữ “đáp án” hoặc solution cũng quá rộng. Chưa có nguyên văn bản nháp của đúng phiên lỗi trong ảnh, nên chưa kết luận đây là nguyên nhân duy nhất của phiên đó.
4. PR29 buộc ví dụ số cho yêu cầu ba dạng khảo sát là điều kiện bổ sung quá hẹp so với quyền trình bày lý thuyết của Trạm 1. Đã hoàn tác; không đưa trở lại qua bản vá khác.
5. PATCH_REPORT_REUSE_EXISTING_BBT.md thừa nhận PR26 tạo renderer song song dù dự án có công cụ phù hợp. PR27 đã nối lại công cụ cũ. Không xây lại bộ vẽ chỉ vì đường gọi chưa đúng.
6. PATCH_REPORT_LESSON_PUBLICATION_20261025.md thừa nhận báo hoàn thành trước khi kiểm sinh bài thật trên Cloud là quá sớm. Các số test xanh chỉ có giá trị trong phạm vi ca thử.

Các lỗi này thuộc triển khai và quy trình kiểm chứng. Không quy trách nhiệm cho việc người dùng yêu cầu đúng khoa học, đúng chương trình hoặc phân biệt giải thích với Socratic.

## Hợp đồng phải bảo toàn

- Trạm 1: lý thuyết được có diễn giải, công thức tổng quát, ví dụ và tính toán khi phù hợp; không bắt mọi bài phải có ví dụ số.
- Đúng ba câu trắc nghiệm, đủ phương án A–D/radio, gợi mở Socratic theo từng câu, nhãn mức độ là đề xuất khi chưa thẩm định.
- Đúng hai bài tự luận, mỗi bài đủ bốn bước Pólya bằng tiếng Việt; hướng dẫn không giải hộ hoặc tiết lộ đáp án.
- Giữ infographic, phong cách sổ tay, xuất bài và link YouTube; giữ giọng đọc và thao tác chọn chữ trong phạm vi tính năng hiện có, không coi chúng đã được nghiệm thu âm thanh.
- Trạm 3 giữ các chế độ kho/nguyên đề/upload/quét link, một nút tạo đề luyện tập, tùy chọn cho phép AI, ma trận, chấm, lưu và xuất.
- Câu chưa đạt đi qua sửa có giới hạn và kiểm lại; không lặp vô hạn, không công bố sai để tránh thông báo lỗi.

## Bằng chứng mới tại máy

Tệp qa_evidence/station13_socratic_matrix_20261027.json nằm ngoài repository mã sản phẩm ghi 65/65 tổ hợp qua cả Trạm 1 và Trạm 3; 0 lỗi ghi nhận; tổng thời gian 439,21 giây; 0 lượt AI thật. Kiểm thêm phân tách giải thích riêng tư khỏi Socratic trước chấm và các phần p1/p2/p3, riêng Ngữ văn theo đọc hiểu/viết.

Đây là Streamlit AppTest với dữ liệu giả lập và dữ liệu nghiên cứu cách ly. Không phải kiểm chất lượng tri thức AI, DOM KaTeX trên mọi thiết bị, tiếng phát thật hoặc độ trễ Cloud. Không lấy thời gian toàn bộ bộ kiểm thử làm độ trễ người dùng.

Đã quan sát lại mở Trạm 1 và chuyển sang Trạm 3 ở URL Cloud gốc; ảnh cloud_recovered_t3_20261027.png lưu ngoài repository. Chỉ chứng minh mở/chuyển trạm ở lần quan sát, chưa nghiệm thu sinh đề sau bản Socratic chưa triển khai.

## Thứ tự công việc còn lại

1. Giữ bản sửa Socratic hẹp, hoàn thiện hồ sơ và kiểm CI ở đúng commit cuối; không gộp PR29/30/31 vào cùng lần phát hành.
2. Sau kiểm tại máy mới phát hành bản cần thiết; kiểm lại Cloud bằng ca thật có mục tiêu và ghi commit/nguồn/phạm vi. Không chạy AI hàng loạt chỉ để tăng số ca.
3. Ưu tiên Trạm 3 tạo đề theo tùy chọn, giữ đủ tính năng; khi lỗi phải dựa vào bản nháp chẩn đoán riêng, không thêm lệnh cấm theo phỏng đoán.
4. Còn thiếu bản đồ nguồn yêu cầu cần đạt/SGK/SGV có phiên bản, hiệu lực văn bản, kiểm học thuật và mức độ toàn bộ môn/lớp; giữ cảnh báo xác minh đúng phạm vi.
5. Giọng đọc thật cả ba đường, Nam Bộ/nhân bản, phạm vi Lab, chống trùng giữa phiên, token vật lý và tải Cloud vẫn chưa được phép ghi hoàn tất.

Không sửa mã sản phẩm, không merge và không triển khai trong lần lập đối soát này. Script kiểm UI hiện có thay đổi chưa commit; cache đề không đưa lên GitHub.

## Danh mục nhật ký đối chiếu
- PATCH_REPORT_ACADEMIC_SCOPE_20261026.md
- PATCH_REPORT_ALL_CONTEXT_PUBLICATION.md
- PATCH_REPORT_BANK_ORIGIN_AND_AUTHORED_EXAMPLES.md
- PATCH_REPORT_BOUNDED_QUESTION_RETRY.md
- PATCH_REPORT_CLOUD_IMPORT_STABILITY_20261025.md
- PATCH_REPORT_COGNITIVE_LEVELS_20261024.md
- PATCH_REPORT_CURRICULUM_RECONSTRUCTION_20261024.md
- PATCH_REPORT_ENGLISH_SPEAKING_GRADE.md
- PATCH_REPORT_EXAM_CATALOG_PROVENANCE.md
- PATCH_REPORT_EXAM_VALIDATION_DIAGNOSTICS.md
- PATCH_REPORT_JSON_DIAGNOSTIC_CONTEXT_MATRIX.md
- PATCH_REPORT_LATENCY_AND_TOPIC_CONFLICT_20261026.md
- PATCH_REPORT_LESSON_PUBLICATION_20261025.md
- PATCH_REPORT_MATH_PUBLICATION_20261025.md
- PATCH_REPORT_NAVIGATION_LATENCY_20261025.md
- PATCH_REPORT_NOTEBOOK_INFOGRAPHIC_20261024.md
- PATCH_REPORT_PEDAGOGICAL_SPEECH_20261025.md
- PATCH_REPORT_PRIVATE_LESSON_DIAGNOSTICS.md
- PATCH_REPORT_REUSE_EXISTING_BBT.md
- PATCH_REPORT_SHORT_ANSWER_EXTREMA.md
- PATCH_REPORT_SINGLE_PRACTICE_BUTTON.md
- PATCH_REPORT_SOCRATIC_BOUNDARIES.md
- PATCH_REPORT_STATION1_RESTORATION_20261025.md
- PATCH_REPORT_STATION3_BBT_DISPLAY.md
- PATCH_REPORT_STATION3_JSON.md
- PATCH_REPORT_STATION3_WEB_GENERATION.md
- PATCH_REPORT_SUBJECT_EXPORTS_20261024.md
- BAO_CAO_TONG_HOP_TRAM_1_TRAM_3_20261026.md
- YEU_CAU_VA_CHECKLIST_NGHIEM_THU.md
- DEPLOYMENT_CHECKLIST.md

Các báo cáo PR29/30/31 và lịch sử hoàn tác phải đọc theo nhánh tương ứng; chúng không chứng minh tính năng đã có trong main.
