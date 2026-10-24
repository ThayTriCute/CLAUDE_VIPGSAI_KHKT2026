# Tiêu chí nghiệm thu Trạm 1 và Trạm 3

Chốt theo yêu cầu người dùng ngày 25/10/2026. Đây là tiêu chí và bảng khoảng cách, **không phải giấy chứng nhận sản phẩm đã hoàn hảo**.

| Điều kiện nghiệm thu | Bằng chứng phải có | Trạng thái hiện tại |
|---|---|---|
| Đúng môn, lớp, chủ đề | Ngữ cảnh chọn khớp dữ liệu, nội dung và yêu cầu cần đạt | Chuẩn hóa tên môn/lớp, kiểm tra khai báo và lọc chủ đề đã có; chưa xác minh ngữ nghĩa toàn bộ học liệu |
| Công thức hiển thị được | Chạy parser thật; cùng renderer/phông ở đường hiển thị; kiểm tra desktop/mobile | Bản vá KaTeX bổ sung parser thật, SSR ở nội dung chính và lựa chọn; không đồng nghĩa mọi màn hình/thiết bị được kiểm tra |
| Công thức đúng khoa học | Giả thiết, miền xác định, đơn vị, định luật, lời giải và đáp án được đối chiếu | Mới có một số kiểm chứng Toán, chưa có bộ kiểm độc lập đầy đủ cho mọi môn |
| Mức độ đúng | Yêu cầu cần đạt, nhiệm vụ tư duy, lời giải và đánh giá giáo viên; từng ý Đ/S riêng | Bỏ gán nhãn theo phần/độ dài; căn cứ AI tự khai vẫn cần duyệt |
| Đúng KNTT/CT2018 | Nguồn chương trình theo lớp, phiên bản sách, trang/bài và đính chính | Chưa có kho đối chiếu đã duyệt cho toàn bộ cặp môn/lớp; link sách không chứng minh nội dung đã được tra cứu |
| Đúng tùy biến | Hợp đồng cấu trúc và nội dung; số câu/điểm/chủ đề/mức độ được kiểm tra riêng | Kiểm tra được một phần cấu trúc và ngữ cảnh; tùy biến ngôn ngữ tự nhiên chưa được kiểm chứng đầy đủ từng điều kiện |
| Đúng văn bản hiện hành | Danh mục nguồn, phạm vi và ngày hiệu lực được đối chiếu theo thời điểm | Registry là ảnh chụp kiểm tra có ngày; không phải giám sát tự động mọi văn bản. TT89/2026 chưa áp trước 01/12/2026 |
| Không tự bịa để đủ dữ liệu | Nguồn gốc rõ, phục hồi có giới hạn, lỗi không bị biến thành A/Đúng/0/hình mẫu | Đã bỏ nhiều đường đoán; chưa thể tuyên bố không còn mọi đường cũ cần rà soát |
| Không hiển thị trống hoặc sai âm thầm | Phân biệt đang xử lý / bản nháp chưa đạt / thành công; có đường thử lại | Công thức lỗi được giữ lại, báo trạng thái; không đảm bảo luôn tạo được học liệu đạt yêu cầu |

## Nguyên tắc xử lý mâu thuẫn

Không thể đồng thời cam kết “luôn có nội dung”, “mọi tùy biến đều được đáp ứng” và “đúng tuyệt đối” khi thiếu dữ kiện, nguồn hoặc yêu cầu mâu thuẫn chương trình. Ưu tiên không công bố kết quả sai: phục hồi giới hạn, nếu chưa đạt thì báo trạng thái và giữ bản nháp. Không bịa dữ kiện, hình, trích dẫn hoặc đổi nhãn mức độ để lấp khoảng trống. Các yêu cầu tùy biến phải nằm trong môn/lớp và khung học thuật đã chọn.

## Công việc còn thiếu để nghiệm thu học thuật

1. Tạo kho yêu cầu cần đạt và mục lục/trang/đính chính KNTT theo từng môn/lớp, có phiên bản và nguồn chính thức; đối chiếu hướng dẫn An Giang/nhà trường cho ma trận kiểm tra.
2. Chuẩn hóa tùy biến thành hợp đồng có thể kiểm tra: số câu, điểm, chủ đề, mức độ, hình/bảng và phạm vi kiến thức. Khi không đáp ứng phải báo mục nào chưa đạt, không đổi nhãn cho vừa ma trận.
3. Thẩm định bộ câu chuẩn theo môn/lớp bằng giáo viên; kiểm tra độc lập lời giải và đáp án, theo từng nhánh khoa học. Không dùng AI tự chấm mình làm bằng chứng duy nhất.
4. Có luồng duyệt gắn phiên bản nội dung và tài khoản giáo viên. Hiện chưa có luồng xuất bản “chỉ học liệu được duyệt” hoàn chỉnh; dữ liệu AI vẫn được đánh dấu chưa thẩm định.
5. Kiểm thử trực quan, tải đồng thời, thiết bị và sai lỗi trên tập giữ riêng; ghi nhận lỗi thực tế. Không gọi một lượt test xanh là chứng minh không còn lỗi.

Chỉ đổi trạng thái nghiệm thu từng điều kiện khi có bằng chứng tương ứng. Bảng này không thay thế thẩm định chuyên môn hoặc quy định pháp luật.
