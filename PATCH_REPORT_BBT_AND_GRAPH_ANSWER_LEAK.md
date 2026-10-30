# BBT lệch cột và công thức lộ đáp án trong câu nhận dạng đồ thị

Nguyên nhân: question_visual_html bỏ qua công cụ BBT có sẵn và tách thô chuỗi bằng |, phá vạch kép ||/căn cột. Prompt WEB_QUESTION_INSTRUCTION yêu cầu nêu công thức hàm số tương ứng, trái mục tiêu nhận dạng đồ thị. Không có object gốc của ảnh nên không quy chắc mọi chi tiết dữ liệu trong ảnh cho một bước cụ thể.

Sửa: bảo vệ vạch kép, chuẩn hóa slot có đủ dữ liệu và gọi _build_svg_bbt_from_rows đã có, giữ hệ số/giới hạn nguồn. Bảng có ô || trống giới hạn được đưa vào luồng phục dựng/thay cả câu, không tự điền giới hạn. Dạng chưa hỗ trợ và hai hàng vẫn giữ văn bản nguồn, không cắt dữ liệu. Không thay đồ thị/radio/giao diện tổng thể.

Prompt mới yêu cầu công thức tạo hình ở f/explain nội bộ; câu nhận dạng không chứa công thức đáp án trong q/chú thích. Guard hẹp nhận diện công thức ở câu hỏi “đồ thị ... hàm số nào” và đưa vào bộ thay toàn câu có sẵn. Không xóa tùy tiện công thức khỏi bài cho hàm thông thường; nguồn/khóa gốc được giữ trong kiểm thử. Không tăng retry/cap API.

Targeted47/47 qua6.047s; full288/288 qua253.460s (VISUAL_TABLE_LEAK_FULL_20261030.log). Bank replacement kiểm không gọiAI/không mutate nguồn. Preview HTML qua Chrome MCP thấy các mốc -inf,-2,-1,0,+inf/vạch kép/giới hạn trái-phải/mũi tên căn đúng trên dữ liệu fixture đủ; không coi đó là chứng nhận câu nguồn. File qa_evidence/BBT_PATCH_PREVIEW_20261030.html.

Được: sử dụng lại renderer cũ, sửa prompt mâu thuẫn, phát hiện lộ công thức trước xuất bản. Giới hạn: parser BBT có phạm vi, dạng chưa hiểu giữ văn bản; không thẩm định mọi bảng/kiến thức/KNTT. Nếu không có câu thay thế đạt trong ngân sách hiện hữu vẫn báo chưa đủ, không giấu lỗi bằng hình mẫu. Cloud cần kiểm nạp mới sau merge; không coi unit tests là nghiệm thu toàn hệ thống.

