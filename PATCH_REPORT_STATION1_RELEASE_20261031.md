# Trạm 1: parser, BBT, hướng dẫn và Lab

Giữ bố cục, radio, nút và thư viện mẫu đã có. Bản này sửa các lỗi tái hiện được, không phải chứng nhận nghiệm thu kiến thức mọi môn/lớp.

- MCQ: chỉ đọc Phần 2; không lấy ví dụ lý thuyết/tự luận làm câu trắc nghiệm; không tự gán A khi thiếu khóa; đọc đúng “Chọn B”; giữ khóa theo phương án sau trộn. Câu thiếu khóa được ghi chưa xác định khi chấm, không khóa cả bài học.
- Markdown: bỏ dấu nhấn mạnh đầu câu bị lẻ sau nhãn mức độ, giữ nhấn mạnh cân bằng.
- BBT: khôi phục màu chữ trực tiếp ở các ô trong dark mode, giữ lưới/mũi tên/giới hạn. Không tự vẽ mũi tên lên–xuống nếu không có dấu đạo hàm hoặc hướng được cung cấp; dữ liệu gốc vẫn hiển thị.
- Hướng dẫn: fallback hẹp cho tham số và tính đơn điệu trên toàn R/ℝ/LaTeX; không đưa đáp số. Prompt BBT chỉ áp cho Toán khi đủ dữ kiện; Ngữ văn Pólya yêu cầu HS tự đề xuất luận điểm, không viết sẵn.
- Chốt bài: nhận “không còn thắc mắc”, không chốt khi còn chưa hiểu/câu hỏi mới; chỉ ghi hoàn tất sau phản hồi thành công; reset trạng thái chốt khi đổi bài. Giữ bài học nhân sinh, chỉ gán danh ngôn/tác giả khi bản ghi có nguồn đã xác minh. Không đổi prompt Trạm 2 so với nền phát hành.
- Lab: giữ mẫu và nút; sửa đúng mẫu Tin học “Sơ đồ thuật toán & Cây nhị phân” đang trỏ Oxyz sang sơ đồ cây tìm kiếm và các bước tìm kiếm; preset khác giữ nguyên.
- Ngày áp dụng pháp quy lấy ngày Việt Nam, tách khỏi ngày rà nguồn. Dùng registry hiện có; không tuyên bố tự kiểm định hiệu lực hoặc cập nhật đầy đủ nguồn.

## Kiểm chứng và giới hạn

Worktree phát hành sạch:353/353 kiểm thử qua358.610s, diffcheck đạt. Số này không bao gồm các test corpus/legal-watch thử nghiệm giữ ngoài bản phát hành. Kiểm phạm vi prompt Trạm2 cũng đã qua sau khi khôi phục phần sửa nhầm trước phát hành.

Các ca lỗi có log trước/sau trong qa_evidence của workspace. Đã kiểm thực tế một bài Toán12:3MCQ khóa B/A/B chấm đúng,2tự luận có4bước,BBT đúng dữ liệu nhưng phát hiện hồi quy tương phản đã sửa local. Preview renderer mới đọc rõ, giữ các dạng bảng và không tự thêm hướng thiếu. Đây không thay việc nạp bản cuối trên Streamlit.

Ma trận hỗ trợ có65cặp môn/lớp; chưa nghiệm thu học thuật đủ65cặp. Giọng đọc,Lab toàn bộ,độ trễ,nguồn CT2018/KNTT/pháp quy đầy đủ và Cloud sau triển khai còn phải kiểm. Không xóa cảnh báo chưa thẩm định.

Bản phát hành tách riêng khỏi corpus/evidence/legal-watch thử nghiệm, không thêm thư viện hoặc tăng retry/trần gọi AI. Các hàm BBT/Socratic/nhận ý chốt dùng chung có thể tác động nơi gọi khác; có kiểm hồi quy trong bộ test. Không tuyên bố tuyệt đối không lỗi.

## Bổ sung sau PR62: bảo toàn ranh giới câu và mã HTML

- Chỉ tách nhãn Câu/[Q] ở đầu dòng để không cắt mất dữ kiện khi thân câu nhắc Câu2. Nhãn A) không còn giữ thừa dấu ngoặc; khóa vẫn theo phương án sau trộn.
- Lỗi thực tế Tin học12: cleaner dùng chung xóa p/br/b/i cả trong inline/fenced code. Giữ nguyên vùng code/math quanh bước gỡ HTML; markup trang trí ngoài code vẫn được xử lý. Hàm dùng chung cũng phục vụ câu hỏi Trạm3, có hồi quy chéo; không thay giao diện.
- Test trước sửa tái hiện lỗi; targeted61/61 qua13.386s, full358/358 qua356.966s sau sửaHTML, diffcheck theo CRLF gốc đạt. Bản355 trước đó chưa gồm váHTML, không dùng làm bằng chứng cuối.
- Tin học12 thử thật: có3MCQ và2tựluận×4bước; câu1 chọnhead sai nhận gợiý, chọnbody đúng chấmđúng. Đã quan sát chốt nhân sinh không gán tácgiảthiếunguồn. Gợiý còn quá gần đápán, thẻ trongchat bịđưavàomathmode, câu3 cần rà tínhduynhất khi đủthẻ. Chưa nghiệmthu họcthuật.
- Mã mới chưa xác minh reload runtime tại thời điểm ghi. Ma trận65cặp vẫn0accepted,2livepartial,63chưathửbàithật. Không chứng nhận từfixture. Không tăngretry/capAPI, không thêmdependency; cache/DB/Key không đưa vàoGit.

## Xác minh runtime local sau sửa HTML

Đã khởi lại local8502 đúng mãcf3f26b, Key do người dùng nhập trực tiếp. Một bài Tin học12 mới hiện nguyên vẹn p/br trong lý thuyết, mã mẫu, phương án và Pólya. Có3MCQ×4phươngán và2tựluận×4bước; khóaC/B/D được tự đối chiếu rồi chấmUIđúng3/3. TảiMarkdown vàHTML qua đúng nút app: cả hai giữ p/br và mã mẫu. GợiýQ2 còn dùng từOrder quá gần đápán; giữ mục chấtlượnghướngdẫn mở.

UI đổi ngữ cảnh65/65môn/lớp trênChrome:heading đúng và nútLab hiện,0API; median1881ms,p953048ms,max4112ms tính cảMCP/snapshot. Không suy ra độtrễAI hoặc65bàihọc đạt họcthuật. Mộtbàimới được quan sát AItrảlờiở21s vàdựngđủbàiở49s; đây mốcquan sát,không phảiTTFT chínhxác.
