# Giữ nguồn gốc ngân hàng và kiểm tra câu mẫu

## Nguyên nhân tác động chung

Rà đường dữ liệu trước khi đổi nút sang ưu tiên kho cho thấy ingest_ai_generated_exam_to_bank gắn is_real_bank_question=True cho đề AI; get_baseline_questions_pool tiếp tục gắn mọi câu đọc từ kho thành câu thật và is_ai_generated=False. Vì vậy nguồn AI có thể mất nhãn khi quay lại ngân hàng. Đây là lỗi metadata áp dụng chung các môn/lớp, không phải một lỗi riêng Toán.

## Sửa và giữ chức năng

Giữ chức năng tích lũy và tái sử dụng ngữ liệu. Đề AI mới và cache AI cũ giữ is_ai_generated/is_ai_harvested, không thành nguyên đề thật. Pool giữ các cờ này ở từng câu và ghi nguồn AI rõ ràng; đề trộn có AI/câu mẫu ghi nguồn mixed_bank thay vì nguyên đề thật. Danh sách chế độ nguyên đề thật loại các bản có nhãn AI/câu mẫu, trong khi kho luyện tập vẫn giữ chúng. Không xóa dữ liệu cache người dùng hoặc suy ra đã kiểm chứng kiến thức chỉ từ nguồn.

Các câu được dựng trực tiếp trong mã không có bằng chứng đề gốc trong hàm: public builder nay ghi là câu mẫu biên soạn, bỏ tên trường/cổng/năm chưa được đối chiếu, giới hạn đúng Toán 12. Không mang mẫu này sang 64 ngữ cảnh còn lại. Chỉ chuẩn hóa dấu xuống dòng hàng bảng biến thiên, giữ nguyên lệnh \nearrow trong công thức.

## Sai sót khoa học tái hiện được trong mẫu

Mẫu đọc đồ thị f'(x)=x³−4x²−x+4 có các nghiệm −1,1,4. Trên (1,4), đạo hàm âm; x=1 là hoành độ cực đại. Ba khóa Đúng/Sai trước đó mâu thuẫn với dấu này và giá trị nguyên hàm trên đoạn; sửa theo phép kiểm tra độc lập bằng SymPy, không ép riêng một phương án trắc nghiệm. Mẫu phân thức (x²−3x+6)/(x−1) có cực tiểu nhánh phải tại (3,3), không phải (2,4); sửa chi tiết giải thích, giữ câu, mô hình và phương án đúng đã đối chiếu độc lập.

## Kiểm thử và giới hạn

62 ca tập trung đạt trong 9,398 giây trước tinh chỉnh nhãn trường nguồn của bảng audit. Bao gồm nguồn AI qua ingest/cache/pool, kiểm tra 65 tổ hợp không mất ngữ cảnh hoặc đổi AI thành câu thật; đề trộn không tự nhận nguyên đề thật; mẫu Toán không đi sang môn/lớp khác; dấu xuống dòng bảng không phá lệnh LaTeX; tính đạo hàm/nguyên hàm và đối chiếu cả bốn phương án mẫu phân thức. Kiểm thử dùng tệp tạm và provider giả, không gọi API thật. Toàn bộ mã cuối được chạy kiểm thử lại trước push và CI trước hợp nhất.

Toàn bộ 254 ca tại máy đạt trong 319,941 giây trước tinh chỉnh cuối cho hình dạng phản hồi thay câu. Phản hồi AI là array hoặc replacement_question không phải object trước đây bị gộp vào unavailable và bỏ lượt sửa; nay nhận diện là dữ liệu chưa đạt và thử lại trong ngân sách cũ. Với ngoại lệ khác, ghi giai đoạn provider/decode/recover/validate và tên loại ngoại lệ, không ghi nội dung lỗi có thể chứa key. 36 ca tập trung cuối đạt trong 4,400 giây, bao gồm hai hồi quy mới cho hình dạng phản hồi và dấu vết không lộ bí mật. CI kiểm tra toàn bộ mã cuối trước hợp nhất.

Chưa thẩm định mọi câu trong kho hoặc mọi trang SGK. Các phép tính trên chỉ xác minh những phát biểu được nêu, không chứng nhận toàn bộ môn Toán hay các môn khác. Lỗi phục hồi unavailable và bản nháp AI có câu nhiều đáp án vẫn là mục điều tra riêng; không được báo hết lỗi nhờ đổi nhãn nguồn.
