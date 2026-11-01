# Trạm 1: tọa độ chính xác, nhãn đồ thị và ngữ cảnh môn học

## Vấn đề và thay đổi

Đồ thị trước đây đổi tọa độ vô tỉ thành số gần đúng ba chữ số thập phân. Bản này giữ căn thức/phân số chính xác. Khi nghiệm bậc ba không có biểu thức ngắn, ký hiệu α theo thứ tự nghiệm thực được định nghĩa bằng phương trình ngay trong hình; không in CRootOf hoặc số gần đúng.

Giữ giao Ox/Oy, cực trị và tâm I; các điểm cực trị/tâm có hình chiếu hai trục. Điểm nằm trên trục có hình chiếu trùng điểm. Ưu tiên nhãn tọa độ cần thiết, bỏ tick phụ gây chật; đặt chú thích ở vị trí tránh trục, điểm, đường cong, nét dóng và nhãn khác. Nhãn dài có chú giải. Cùng bộ dựng phục vụ bài học và cả ba kiểu HTML/infographic; không thêm TeX server hoặc lượt AI.

Marker phiên bản đồng bộ bộ dựng, policy và nguồn khi worker giữ module cũ. Chỉ nạp lại các service đã đổi khi marker lệch; bản hiện tại không nạp lại mỗi lần render. Section infographic cũ dùng số gần đúng được thay đúng một lần. Không đổi cấu hình watcher hoặc yêu cầu reboot Cloud.

Prompt Toán yêu cầu cùng quy tắc chính xác. Prompt Ngữ văn phân biệt đọc/viết, tự sự/nghị luận; không buộc mọi tiết viết cả bài văn hoặc lập luận điểm. Chỉ dẫn HTML chỉ áp cho chủ đề Tin học liên quan HTML/CSS/web.

Thông báo NXBGD ngày 29/04/2026 về SGK chỉnh sửa được đưa vào ngữ cảnh và khối nguồn sẵn có của đúng 7 cặp đang hỗ trợ: LS&ĐL 6–9, Lịch sử 10, GDKT&PL 10, Địa lí 12. Liên kết sách chưa được biến thành xác nhận đã đọc bản chỉnh sửa. Theo Điều 2 bản ký QĐ3588, sửa ngày hiệu lực từ ngày ban hành 26/12/2025 sang 01/01/2026; giữ riêng ngày ban hành và nguồn đối chiếu.

## Kiểm local

- Tái hiện trước sửa: test tọa độ chính xác thất bại 4 subcase; prompt Văn/Tin thất bại 4 subcase. Log tại qa_evidence.
- Nhóm renderer/export/policy/nguồn: 62/62, 14.316s. Sau điều chỉnh cuối tránh đường cong: renderer/export 15/15, 9.921s.
- Sau migration module và section cũ: 65/65, 16.907s, T1_EXACT_RUNTIME_TARGETED_20261101.log.
- Chrome: 30 ca (24 cấu hình giao trục cộng 6 ca vô tỉ/điểm gần nhau), đều ready=true/errors=0; không nhãn gần đúng, mỗi điểm có chú thích, không cặp nhãn getBBox chồng nhau hoặc nhãn đè điểm lấy mẫu đường cong. Đây kiểm tập ca xác định, không bảo đảm hình học cho mọi hệ số có thể nhập.
- 65 ngữ cảnh nguồn/prompt không API đạt, đúng 7 thông báo bản sách; đây kiểm ngữ cảnh/tra cứu, không phải 65 bài học được thẩm định.
- Full hồi quy bản cuối: **380/380 trong 268.941s**, exit 0; T1_EXACT_RUNTIME_FINAL_FULL_20261101.log. Full 377 trước đó không đại diện cho migration cuối.
- Phát lại phần lý thuyết bài cubic thật đã tải từ local qua entry app hiện tại tại 8505, không gọi AI/không chuyển khóa: main và infographic revision 2026110102, 2 SVG hình trực tiếp, 6 điểm, 3 gióng, không gần đúng, iframe ready=true/errors=0, không exception. HTML tải thật đã kiểm marker/2 hình/chú giải nghiệm: T1_EXACT_LOCAL_RUNTIME_EXPORT_20261101.html. Icon SVG của liên kết tiêu đề không tính là hình toán. Đây kiểm phần bài/infographic, không kiểm lại MCQ/chốt/giọng đọc.

## Giới hạn còn mở

Chưa nghiệm thu kiến thức tất cả bài/môn/lớp hoặc đối chiếu toàn bộ trang KNTT/SGV/phụ lục CT2018. Chưa xác minh hết danh mục pháp quy hoặc bản ký QĐ185. TT89/2026 hiệu lực 01/12/2026 chưa được áp sớm tại ngày kiểm 01/11. Không có thay đổi chứng nhận academic_verified, không tự tạo nguồn hay lời giải.

Ảnh kiểm cho thấy nhãn trục cần thêm khoảng trống; đã sửa và kiểm lại bằng DOM. Hai lượt chụp ảnh cuối bị công cụ treo, không coi là bằng chứng ảnh đã lưu. Bằng chứng Chrome cuối là T1_EXACT_LABEL_CURVE_CHROME_{0,10,20}_20261101.txt, manifest và HTML local trong qa_evidence. Không thay đổi giao diện điều khiển, không đưa cache/DB/khóa vào commit.
