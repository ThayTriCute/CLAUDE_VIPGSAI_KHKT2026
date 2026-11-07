# CT2018, KNTT, YCCĐ và văn bản áp dụng

Phần chốt gia sư Trạm1–3 phải tuân docs/AI_CONTEXTUAL_PHILOSOPHY_CLOSURE.md: đủ chiều sâu, mới theo ngữ cảnh, luân phiên nguồn Á–Âu/cổ–hiện đại có xác minh và lịch sử kế hoạch qua phiên. GUIDANCE của philosophy_rotation được with_academic_grounding gắn chung cho mọi transport/model; đọc tệp không thay việc truyền API hoặc kiểm phản hồi thật.

## Quy tắc chủ dự án nhắc lại 07/11/2026 — sửa cho toàn hệ thống

Mỗi lỗi quan sát là ca tái hiện để tìm tầng sở hữu nguyên nhân trong prompt, nguồn, parser, kiểm định, trạng thái, hiển thị hoặc xuất. Ưu tiên cơ chế chung đa môn/đa lớp; không coi sửa một ví dụ là hoàn thành hệ thống. Quy tắc chuyên môn phải có điều kiện môn/chủ đề phù hợp, không áp cơ học sang môn khác.

AI qua API không tự mở tệp local. Quy tắc bắt buộc phải thực sự vào system instruction tại hai ranh giới with_academic_grounding/with_teaching_step_layout trước vòng chọn key/model, dùng cho JSON, streaming và fallback. Provider mới phải giữ cùng contract. File hướng dẫn và kiểm cấu trúc không chứng minh mọi đầu ra kiến thức đã đúng.

Hiệu chỉnh bài thật theo nguồn dùng apply_reviewed_content_corrections: chỉ hồ sơ đúng môn/lớp/chủ đề có cặp before/after và lý do rõ; bảo toàn code, khóa đáp án và bài đã duyệt không có quyết định mở lại cụ thể. Không suy diễn rồi tự viết lại mọi bài. Lưu bản gốc, bản sửa và kiểm idempotence/ca không được đổi; kiểm lại UI, xuất và phạm vi liên quan. Bổ sung 07/11 về vận chuyển qua màng đã vào ACADEMIC_GROUNDING_GUIDANCE dùng chung, không chỉ ghi ở bài Sinh10.

Trước sửa phần sinh nội dung, đọc checkpoint và tài liệu này. Hai transport trong app.py bắt buộc gọi with_academic_grounding trước vòng model/key, kể cả JSON, streaming và fallback. Provider mới phải giữ contract tương đương. API không tự đọc tài liệu local.

Tái dùng policy_prompt theo môn/lớp/trạm, reviewed_lesson_sources đúng bài, curriculum_outcome_overrides và hồ sơ nguồn đã đọc. Không lấy mục tiêu AI tự viết làm YCCĐ chính thức. Không coi link SGK là toàn văn sách đã được đưa vào model.

Tình trạng 07/11/2026: ràng buộc prompt dùng chung không phải bộ kiểm định học thuật hoàn chỉnh. Registry nguồn từng bài và bản đồ YCCĐ còn thiếu; overrides chỉ là pilot ba mục. Chưa được tuyên bố phủ toàn bộ CT2018/KNTT hoặc mọi văn bản hiện hành. Cần bổ sung phụ lục môn/lớp, YCCĐ có vị trí/phiên bản, ánh xạ bài và bộ ca kiểm đầu ra trước khi đóng nghiệm thu toàn hệ thống.

Metadata pháp lý chỉ phục vụ tra cứu; dùng ngày hiệu lực, đọc sửa đổi cùng bản gốc và phân biệt quy phạm với hướng dẫn. Ngày 07/11 sửa mục TT13/2026 từng trỏ nhầm TT13/2022: nguồn đúng https://vanban.chinhphu.vn/?docid=217189&pageid=27160&typegroupid=6 . Chỉ xác minh danh tính văn bản, chưa ánh xạ từng điều.

Không thay UI, schema, retry hoặc gọi AI thêm để chứng minh prompt. Kiểm cấu trúc khác nghiệm thu kiến thức thật. Giữ các ca owner đã duyệt và chính sách hoàn thành local theo khối trước push.

## Owner 08/11/2026 — rà soát Lịch sử, GDCD, GDKT&PL

Với Lịch sử, GDCD và Giáo dục kinh tế và pháp luật ở mọi lớp/trạm: rà kỹ các khẳng định về đường lối, chính sách, chính trị và pháp luật Việt Nam. Đối chiếu đủ ba đầu sách chủ dự án đang dùng sau khi xác minh tên bộ, ấn bản và phạm vi từng cuốn; không mặc định ba đầu sách là ba bộ sách khác nhau hoặc SGK/SGV/SBT khi chưa xác minh. Bài mẫu không đại diện toàn cuốn. Tách sự kiện/tư liệu gốc, diễn giải lịch sử, nội dung sách và quy định pháp luật hiện hành; không tự gán tác giả, động cơ, lập trường hoặc lời trích cho tư liệu. Nhận thức có góc nhìn khác nhau không có nghĩa mọi nhận định đều đúng hoặc tùy tiện. Khẳng định pháp lý phải có văn bản chính thức đã đọc, điều/khoản liên quan, ngày hiệu lực, sửa đổi và phạm vi áp dụng tại ngày đánh giá; phân biệt bối cảnh lịch sử với luật hiện hành. Thiếu một nguồn bắt buộc thì ghi rõ chưa đối chiếu đủ, không chứng nhận đạt pháp luật Việt Nam hoặc đủ ba đầu sách. Không tự sửa bài đã được chủ dự án duyệt chỉ vì bổ sung hướng dẫn này.

Quy tắc được truyền qua ACADEMIC_GROUNDING_GUIDANCE tại cả hai transport JSON/streaming trước model dự phòng. Đây là yêu cầu kiểm chứng, không phải bộ kiểm định tự động hoặc bằng chứng đã kiểm hết sách/pháp luật. Hồ sơ nghiệm thu phải lưu tên/ấn bản/phạm vi đã đọc, nguồn chính thức cho từng khẳng định cần đối chiếu, lỗi và trạng thái chưa xác minh. Giữ bản gốc và các phần owner đã duyệt.
