# Quy trình phát hành Streamlit Cloud

Với cấu hình `server.fileWatcherType = "none"`, việc Cloud kéo GitHub không bảo đảm nạp lại các module Python đã import. Thay đổi app.py cùng services có thể làm tiến trình đang chạy trộn mã mới và module cũ.

Mỗi bản phát hành cần: sửa tại máy; kiểm thử; CI đạt; push main; khởi động lại tiến trình Cloud khi thay module Python; xác minh lần khởi động trong log; mở phiên mới và kiểm tra Trạm 1–4. Không đánh dấu phát hành hoàn tất chỉ dựa vào dòng Updated app hoặc CI đạt. Không dùng importlib.reload/sys.modules.pop trong phiên người dùng để chữa tạm vì có thể tạo trạng thái không đồng nhất giữa các luồng.

Sự cố ngày 25/10/2026: Cloud kéo bản khôi phục lúc 03:54:51 UTC, báo Updated app lúc 03:54:54 UTC nhưng không có lần khởi động Uvicorn mới ở đoạn log đó; app.py mới import native_radio_label trong khi services.math_publication đang được giữ từ tiến trình cũ. Hàm có trong commit main và CI khởi động sạch đạt. Khởi động lại Cloud là bước phục hồi cần xác minh, không phải bằng chứng rằng mọi lỗi import tương lai đã được loại bỏ.
