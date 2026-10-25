# Đối soát phạm vi ngữ liệu trước khi xuất Trạm 1 và Trạm 3

## Vấn đề

Người dùng phản ánh bài chọn khảo sát hàm bậc ba lại sinh hàm bậc bốn. Prompt nhắc CT 2018/KNTT không đủ để ngăn việc lệch phạm vi. Cổng cuối trước đây kiểm tra môn/lớp khai báo, cú pháp công thức và một số mâu thuẫn cụ thể, chưa có quy tắc xác định cho trường hợp này.

## Căn cứ và phạm vi quy tắc

Đã đọc trang 106 của Chương trình môn Toán ban hành kèm TT 32/2018/TT-BGDĐT. Phần khảo sát và vẽ đồ thị cơ bản lớp 12 nêu ba dạng: bậc ba, phân thức bậc nhất/bậc nhất và bậc hai/bậc nhất, với điều kiện hệ số. Bản văn bản do Bộ ban hành, lưu tại trường:
https://fileth.hcm.shieldix.app/data/hcmedu/thlevanthogv/attachments/2020_5/3cttoan18201918_295202014.pdf

Đây không phải căn cứ để cấm mọi biểu thức bậc bốn trong mọi bài Toán 12. Nguyên hàm/tích phân, hàm phụ, phương án nhiễu và bài khảo sát riêng được phân biệt. Chưa có nội dung SGK KNTT gốc được kiểm tra từng trang trong lần vá này nên không gắn nhãn đã xác minh toàn bộ sách.

## Đường xử lý

- Đưa hướng dẫn phạm vi có nguồn vào prompt tương ứng, không chèn quy tắc Toán vào môn khác.
- Trạm 1: kiểm tra phần lý thuyết, đề câu hỏi và đề tự luận trước công bố; tách phương án nhiễu khỏi đối tượng khảo sát. Nếu phát hiện hàm bậc từ bốn lệch bài khảo sát đã chọn, dùng đúng lượt sửa bổ sung sẵn có để biên soạn lại, không thay lẻ số mũ/đáp án.
- Trạm 3: thêm kiểm tra phạm vi vào luồng đối soát/thay thế toàn câu hiện có. Câu thay phải qua kiểm tra môn/lớp/chủ đề, mức độ khai báo, dữ kiện và khóa chấm hiện có. Dùng chung ngân sách tối đa hai lời gọi thay thế hiện hữu, không thêm vòng lặp. Cổng xuất cuối kiểm tra lại độc lập; chưa sửa hết thì không mở đề sai.
- Đề nhiều chủ đề dùng chủ đề đã khai báo của từng câu khi khớp danh sách chọn, để phần tích phân không bị áp quy tắc khảo sát một cách máy móc.
- Đổi ví dụ gợi ý nhập tùy biến cũ từng đề xuất khảo sát trùng phương sang dạng phân thức phù hợp phạm vi. Giữ nguyên bố trí giao diện.
- Ngày xét hiệu lực văn bản dùng ngày hiện tại theo múi giờ Việt Nam; ngày đối chiếu nguồn vẫn giữ riêng, không đổi thành ngày mới nếu chưa rà soát lại văn bản. Danh mục lưu trong dự án cần tiếp tục được cập nhật, không phải dịch vụ tự xác minh mọi văn bản mới.

## Giới hạn thực tế

Quy tắc hiện thực là phát hiện một số định nghĩa hàm bậc cao tường minh trong phạm vi khảo sát Toán 12, không phải chứng minh ngữ nghĩa của mọi biểu thức và mọi môn. Những quy tắc chưa có nguồn/kiểm thử không được coi là đã thẩm định. Bộ lọc cuối và AI sửa bài không bảo đảm tuyệt đối mọi kiến thức, mức độ hay đáp án đều đúng. Không lấy tên Bộ/KNTT hoặc số ca kiểm thử phần mềm làm chứng nhận học thuật.

## Kiểm thử

226 kiểm thử toàn bộ đạt trong 394,039 giây trước tinh chỉnh ngày hiệu lực. Các ca riêng kiểm tra hàm bậc bốn trong bài khảo sát, nguyên hàm hợp lệ, hàm phụ, hủy số hạng, phương án nhiễu, nhiều môn/nhiều chủ đề, thay toàn câu không sửa đầu vào và cổng cuối độc lập. Kiểm tra ngày hiệu lực được bổ sung riêng, đồng thời CI chạy lại toàn bộ mã cuối.
