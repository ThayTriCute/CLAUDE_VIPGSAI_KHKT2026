## Ưu tiên owner 07/11/2026 — bộ lọc làm sau nghiệm thu THPT

Kiểm xong tất cả môn khối10,11,12 rồi mới tiếp tục hoàn thiện bộ lọc CT2018/KNTT/YCCĐ/văn bản. Phần ràng buộc API đã vá giữ nguyên; đọc docs/AI_CURRICULUM_GROUNDING.md trước sửa tiếp. Không coi prompt là bộ kiểm định học thuật hoàn chỉnh.

## Quy tắc ưu tiên 07/11/2026 — AI sinh bài và bố cục bước

- Trước sửa prompt/sinh bài/renderer/export, đọc checkpoint và `docs/AI_TEACHING_STEPS_LAYOUT_PROMPT.txt`. Owner đã duyệt bố cục xuống đoạn từng bước; giữ đóng bằng chứng đã duyệt khi không có lỗi mới.
- API không mặc nhiên đọc tệp local. Mọi đường gọi model phải nhận quy tắc qua `with_teaching_step_layout` tại ranh giới API, gồm JSON/streaming/model dự phòng; không chỉ thêm hướng dẫn vào tài liệu. Đường/provider mới phải có kiểm thử contract tương ứng.
- Giữ formatter dùng chung sau sinh, bảo toàn toán/mã/đáp án; không vá riêng một môn/lớp hoặc mẫu bài. Không thêm lượt AI, tăng retry hoặc sinh lại bài đã lưu để kiểm bố cục.
- Phát hành theo quyết định owner mới nhất: hoàn thành local khối nào mới push đợt khối đó; quy tắc này ưu tiên các mục lịch sử yêu cầu push từng bản vá nhỏ.

# Hướng dẫn bổ sung cho BBT và đồ thị

Bắt buộc trước mọi thao tác liên quan hình trong infographic: đọc `docs/AI_BBT_GRAPH_INFOGRAPHIC_PROMPT.txt`, đối chiếu yêu cầu mới nhất và bằng chứng đúng phiên bản. Mọi đồ thị, hình vẽ, BBT nằm trong infographic phải dùng nền trong suốt để hiện đúng nền infographic, kể cả nền quanh nhãn. Không chèn tấm nền trắng riêng. Giữ nét/nhãn tương phản và kiểm hình thực; đọc prompt không thay thế kiểm chứng. Quy tắc phải có cả trong prompt API và prompt phong cách tải về.

Tuân theo hướng dẫn workspace và checkpoint trong `F:/FINAL KHKT 2026/qa_evidence/HANDOFF_CURRENT.md`.
Khi làm BBT, bảng xét dấu, đồ thị, tô miền hoặc infographic toán, đọc và áp dụng `docs/AI_BBT_GRAPH_INFOGRAPHIC_PROMPT.txt` trước sửa/sinh nội dung. Đây là chỉ dẫn công việc, không phải bằng chứng nghiệm thu. Giữ đóng phạm vi chủ dự án đã duyệt; dùng lại bài thật. Bản vá đủ bằng chứng local phải commit/push file cụ thể trong cùng vòng việc rồi theo CI/merge. Không tự bật lại lịch đã tắt.

Yêu cầu chủ dự án 05/11/2026: phần Đồ thị phải có hình vẽ thực của hàm đã cho. Cực trị và tâm đối xứng có nét gióng tới cả hai trục; giao trục ghi tọa độ. Giữ tọa độ vô tỷ chính xác, không làm tròn và không đè nhãn; nếu chật phải dùng chú giải có liên kết rõ tới điểm. Mỗi ví dụ có hàm riêng phải có hình riêng, không chọn tùy ý một hình thay tất cả.


## Quy tắc bắt buộc của chủ dự án — 07/11/2026: tối ưu toàn cục

- Trước sửa, đọc HANDOFF_CURRENT.md, CHECKLIST_CURRENT.md và yêu cầu nghiệm thu hiện tại. Quyết định owner mới nhất có ưu tiên; mục owner đã duyệt giữ đóng, không kiểm/sinh lại do nhật ký lịch sử thiếu snapshot. Hiện Anh10/Tin10 đã đóng; Công nghệ10 là mục tiếp theo.
- Một lỗi quan sát được là ca tái hiện, không mặc định chỉ thuộc môn/lớp đó. Xác định nguyên nhân ở prompt, parser, kiểm định, trạng thái, renderer hoặc export dùng chung; sửa ở tầng sở hữu nguyên nhân với phạm vi nhỏ nhất. Không thêm đặc lệ theo câu mẫu nếu quy tắc dùng chung giải quyết được; không áp quy tắc chuyên môn sang môn không liên quan.
- Yêu cầu khoa học chung phải được truyền qua system instruction của các đường sinh bài/đề và model dự phòng: đủ giả thiết, phạm vi, điều kiện biên, ngoại lệ, kiểm phản ví dụ; đáp án/lời giải/ngữ liệu/hình nhất quán. Tái dùng cơ chế sẵn có, không chép trùng prompt, thêm lượt AI, tăng retry hoặc bộ chặn làm mất bài hợp lệ. Prompt không tự chứng minh đầu ra đúng.
- Với mỗi bản vá, lưu ca lỗi thật trước/sau; kiểm các đường dùng chung và các môn/lớp liên quan, thêm trường hợp không được thay đổi. Ma trận test cấu trúc không thay nghiệm thu học thuật toàn SGK. Giữ nguyên giao diện/tính năng ngoài thay đổi owner yêu cầu cụ thể; nếu cần sửa rộng phải giải trình được/mất/phạm vi trước.
- UI chỉ Chrome MCP đúng cửa sổ kiểm thử nền tím/avatar T, repoVIP và appVIP được giao. Không desktop, không profile/tab anh đang làm việc. Sau mất kết nối lấy inventory mới, không đoán tabID/profile. Quyền thao tác đã có; không hỏi lại quyền chung, chỉ hỏi khi không xác định được đúng tab hoặc thiếu điều kiện thực tế.
- Kiểm local phù hợp, push tệp cụ thể khi bản vá đã đủ bằng chứng; theo CI/merge rồi xác minh Cloud. Không stage DB/cache/khóa/dữ liệu học sinh. Ghi riêng local/push/main/Cloud và phần chưa kiểm.
- Sau mỗi mốc và trước kết thúc, cập nhật bàn giao ngắn ở đầu file, lưu bằng chứng và kiểm đã ghi thành công: mục hiện tại/đã đóng, nguyên nhân và tầng sửa, phạm vi môn/lớp, commit, test/log, AI pending, blocker và bước tiếp. Không hứa tiếp tục chạy khi không có tác vụ thật đang chạy.
