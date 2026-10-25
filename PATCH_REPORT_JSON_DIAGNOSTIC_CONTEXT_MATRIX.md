# Chẩn đoán phản hồi đề lỗi và ma trận kiểm thử môn lớp

## Bằng chứng thực tế sau các bản vá trước

Một lượt Trạm 1 trên Cloud đã hiển thị bài khảo sát hàm bậc ba, ba nhóm trắc nghiệm và hai bài tự luận. Lượt đề Trạm 3 đầy đủ 12/4/6 với bốn chủ đề vẫn thất bại đọc JSON ở dòng 117 cột 13. Vì chưa giữ được bản nháp gốc, không được khẳng định bộ phục hồi cú pháp trước đã sửa dứt điểm lỗi thực tế.

## Thay đổi giới hạn trong bản này

Khi đường tạo đề Trạm 3 gặp ValueError liên quan JSON, giữ đúng một bản nháp lỗi trong bộ nhớ phiên, tối đa hai triệu ký tự, kèm môn/lớp/số câu và thông báo lỗi. Che các API key đang cấu hình nếu chuỗi đó xuất hiện trong bản nháp. Không đưa bản nháp vào đề thi, nhật ký đồng bộ, GitHub hoặc dịch vụ bên ngoài. Xóa bản cũ khi bắt đầu yêu cầu tạo đề tiếp theo.

Chỉ sau khi xác thực Trạm 4, quản trị mới có mục tải bản nháp để kiểm tra ở máy. Bản nháp có thể chứa khóa chấm nên không hiển thị cho học sinh hoặc trước xác thực. Đây là công cụ để tái hiện đúng lỗi thay vì liên tục gọi AI và đoán nguyên nhân; nó chưa tự chữa mọi JSON sai.

Sửa trình bày Pólya khi AI đặt câu hỏi ngay trên dòng tiêu đề: không lặp lại tên bước trong thân gợi mở. Loại dấu in đậm còn thừa sau nhãn câu; không đổi nội dung toán hoặc tự tạo lời giải.

## Ma trận 65 ngữ cảnh

Kiểm thử từng tổ hợp môn/lớp app đang hỗ trợ, lớp 6–12: prompt/schema giữ ngữ cảnh, đường tham khảo giữ môn/lớp, vòng đọc JSON không đổi cấu trúc, dữ liệu khai báo nhầm môn hoặc lớp bị từ chối, môn tích hợp THCS không bị đổi thành Vật lý riêng. Đây là kiểm thử phần mềm, không chứng minh kiến thức mọi môn đã đúng CT2018/KNTT.

Danh mục hiện có 105 mục liên kết tham khảo và 15 mục quay về cổng tra cứu. Chưa kiểm tra khả năng truy cập từng URL trong lượt ma trận này; chưa kiểm chứng từng trang SGK. Kết quả AI thực tế mới được quan sát ở Toán 12 trong lượt này: Trạm 1 xuất được bài nhưng chưa thẩm định mọi hướng dẫn; Trạm 3 còn lỗi JSON. Các ngữ cảnh khác không được ghi là đã kiểm chứng đầu ra AI.

Kiểm thử trước phát hành: 236 ca toàn bộ đạt trong 271,005 giây trước bổ sung ca trình bày nhãn bước lặp trong thân câu. Mã cuối đạt 19 kiểm thử tập trung cho ma trận/ngữ liệu trình bày; ca giao diện xác nhận bản nháp lỗi được giữ, API key được che và nút tải chỉ xuất hiện sau đăng nhập quản trị đã đạt. CI chạy toàn bộ mã cuối. Chưa tuyên bố đã sửa xong lỗi JSON từ AI thực tế; mục tiêu của phần chẩn đoán là lấy đúng dữ liệu lỗi để sửa có bằng chứng.
