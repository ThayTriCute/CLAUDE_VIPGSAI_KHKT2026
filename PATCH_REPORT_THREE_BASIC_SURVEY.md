# Trạm 1: yêu cầu khảo sát cả ba dạng hàm — 27/10/2026

## Vấn đề và bằng chứng
Người dùng báo bài khảo sát ba hàm cơ bản không đạt CT2018/KNTT. Snapshot giữ ngoài Git tại `qa_evidence/tram1_math12_incident_20261027.txt` cho thấy phiên bài học Toán 12 có ba tên dạng, nhưng phần lý thuyết chỉ triển khai một ví dụ phân thức 1/1. Không kết luận từ đó rằng toàn bộ kiến thức trong bài nằm ngoài chương trình. Tên bài đã lưu trong phiên là chủ đề khảo sát tổng quát; không có bằng chứng nguyên văn yêu cầu lúc sinh đã ghi rõ ba dạng. Ca hồi quy dùng yêu cầu ba dạng do người dùng xác nhận sau đó, không giả là tái hiện nguyên prompt cũ.

## Nguồn đã đối chiếu
- CT môn Toán kèm TT32/2018, trang 106 trong bản PDF đã lưu tại máy từ trang trường: ba dạng và điều kiện hệ số. Bản gốc tải trước; lần mở URL bằng web hiện không truy cập được. Chưa kiểm lại toàn bộ lịch sử sửa đổi ở bản vá này.
- Cổng chính thức NXBGD: https://truonghocsoquocgia.nxbgd.vn/book/393beba7-0dc1-45a9-ac53-3254cffa1344/read. Đã mở Bài 4, trang 26–28; sơ đồ khảo sát, mục hàm bậc ba và mục phân thức. Ngày tạo trang 07/07/2025 không phải bằng chứng năm tái bản. Không tuyên bố đã đọc mọi trang hoặc SGV/đính chính mới nhất.

## Nguyên nhân và sửa hẹp
Prompt cũ nêu phạm vi nhưng không yêu cầu đủ ví dụ cho từng dạng khi người dùng chọn cả ba; cửa kiểm chủ yếu bắt bậc 4 và cấu trúc sư phạm. Bổ sung chỉ dẫn riêng vào `lesson_prompt` của T1 khi Toán 12 có yêu cầu khảo sát ba dạng rõ ràng. Không đưa cấu trúc bài học vào prompt thi T3.

Dùng lại parser biểu thức có giới hạn để nhận dạng ví dụ số bậc 3, phân thức 1/1 và 2/1 trong phần lý thuyết. Không tính công thức tham số chung hoặc phân thức rút gọn thành đa thức là ví dụ của dạng phân thức. Giữ các cách ghi tương đương y=f(x)=..., f(x)=..., tfrac, left/right. Nếu thiếu, dùng đúng lượt sửa hữu hạn hiện có; không thêm vòng gọi AI, không tự chèn bài mẫu hoặc sửa đáp án.

## Giới hạn
Kiểm hiện diện ba ví dụ là điều kiện cần, không chứng minh ví dụ đã giải trọn vẹn, BBT/đồ thị đúng, phân loại mức độ đúng hoặc khoa học toàn bài đúng. Không áp quy tắc này cho chủ đề rộng không yêu cầu rõ ba dạng, bài chỉ một dạng, môn khác hoặc lớp khác. Không thay giao diện, infographic, video, radio, Socratic và bốn bước Pólya.

## Kiểm thử
Các ca tập trung đã kiểm bản nháp thiếu dạng, dạng hợp lệ, dạng rút gọn, ký hiệu tương đương, không lan sang ngữ cảnh khác, một lượt sửa thành công/thất bại và tách prompt T3. Hồi quy toàn dự án: 311 ca qua trong 381,566 giây; sau thay đổi tách chỉ dẫn riêng T1, 42 ca tập trung qua trong 10,553 giây. Biên dịch app.py và hai module sửa qua. Chưa nghiệm thu Cloud; bản vá chưa được coi là đã triển khai chỉ từ test xanh.
