# Bản vá 18 — thời lượng và nhãn năng lực ở đề luyện Tiếng Anh

## Bằng chứng và nguyên nhân

Cloud đề5791, Tiếng Anh7: cấu hình/đồng hồ45phút nhưng tiêu đề phần câu hỏi ghi50phút. Chấm3/3đúng thành10/10 rồi app tự hiển thị B2(Vận dụng cao), Bậc6ViệtNam và0.75điểmchuẩn. Ba câu luyện tập không phải bài đánh giá năng lực được chuẩn hóa nên không đủ căn cứ kết luận CEFR.

Trong app.py, tiêu đề hardcode50; delta lấy số câu đúng nhân0.25 bất kể cấu hình; CEFR được chọn chỉ theo ngưỡng điểm luyện tập, kèm một nhãn bậc Việt Nam cố định. Đây là mã hiển thị của app, không phải kết luận từ dữ liệu đánh giá chuẩn hóa.

## Phạm vi và được–mất

Thời lượng dùng cùng exam_time_mins với header bài thi. Giữ nguyên ba cột kết quả và cách tính điểm/tỉ lệ; delta nói rõ phạm vi đề luyện tập. Cột CEFR vẫn còn, hiển thị Chưa đánh giá và cần bài đánh giá năng lực chuẩn hóa thay vì tự gán trình độ. Không đổi bố cục, radio, Socratic, export hoặc số lần gọi API.

Mất nhãn năng lực tự suy từ điểm; đây là kết luận không đủ bằng chứng. Không thay bằng một bậc khác. Chưa xây dựng hay tuyên bố có bài đánh giá CEFR chuẩn hóa. Các nhãn chuẩn Bộ khác ngoài phạm vi còn trong bản kiểm.

## Kiểm chứng

AppTest không API với dữ liệu Tiếng Anh7, thời lượng45phút, chọn và nộp bài đúng: kiểm nhãn thời lượng, bảo toàn điểm/tỉ lệ và không tự chứng nhận CEFR. Targeted1/1qua72,045s; full255/255qua193,235s. Log PR6_PATCH18_ENGLISH_LABELS_TARGETED_20261029.log và PR6_PATCH18_ENGLISH_LABELS_FULL_20261029.log ngoài repo. Trạng thái triển khai được ghi trong HANDOFF_CURRENT.md; chưa coi sửa local là nghiệm thu Cloud.

