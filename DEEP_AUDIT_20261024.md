# Rà soát sâu và tối ưu bộ nhớ — 24/10/2026

## Kết luận có bằng chứng

Đợt này kiểm kê 79 tệp dự án, gồm 34 tệp Python và khoảng 34.753 dòng tại thời điểm kiểm kê (không tính `.git`, bytecode và cache kiểm thử). Đã phân tích AST/cú pháp, tìm tên chưa khai báo, kiểm tra dữ liệu và tài nguyên bằng `deep_check_var_project.py`; rà soát các điểm nạp dữ liệu, cache, đồng bộ, chuyển trạm, gọi AI và lưu bài. Đây không phải cam kết mỗi dấu câu đều đã được đánh giá thủ công hoặc mọi nhánh đều được thực thi.

**Phát hiện chính:** kho Toán dùng `json.load` trên XZ giữ khoảng 299,5 MiB đối tượng Python, đỉnh 556,5 MiB trong phép đo `tracemalloc` riêng bộ nạp. Cache nhiều môn và các chỉ mục giữ tham chiếu không giới hạn có thể khiến bộ nhớ tăng qua thời gian. Đây là nguy cơ thiếu RAM có bằng chứng tại máy kiểm thử; chưa có log OOM của Cloud để kết luận đó là nguyên nhân duy nhất của mọi lần văng.

## Bản vá đợt 2

| Vấn đề | Thay đổi | Cách xác minh |
|---|---|---|
| Giải nén cả văn bản JSON lớn vào RAM | Đọc từng đề bằng `ijson`; dùng chung chuỗi bất biến lặp lại, giữ dictionary/list độc lập | So sánh SHA256 nội dung chuẩn hóa toàn bộ 13 shard, 33.679 đề: giống hệt |
| Cache nhiều môn tích lũy | Giữ tối đa 2 shard, 8 danh sách, 4 pool; bỏ tham chiếu chỉ mục/pool khi đẩy shard cũ ra; khóa các thao tác nạp/index để tránh hai luồng cùng giải nén | Kiểm thử eviction và giải phóng tham chiếu; kiểm thử đa môn hiện có |
| Copy/serialize toàn bộ danh sách đề ở cache Streamlit | Bỏ `st.cache_data` của danh sách đầy đủ; dùng cache tầng engine và tạo wrapper nhẹ | Các kiểm thử UI và engine |
| Hai nhánh trộn đề quét gọi `enrich_exam_visuals_jit` chưa tồn tại | Bổ sung hàm làm giàu đúng một đề đã chọn, deepcopy trước khi chỉnh nội dung | Kiểm tra tên khai báo và cách ly sửa đổi nguồn |
| Tạo executor mới mỗi lần Streamlit rerun | Dùng một executor chung qua `st.cache_resource` | Rà soát điểm khởi tạo; kiểm thử UI rerun |
| Sự kiện bị bỏ khỏi pending ngay khi mới gửi nền | Giữ pending tới khi Future thành công, đối soát trên luồng giao diện; giới hạn 32 tác vụ đang chờ trong mỗi phiên | Rà soát luồng; chưa kiểm chứng webhook sản xuất |
| Stream AI đứt giữa chừng có thể nối thêm câu trả lời mới | Dừng với thông báo, giữ phần đã nhận; bỏ vòng fallback thường có thể cộng thêm 240 giây sau 180 giây stream | Kiểm thử lỗi kết nối sau chunk đầu, không gọi lại model |
| Header cũ bị Streamlit magic in ra mỗi lượt | Đổi chuỗi đứng riêng sau import thành comment | Kiểm tra source và AppTest |
| QR mặc định dẫn sang app khác | Đổi URL mặc định sang app demo được yêu cầu; vẫn ưu tiên cấu hình APP_URL | Kiểm tra cấu hình trong source; cần đối chiếu secret thực tế |
| Nguy cơ commit DB học sinh | Thêm ignore DB/WAL/SHM | Không xóa, sửa hay đưa DB vào bản vá |
| Công cụ audit tuyên bố “100%, zero bugs” khi pass | Đổi kết luận thành phạm vi kiểm tra thực sự đạt | Chạy lại audit |

## Đo bộ nhớ

Cùng Python 3.14.5, cùng kho Toán 4.238 đề, cùng `tracemalloc` bắt đầu trước nạp:

| Bộ nạp | Bộ nhớ đang giữ | Đỉnh tạm thời |
|---|---:|---:|
| Trước | 299,5 MiB | 556,5 MiB |
| Sau | 102,6 MiB | 111,2 MiB |

Đỉnh giảm khoảng **80%**, bộ nhớ giữ giảm khoảng **66%**. Đây là bộ nhớ Python do phép đo theo dõi, không phải toàn bộ RSS của Streamlit hay số đo trên Cloud. Có tracing, thời gian trước 4,676 giây và sau 12,543 giây; không tracing, bộ nạp mới được đo 2,778 giây. Không dùng các lần đo khác điều kiện để khẳng định tăng tốc. Thay đổi ưu tiên giảm nguy cơ tràn RAM; đổi qua nhiều môn có thể phải nạp lại shard đã bị loại.

## Kết quả kiểm tra

- Audit cuối sau sửa tương thích: 64 kiểm thử đạt trong 68,322 giây; không còn hai tên hàm chưa định nghĩa đã phát hiện.
- 13/13 shard và 33.679 đề giữ nguyên nội dung chuẩn hóa so với bộ nạp cũ. Không thay đổi câu hỏi, đáp án hoặc nguồn trong dữ liệu trên đĩa.
- Bộ kiểm thử mới kiểm tra JSON/XZ/GZ, dạng object/array, cách ly mutable objects, eviction cache và mất kết nối sau khi đã nhận một phần phản hồi.
- Các kiểm thử UI dùng AppTest, cơ sở dữ liệu tạm và không gọi Gemini thật. Không phải phép thử tải nhiều học sinh.
- Bằng chứng cục bộ: `qa_fixtures/inventory_round2.json`, `bank_integrity_round2.json`, `bank_integrity_round2.log`, `deep_audit_round2_final.log` ở thư mục làm việc cha.

### Bổ sung sau CI Python 3.10

CI phát hiện `OrderedDict.popitem` trên Python 3.10 có thể gọi lại `__getitem__` của cache sau khi đã bỏ liên kết phần tử, gây `KeyError`. Đã thay thao tác lấy/bỏ phần tử bằng các phương thức lớp gốc và thêm kiểm thử thứ tự loại phần tử/đọc cache rỗng. Không merge lượt CI thất bại.

## Phần còn cần làm theo ưu tiên

### P1 — Độ ổn định vận hành

1. Đo Cloud sau triển khai: tải nguội/ấm, chuyển cả 4 trạm, RAM và thời gian API; ghi nhận mất WebSocket/restart. Cần test nhiều phiên có kiểm soát trước khi kết luận hết văng. Không chạy tải lớn lên demo đang dùng mà không có lịch và giới hạn.
2. Đồng bộ nền hiện vẫn thiếu durable outbox dùng chung cho Sheets/Supabase: pending trong session và SQLite không bảo đảm tự retry sau Cloud redeploy. Supabase còn tạo daemon thread theo sự kiện. Nên dùng outbox SQLite với khóa idempotency, worker giới hạn và trạng thái retry/backoff; dữ liệu quan trọng cần nơi lưu bền vững ngoài ổ đĩa container.
3. Upload Word/PDF chưa có đủ giới hạn tài nguyên: kích thước giải nén ZIP, tổng ảnh, số trang và thời gian xử lý. Nên chặn trước giải nén, xử lý trong worker có deadline. Không suy từ giới hạn file upload của Streamlit ra giới hạn bộ nhớ sau giải nén.
4. Cơ chế lưu nháp JavaScript chỉ quét textarea, dùng mã đề làm khóa, chưa chứng minh khôi phục được toàn bộ trắc nghiệm/đúng-sai khi mất hẳn session. Cần snapshot đáp án theo attempt/student/context và luồng khôi phục rõ ràng; không quảng cáo chống mất bài tuyệt đối.

### P2 — Bảo trì và tính đúng đắn

5. `app.py` vẫn khoảng 20 nghìn dòng, nhiều luồng UI/AI/chấm điểm đan xen. Tách từng trạm và service theo từng bước có kiểm thử; tránh viết lại toàn bộ một lượt.
6. `models/exam_models.py` dùng `hash(q_text)` làm ID dự phòng: ID thay đổi giữa process và không phân biệt phương án. Nên chuyển sang fingerprint nội dung ổn định có phiên bản; phải đánh giá tương thích với dữ liệu đã lưu trước khi migrate.
7. BKT/FSRS còn tham số giả định; không diễn giải hệ số đặt sẵn thành bằng chứng hiệu quả học tập. Phần hiển thị dữ liệu giả đã được loại/gắn nhãn ở đợt 1, nhưng comment và tài liệu mô hình còn cần chỉnh để thống nhất.
8. Dependencies đa phần chưa khóa phiên bản và log có cảnh báo Streamlit deprecated (`components.html`, các tham số cũ). Nên tạo bộ phiên bản đã kiểm chứng Python 3.10/3.11, xử lý từng cảnh báo rồi nâng cấp; không thay hàng loạt API chỉ dựa vào warning.
9. Nhiều khối `except Exception: pass`, thời gian cố định “0.1s”, “100%” trong UI và comment che khuất giới hạn thực tế. Nên bổ sung log có event ID, thông báo thao tác có thể phục hồi và bỏ những tuyên bố không có đo lường.
10. `.devcontainer` tắt CORS/XSRF trong lệnh khởi động; nên dùng mặc định an toàn và kiểm tra preview của Codespaces. Không áp dụng cài đặt này lên Cloud.

## Giới hạn kết luận

Bản vá làm giảm một nguy cơ RAM đã đo được và sửa các nhánh lỗi cụ thể. Không đủ cơ sở khẳng định mọi tính năng đã mượt, mọi nội dung học thuật đã đúng, hay app sẽ không bao giờ văng. Không thay mật khẩu Trạm 4, không commit API key, không ghi đè dữ liệu học sinh. Trạng thái triển khai GitHub/Cloud cần được báo riêng theo bằng chứng sau khi xuất bản.
