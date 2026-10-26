# BBT: màu chữ trên nền trắng — 27/10/2026

Tái hiện bằng Streamlit giao diện tối với chính hàm vẽ BBT hiện có: màu trên table không thắng quy tắc màu của từng td. DOM cho chữ/số rgb(250,250,250) trên nền trắng. Đặt màu mực #0f172a tại từng td trong hàm cũ; màu dấu +/- khai báo phía sau vẫn giữ xanh/đỏ. Không đổi dữ kiện, lưới, mũi tên, bộ lọc hoặc luồng gọi. Cả bảng biến thiên và bảng xét dấu dùng nhánh đã có.

19 kiểm thử liên quan qua (BBT, nguồn danh mục và hợp đồng sinh đề). Trình duyệt tại localhost xác nhận chữ/số rgb(15,23,42), dấu xanh rgb(22,163,74), đỏ rgb(220,38,38). Chưa triển khai Cloud: tạm ưu tiên chẩn đoán nội dung Trạm 1 theo báo lỗi người dùng. Không coi DOM hoặc tương phản là chứng nhận học thuật.
