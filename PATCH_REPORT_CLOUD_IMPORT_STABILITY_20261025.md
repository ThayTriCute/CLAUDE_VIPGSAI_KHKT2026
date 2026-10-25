# Ổn định import khi vận hành nhiều phiên — 25/10/2026

## Bằng chứng và phạm vi kết luận

Cloud ghi KeyError: services.academic_context và services.context_recovery trong cơ chế import của Python. Một lượt chạy có thể dừng ngay ở đầu app.py. Log này chưa chứng minh toàn bộ tiến trình đã sập hoặc chứng minh mọi hiện tượng chậm cùng nguyên nhân. Các file tồn tại, services có __init__.py; không tìm thấy thao tác xóa sys.modules trong mã dự án.

Đọc mã Streamlit 1.66.1 đang cài: LocalSourcesWatcher gom các module cần gỡ khi file thay đổi, rồi flush_pending_evictions gỡ chúng khỏi sys.modules ở đầu lượt chạy. Các phiên dùng chung tiến trình. Thử nghiệm cách ly dùng chính flush_pending_evictions của Streamlit để gỡ một module đang import ở luồng khác đã tái hiện đúng KeyError. Đây là chứng minh cơ chế có thể gây lỗi; chưa có dấu vết đủ để khẳng định chính watcher đã kích hoạt sự cố Cloud cụ thể.

## Cách vá và đánh đổi

Thêm .streamlit/config.toml cho vận hành: server.fileWatcherType="none", server.runOnSave=false. Streamlit chọn NoOpPathWatcher, không đăng ký các bộ theo dõi mã nguồn và không phát sinh việc gỡ module do thay đổi file qua đường đó. Không sửa sys.modules của người dùng, không nuốt mọi lỗi import và không thêm vòng thử lại vô tận.

Bản vận hành phải được khởi động lại sau khi phát hành để nạp mã mới một cách đồng bộ. Chỉ push chưa đủ chứng minh tiến trình đã nạp phiên bản mới. Khi lập trình cục bộ có thể chủ động dùng --server.fileWatcherType=auto; không dùng chế độ đó cho bản vận hành nhiều phiên. Cấu hình này không thay đổi quyền truy cập, mật khẩu hoặc bảo vệ mạng.

## Kiểm chứng

Hai kiểm thử riêng đã đạt: cấu hình vận hành chọn đúng NoOpPathWatcher; tám luồng đồng thời import các dịch vụ thật và nhận đúng ngữ cảnh Toán lớp 6. Kịch bản tái hiện chạy trong tiến trình riêng và thư mục tạm, không gỡ module của app đang dùng. Bộ kiểm tra tổng đạt: 50 tệp Python qua kiểm tra tĩnh/dữ liệu, 161 kiểm thử thành công trong 193,789 giây. Cloud sau phát hành được đối chiếu riêng trong biên bản phát hành.

Không tuyên bố đã chữa mọi lỗi import hay mọi tình huống sập. Sau khi khởi động lại cần kiểm tra giao diện và log mới, không lấy log lỗi cũ làm bằng chứng bản mới vẫn lỗi. Nếu xuất hiện lại phải điều tra nguyên nhân khác, gồm phụ thuộc hoặc cập nhật tiến trình không đồng bộ. Chưa có kiểm thử tải học sinh đồng thời quy mô lớn, chưa có SLA hoặc chứng nhận Big Tech.

## Nguồn kỹ thuật chính

- Cấu hình chính thức: https://docs.streamlit.io/develop/api-reference/configuration/config.toml
- Mã nguồn watcher: https://github.com/streamlit/streamlit/blob/develop/lib/streamlit/watcher/local_sources_watcher.py
- Kết quả tái hiện cục bộ: F:/FINAL KHKT 2026/qa_fixtures/reproduce_import_eviction.py
- Nhật ký sự cố: F:/FINAL KHKT 2026/qa_evidence/cloud_import_diagnostics_20261025.txt
