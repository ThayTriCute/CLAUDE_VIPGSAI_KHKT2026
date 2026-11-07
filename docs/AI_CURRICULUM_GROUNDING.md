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

Với Lịch sử, GDCD và Giáo dục kinh tế và pháp luật ở mọi lớp/trạm: rà kỹ các khẳng định về đường lối, chính sách, chính trị và pháp luật Việt Nam. Ba nguồn sách chủ dự án yêu cầu là VniTeach, Nền tảng Tập huấn NXBGDVN và Trường Học Số Quốc Gia, đúng ba cột thư viện trong ứng dụng; không hiểu thành ba loại SGK/SGV/SBT hoặc ba bộ sách. Rà soát bài liên quan qua cả ba nguồn này, xác minh đúng môn/lớp/bộ KNTT/ấn bản và phạm vi đã đọc. Cùng một cuốn được dẫn lại ở nhiều cổng không phải ba bằng chứng độc lập; ghi rõ nguồn trùng, thiếu hoặc không truy cập được, không tự coi đã đọc. Bài mẫu không đại diện toàn cuốn. Tách sự kiện/tư liệu gốc, diễn giải lịch sử, nội dung sách và quy định pháp luật hiện hành; không tự gán tác giả, động cơ, lập trường hoặc lời trích cho tư liệu. Nhận thức có góc nhìn khác nhau không có nghĩa mọi nhận định đều đúng hoặc tùy tiện. Khẳng định pháp lý phải có văn bản chính thức đã đọc, điều/khoản liên quan, ngày hiệu lực, sửa đổi và phạm vi áp dụng tại ngày đánh giá; phân biệt bối cảnh lịch sử với luật hiện hành. Thiếu một nguồn bắt buộc thì ghi rõ chưa đối chiếu đủ, không chứng nhận đạt pháp luật Việt Nam hoặc đã đối chiếu đủ ba nguồn sách. Không tự sửa bài đã được chủ dự án duyệt chỉ vì bổ sung hướng dẫn này.

Quy tắc được truyền qua ACADEMIC_GROUNDING_GUIDANCE tại cả hai transport JSON/streaming trước model dự phòng. Đây là yêu cầu kiểm chứng, không phải bộ kiểm định tự động hoặc bằng chứng đã kiểm hết sách/pháp luật. Hồ sơ nghiệm thu phải lưu tên/ấn bản/phạm vi đã đọc, nguồn chính thức cho từng khẳng định cần đối chiếu, lỗi và trạng thái chưa xác minh. Giữ bản gốc và các phần owner đã duyệt.

## Owner 08/11/2026 — ưu tiên kho nén ba nguồn tại local

Ba nguồn VniTeach, Tập huấn NXBGDVN, Trường Học Số Quốc Gia đã có dữ liệu nén trong F:/FINAL KHKT 2026/textbook_archive_6_12. Trước tìm online/tải lại, đọc manifest.json, offline_book_inventory.json, book_index.json và metadata liên quan; kiểm cả .xz/.tar.xz, không chỉ .zip/.rar/.7z. Giải nén có chọn lọc để đọc đúng bài, giữ bản gốc. Phân biệt PDF/ảnh trang sách với HTML danh mục/liên kết; tên kho hoặc giải nén thành công không chứng minh đã đủ sách hay đã nghiệm thu nội dung. Evidence khám phá: F:/FINAL KHKT 2026/qa_evidence/THREE_SOURCE_LOCAL_ARCHIVE_DISCOVERY_20261108.json.

## Quyết định owner 08/11/2026 — chỉ tra online khi có lý do cụ thể

Bắt buộc dùng kho nén F:/FINAL KHKT 2026/textbook_archive_6_12 trước: tra chỉ mục/metadata và nội dung nén liên quan đúng môn, lớp, bộ, cuốn, bài; tái dùng bằng chứng còn đúng phiên bản. Chỉ tra VniTeach, Tập huấn NXBGDVN hoặc Trường Học Số Quốc Gia khi (1) kho thiếu đúng sách/nội dung cần dùng sau khi đã kiểm có mục tiêu, hoặc (2) cần xác tín thêm điểm cụ thể như ấn bản, trang cập nhật, mâu thuẫn nguồn. Trước tra online ghi ngắn phần local đã kiểm và lý do cần tra; sau tra lưu nguồn/bằng chứng về F để dùng lại. Không tìm link, tải lại, gọi AI hoặc đọc lại toàn cuốn chỉ vì chưa xem kỹ kho; không coi chỉ mục cũ là bằng chứng toàn kho thiếu. Không tự tăng retry hoặc sinh lại bài đã có. Đây là điều kiện bắt buộc, không chỉ khuyến nghị ưu tiên local. Giữ kiểm chứng cần thiết, không tự công bố kiến thức/pháp luật đã đạt.

## Owner xác nhận 08/11/2026 — nhãn Bộ sách Thống Nhất

Chủ dự án xác nhận “Bộ sách Thống Nhất” trong kho/THSQG này chính là KNTT thống nhất. Không coi khác nhãn Thống Nhất/KNTT tự nó là sai bộ sách hoặc lý do bắt buộc tra online. Dùng đối chiếu tiếp theo xác nhận này; vẫn kiểm đúng môn/lớp/cuốn/bài/trang và các cập nhật cụ thể khi có căn cứ cần xác tín.
