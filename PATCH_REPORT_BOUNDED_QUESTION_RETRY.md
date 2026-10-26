# Phục hồi câu chưa đạt bằng lượt sửa có phản hồi

## Nguyên nhân có bằng chứng

Bản nháp Cloud Toán 12 gồm 12/4/6 câu tải ngày 26/10/2026 có JSON đọc được nhưng câu Đúng/Sai đầu tiên tham chiếu đồ thị thiếu hình. Một lượt AI thay câu chưa đạt; cơ chế cũ chuyển ngay câu đó sang cần kiểm tra dù ngân sách toàn đề vẫn còn. Phản hồi thay câu còn dùng json.loads riêng, khác bộ đọc JSON/LaTeX của đề chính. Ngoại lệ bị bỏ qua nên không có dấu vết phân biệt dữ liệu bị từ chối với dịch vụ không đáp ứng.

## Bản sửa giới hạn

Giữ cách tìm dữ liệu/câu cùng ngữ cảnh từ ngân hàng trước. Nếu còn lỗi, thử thay nguyên câu bằng AI, kiểm tra lại môn/lớp/chủ đề/mức độ khai báo, dữ liệu hình, cấu trúc, công thức và kiểm chứng toán trong phạm vi đang hỗ trợ. Nếu bản thay chưa đạt, gửi mã lý do vào lượt tiếp theo. Tổng ngân sách app vẫn hai lượt AI cho toàn đề, không phải hai lượt cho mỗi câu. Câu đã đạt không sinh lại. Lỗi dịch vụ sau cơ chế fallback sẵn có không bị thử lặp lại cho cùng câu trong vòng mới.

Phản hồi thay câu dùng safe_json_loads chung để giữ LaTeX và phục hồi cú pháp trong giới hạn hiện có. Lưu dấu vết accepted/rejected/unavailable; không chép lỗi nhà cung cấp có thể chứa key vào dấu vết. Không đổi giao diện, radio, Socratic, infographic, giọng đọc hoặc số lần AI khi mở trạm/bấm đáp án. Chưa thay cơ chế Trạm 1 trong bản này.

## Kiểm thử và giới hạn

71 ca tập trung đạt trong 7,180 giây. Chạy lại toàn bộ bản nháp Cloud tại máy, dùng ngân hàng hiện có và provider mô phỏng: câu P.I được thay từ ngân hàng; câu P.II bị từ chối lượt đầu vì thiếu hình, lượt sau có công thức số rõ ràng và được phục dựng/kiểm tra; giữ đủ 12/4/6 và không sửa dữ liệu đầu vào. Đây là tái hiện có kiểm soát, không phải kết quả AI thật trên Cloud sau vá.

Ma trận kiểm thử giữ ngữ cảnh cho 58 tổ hợp môn/lớp dùng luồng thay câu trắc nghiệm; bảy tổ hợp Ngữ văn giữ nguyên đoạn đọc/câu hỏi/đề viết và không gọi bộ thay từng câu này. Ngữ văn cần cơ chế sửa đồng bộ ngữ liệu–câu hỏi–hướng dẫn chấm riêng. Không được diễn giải kiểm thử cấu trúc này thành chứng nhận học thuật 65 ngữ cảnh.

Hết ngân sách mà vẫn chưa đạt thì chưa xuất đề đó. Bản này không đảm bảo mọi bản sinh sẽ đạt sau hai lượt, không tự chứng minh mọi đáp án khoa học đúng và chưa tái hiện được JSON dòng 558/cột 51 trong ảnh cũ. Những giới hạn đó cần tiếp tục được kiểm tra trong đợt rà soát tổng thể; không nới bộ lọc để giấu lỗi.

## Chi phí và kiểm thử mã cuối

Chỉ gửi câu lỗi. Với mệnh đề Đúng/Sai, bỏ thuyết minh mức độ/chuỗi bước nhận thức khỏi dữ liệu gửi sửa, giữ nguyên nội dung và khóa chấm. Trên câu Cloud đã tải, đoạn dữ liệu nguồn giảm từ 1.648 xuống 554 ký tự (66,4%); đây không phải số token tính phí hay tỷ lệ giảm toàn prompt. Không có lời gọi Gemini thật trong lượt triển khai mã này; kiểm thử dùng provider mô phỏng. Hai lượt là ngân sách gọi hàm sinh sửa của toàn đề; cơ chế fallback nhà cung cấp vẫn có những lần thử kết nối riêng và thời hạn sẵn có.

Toàn bộ 242 kiểm thử đạt trong 286,992 giây trước tinh chỉnh dữ liệu prompt cuối. Mã cuối đạt 72 ca tập trung trong 7,289 giây; ca giao diện retry đạt trong 31,283 giây, xác nhận một lượt sinh và hai lượt sửa rồi mới mở bài. Dữ liệu kiểm thử cũ có hai phương án trùng đã được đổi thành bốn phương án khác nhau với khóa đúng. CI chạy toàn bộ mã cuối trước hợp nhất. Chưa xác minh bằng một lượt sinh Gemini thật trên Cloud sau vá; không được báo đã hoàn thiện toàn hệ thống.
