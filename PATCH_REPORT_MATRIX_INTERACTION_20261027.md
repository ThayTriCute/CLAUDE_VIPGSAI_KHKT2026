# Bản vá tương tác ma trận Trạm 3 — 27/10/2026

## Phạm vi
Dựa trên main a7ef9d1, không gộp các PR29–32. Chỉ thay cách xử lý sự kiện của hai ô ma trận hiện có và nút xác nhận; không đổi nhãn, bố cục, chế độ kho/upload/quét link, giọng đọc, infographic, hợp đồng bài học hoặc bộ lọc học thuật.

## Bằng chứng trước sửa
- Đọc lại PATCH_REPORT_NAVIGATION_LATENCY_20261025.md: các nút chuyển trạm đã dùng callback. Không làm lại bản tối ưu đó.
- Ba lần bấm xác nhận trong AppTest đều thực thi app hai lần, thời gian 1,1046 / 1,1475 / 1,1945 giây. Không có AI. Đây là đo tại máy, không phải Cloud.
- Cả ba lượt nhập yêu cầu ở ô học sinh rồi xác nhận đều kết thúc với custom_matrix_prompt rỗng: tab giáo viên vẫn chạy và ghi đè giá trị cũ. Đây là mất yêu cầu tùy biến, độc lập với chất lượng phản hồi AI.
- Profiling trong luồng chạy script: lần đầu mở Trạm 3 có chi phí nạp shard môn học lớn; lần mở nóng thấp hơn. Profiling làm tăng chi phí đo, không lấy 8,556 giây khi gắn profiler làm độ trễ thực tế của Cloud. Bản này không đổi cấu trúc kho vì cần kiểm chứng bộ nhớ và mọi chế độ trước khi sửa rộng.

## Cách sửa
Nút xác nhận dùng callback trước lượt dựng trang, bỏ st.rerun bổ sung. Cả hai ô dùng cùng callback, ghi yêu cầu chuẩn hóa vào trạng thái dùng chung và đồng bộ ô còn lại trước khi widget được dựng. Ô giáo viên không tự ghi đè yêu cầu mới từ ô học sinh bằng giá trị cũ nữa. Cho phép xóa yêu cầu về rỗng và chuyển quyền nhập theo ô vừa chỉnh.

## Được, mất và đánh đổi
- Được: một lượt dựng trang cho xác nhận; yêu cầu nhập từ hai tab nhất quán; không tăng lượt AI.
- Không cắt tính năng hoặc thay thành phần giao diện trong diff sản phẩm. Hai ô vẫn có mặt. Hành vi đồng bộ là chủ đích vì chúng đã dùng chung custom_matrix_prompt; không còn hai bản nháp độc lập ngầm ghi đè nhau.
- Không giảm chi phí tải shard lần đầu, không giảm thời gian chờ Gemini, không sửa lỗi Socratic bắt nhầm của bản nền trong cùng bản vá.
- Các số đo phải ghi rõ mock/provider, cache, môi trường; kiểm UI không thay kiểm học thuật.

## Nghiệm thu
ĐANG THỰC HIỆN. Kiểm riêng callback đã qua: nhập từ học sinh, nhập từ giáo viên, xóa yêu cầu, giữ giá trị ở cả hai ô, đúng một lượt app, không gọi AI. Ma trận 65 môn/lớp mở rộng chuỗi 1→2→3→4→1, chọn trắc nghiệm T1 và giữ lựa chọn, xác nhận/đồng bộ ma trận hai chiều T3, sinh bài/đề bằng provider/kho giả, giữ 3 MCQ, 2×4 Pólya, infographic và link YouTube. Chưa được ghi hoàn tất trước khi ma trận và hồi quy đạt.

Bằng chứng nằm tại F:/FINAL KHKT 2026/qa_evidence/: confirm_latency_before_20261027.json, interaction_profile_worker_20261027.log, interaction_all_contexts_after_20261027.json. Kết nối Chrome bị mất ở lần kiểm mới; chưa có benchmark trình duyệt/Cloud sau sửa.
