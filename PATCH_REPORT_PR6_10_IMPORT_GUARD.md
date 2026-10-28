# Khôi phục bảo vệ import production — 28/10/2026

Cloud tiếp tục ghi KeyError services.context_recovery và services.cognitive_levels ngay sau cập nhật. Sau reboot lúc 15:49:49 giờ Việt Nam, log mới vẫn có KeyError services.context_recovery. Chưa chứng minh toàn bộ hiện tượng chậm có cùng nguyên nhân.

Đối chiếu Git xác nhận dac2968 ngày 25/10 đã thêm cấu hình tắt source watcher và kiểm thử import đồng thời; bản phục hồi PR6 0755040 đã xóa cả hai. Khôi phục nguyên hai file đó, không khôi phục các thay đổi giao diện hay bộ lọc khác. Báo cáo gốc PATCH_REPORT_CLOUD_IMPORT_STABILITY_20261025.md trong lịch sử chứa thí nghiệm tái hiện module eviction; đó là bằng chứng cơ chế khả dĩ, không phải truy vết đầy đủ sự cố Cloud này.

## Phạm vi và đánh đổi

- server.fileWatcherType=none, server.runOnSave=false ngăn source watcher gỡ module khi file thay đổi trong tiến trình đang có nhiều phiên.
- Không đổi prompt, nội dung, UI, giọng đọc, bộ nhận ảnh, đáp án hoặc số lượt phục dựng. Không thêm retry/AI call.
- Sau phát hành cần khởi động lại tiến trình để nạp mã đồng bộ. Push đơn thuần không chứng minh runtime đã dùng phiên bản mới.
- Local muốn hot reload có thể chủ động ghi đè --server.fileWatcherType=auto; production không dùng cách đó.
- Không thay fastReruns, bảo vệ mạng, quyền truy cập hoặc cách hiển thị lỗi.

## Kiểm chứng

Hai kiểm thử riêng đạt: cấu hình chọn NoOpPathWatcher thật và tám luồng import dịch vụ nhận đúng ngữ cảnh. Kết quả bộ hồi quy đầy đủ được ghi ở biên bản nghiệm thu sau khi hoàn tất. Chưa nghiệm thu Cloud và chưa chứng nhận mọi môn/lớp.

Lượt đề Cloud 2195 sau reboot vẫn chưa đạt vì p1 câu 3 và p2 câu 1 thiếu hình sau hai lượt phục dựng. Đây là mục độc lập còn mở, không được coi bản vá import sẽ tự giải quyết.

Bộ hồi quy đầy đủ: 229/229 đạt trong 145.804 giây; log PR6_PATCH10_IMPORT_GUARD_FULL_20261028.log ngoài repo. Có cảnh báo ResourceWarning kết nối SQLite chưa đóng trong fixture; chưa coi test xanh là không còn cảnh báo hoặc đã nghiệm thu Cloud.
