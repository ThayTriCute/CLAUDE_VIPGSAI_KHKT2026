# Bản vá khôi phục trải nghiệm Trạm 1 — 25/10/2026

## Nguyên nhân và tác động

Một lần rút gọn prompt đã làm mất ràng buộc ba câu trắc nghiệm và hai bài tự luận theo bốn bước Pólya. Thay đổi cách hiển thị để xử lý công thức chuyển radio đầy đủ thành chữ A–D riêng, làm lệch giao diện đã được người dùng chấp nhận. Phần tự luận hiển thị bản thô nên có thể lộ metadata hoặc lời giải. Các kiểm thử trước tập trung kỹ thuật mà thiếu cam kết chức năng sư phạm và kiểm tra trải nghiệm này.

## Cách vá

Khôi phục radio dọc gắn đầy đủ phương án, giữ nguyên giá trị chấm và trạng thái đã chọn. Công thức hóa học trong nhãn radio được chuyển bằng parser mhchem đóng gói sang TeX tương đương vì radio Streamlit không tự nạp phần mở rộng này.

Prompt và cổng xuất bản yêu cầu đúng ba câu trắc nghiệm, hai bài tự luận, bốn bước Pólya tiếng Việt và gợi mở riêng theo ngữ cảnh. Không mặc định đáp án A khi thiếu khóa. Cắt toàn bộ đuôi metadata riêng tư và chỉ dựng lại nội dung học sinh được phép xem. Bản nháp sai cấu trúc được sửa tối đa một lượt bổ sung; không thêm vòng sửa vô hạn.

Gợi mở Socratic tách khỏi giải thích. Trạm 1 và các vị trí gợi mở trước chấm ở Trạm 3 dùng trường riêng; dữ liệu cũ thiếu gợi mở chỉ gọi AI khi người dùng yêu cầu, có bộ nhớ đệm giới hạn. Không gọi lại chỉ vì mở trang. Bộ lọc chặn một số kiểu lộ đáp án rõ ràng; chưa phải chứng minh ngữ nghĩa tuyệt đối.

Công cụ phục dựng được gọi ngay trong cổng xuất bản Trạm 1. Trường hợp câu hỏi dấu a,d của hàm bậc ba, có điều kiện chữ N đi lên và giao trục tung dương, tạo hàm đại diện x³−3x+1 để vẽ. Bốn tổ hợp dấu được đánh giá độc lập, phải có đúng một phương án phù hợp; không dùng khóa AI để chọn hình. Công thức đại diện không in lên hình làm lộ lời giải. Câu thiếu điều kiện hoặc ngoài phạm vi phục dựng phải bổ sung/biên soạn lại toàn câu thay vì cho qua với cảnh báo thiếu hình. Đây là phục dựng hình phù hợp điều kiện, không khẳng định khôi phục đúng ảnh gốc.

Infographic và liên kết YouTube được giữ. Chữ sổ tay giảm từ 26 xuống 21 px, trọng lượng 500 xuống 400, giảm giãn dòng; tiêu đề đỏ tách dòng, công thức vẫn dùng bộ chữ toán. Kiểu chữ gần tinh thần ảnh mẫu hơn, không cam kết trùng nét chữ viết tay gốc.

## Phạm vi và giới hạn

Giữ các bản vá trước về môn/lớp, xuất bản công thức, điều hướng và import. Không thay cấu hình Cloud trong bản này. Không tuyên bố toàn hệ thống đã hết lỗi, nội dung AI luôn đúng hay đạt chứng nhận Big Tech. Kiểm thử các ngữ cảnh môn/lớp chỉ xác nhận ràng buộc và đường xử lý được giữ, không phải thẩm định kiến thức tất cả môn.

Bản giọng đọc đang phát triển được giữ riêng ở nhánh local codex/unified-pedagogical-speech, commit dbc886a8a8fe831c92c8101ccd7f36629bfe1740; chưa phát hành. Sau bản khôi phục sẽ tiếp tục việc đó theo yêu cầu người dùng.

## Kết quả kiểm thử tại máy phát triển

- 51 kiểm thử tập trung đạt trong 7,823 giây.
- Lượt toàn bộ đầu tiên: 183 ca, một ca điều hướng AppTest vượt hạn 45 giây. Chạy lại riêng ca đó đạt trong 29,210 giây; chạy lại toàn bộ không thay mã đạt 183/183 trong 145,875 giây. Chưa đủ bằng chứng kết luận nguyên nhân lần quá hạn; không che giấu bằng tăng timeout.
- Biên dịch các tệp sửa và kiểm tra whitespace đạt.
- Kiểm tra giao diện cục bộ trước đó đã thấy ba nhóm radio đầy đủ, tám bước Pólya, chú thích hình phục dựng và không thấy metadata riêng tư trong phần học sinh. Kết nối điều khiển trình duyệt hiện báo không gắn được phiên; chưa kiểm chứng lại Cloud sau phát hành trong lần kiểm tra này.
