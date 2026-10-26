# Yêu cầu đã thống nhất và checklist nghiệm thu

Cập nhật ngày 26/10/2026. Đây là bản ghi yêu cầu để đối chiếu khi sửa, không phải tuyên bố hệ thống đã hoàn tất. Báo cáo kết quả chi tiết: `BAO_CAO_TONG_HOP_TRAM_1_TRAM_3_20261026.md`; số đo mới: `PATCH_REPORT_LATENCY_AND_TOPIC_CONFLICT_20261026.md`.

**Ưu tiên số một hiện tại theo người dùng: Trạm 3 tạo được đề thật hợp lệ, đúng tùy chọn, hoạt động mượt.** Sau PR24 vẫn có lượt AI bị giữ vì TikZ không phù hợp web và câu trắc nghiệm hai khoảng cùng đúng. Chưa nghiệm thu luồng tạo đề thật; theo dõi sửa tại `PATCH_REPORT_STATION3_WEB_GENERATION.md`. Không lấy 65 ca UI giả lập hoặc CI xanh để ghi rằng mọi lượt sinh đề đã ổn.

## Nguyên tắc làm việc bắt buộc

- Sửa trong thư mục dự án tại máy; đọc diff, chạy thử phù hợp, rồi mới push GitHub. Kiểm CI và kiểm bản Cloud sau triển khai, bao gồm restart tiến trình khi cập nhật module/config. Không coi push thành công là nghiệm thu Cloud.
- Giữ trọn các chức năng và cấu trúc giao diện đã thống nhất. Không tự ý cắt, thay bố cục hoặc đổi triết lý sư phạm khi sửa lỗi khác. Sửa hẹp theo lỗi tái hiện; kiểm các nhánh liên quan, nêu rõ tác động.
- Mỗi bản vá phải có nguyên nhân kỹ thuật, cách sửa, chứng cứ kiểm thử, giới hạn và phần còn lại. Không gọi là chuẩn Bộ, chính xác 100%, hết lag hoặc đẳng cấp Big Tech khi chưa có chứng cứ đủ phạm vi.
- Tiết kiệm API/token bằng kiểm tại máy, dữ liệu mô phỏng và cache có giới hạn. Vẫn thực hiện thử thật khi cần quyết định chất lượng; không bỏ kiểm quan trọng chỉ để tiết kiệm. Không chạy lại hàng loạt request AI không có mục đích đo cụ thể.

## Hợp đồng sản phẩm phải giữ

| Phạm vi | Yêu cầu | Điều kiện nghiệm thu |
|---|---|---|
| Toàn hệ thống | Đa môn, lớp 6–12; tên môn đồng nghĩa quy về cùng ngữ cảnh, không lẫn môn tích hợp với môn riêng | Kiểm đủ 65 tổ hợp đang hỗ trợ, kiểm chuyển ngữ cảnh và dữ liệu cũ |
| Trạm 1 | Bài học, đúng 3 MCQ với radio; mỗi câu có hướng dẫn tư duy Socratic theo câu; 2 bài tự luận theo cấu trúc hiện có | Giữ câu hỏi/phương án, kiểm khóa chấm riêng và đủ thành phần UI |
| Sư phạm | Phân biệt giải thích kiến thức với Socratic; Socratic không giải hộ hoặc tiết lộ đáp án | Kiểm ngữ cảnh, câu hỏi dẫn dắt và chống lộ lời giải; mọi tự luận đủ bốn bước Pólya tiếng Việt |
| Trực quan | Giữ infographic, prompt chữ viết tay, xuất phiếu/HTML/in PDF và video theo bài | Chữ/dấu/công thức rõ, nội dung bám bài sinh ra; dùng mẫu viết tay người dùng làm tham khảo phong cách; video có link là chấp nhận được |
| Phục dựng | Câu thiếu hàm số/hình/dữ kiện phải được bổ sung nhất quán hoặc thay nguyên câu khi được cho phép | Không sửa riêng một phương án bằng số mẫu; kiểm hình, đề, tất cả phương án và đúng một đáp án; phân biệt câu nguồn và câu mới |
| Trạm 3 | Một nút tạo đề luyện tập, ưu tiên kho; AI bổ sung/sửa theo tùy chọn; giữ nguyên đề thật, upload Word/PDF, quét link, chấm và xuất đề | Không gộp mất chức năng các chế độ; không dùng AI khi người dùng tắt; tôn trọng ma trận và số câu |
| Đổi mới đề | Mỗi lượt hướng tới đề khác về nội dung thực chất, không chỉ đổi mã/đảo lựa chọn | Cần kiểm fingerprint/cooldown và thiết kế lịch sử bền vững trước khi bảo đảm giữa mọi phiên |
| Ngữ cảnh | Đúng môn, lớp, chủ đề và tùy biến người dùng | Kiểm cả nhãn và nội dung; nhãn nguồn có thể sai. Mâu thuẫn xác định phải đi qua phục hồi nguyên câu và kiểm lại |
| Công thức | KaTeX/LaTeX đúng cú pháp và đúng ý nghĩa khoa học theo môn | Test parser không thay kiểm DOM/iframe; kiểm export và công thức mẫu. Không suy ra kiến thức đúng chỉ từ việc render được |
| Mức độ | NB/TH/VD và VDC theo phạm vi công bố, không suy từ dạng câu/Phần I–II–III | Có mô tả yêu cầu tư duy và ma trận điểm đối chiếu; VDC là nhãn mở rộng trong app, không tự nhận là mức chính thức của mọi văn bản |
| Bộ lọc | Chưa đạt thì sửa/biên soạn lại có kiểm soát trước khi xuất | Có giới hạn lượt để không lặp vô hạn, không treo hoặc tiêu hao quota vô hạn; hết lượt mà chưa đủ căn cứ thì giữ bản nháp riêng, báo trạng thái trung thực |
| Điều hướng | Giữ cả nút đầu trang và radio sidebar, trạng thái bài/đề nhất quán | Chuyển trạm không gọi AI ngoài ý muốn, không mất nội dung hoặc chấm/lưu lặp |
| Trạm 4 | Giữ chức năng quản trị, dữ liệu nghiên cứu và chẩn đoán | Dữ liệu có đáp án/bản nháp lỗi chỉ sau xác thực; không lộ key. Không biến dữ liệu QA thành thực nghiệm học sinh |

## Nguồn học thuật và cảnh báo xác minh

- Tham chiếu CT GDPT 2018, SGK/SGV Kết nối tri thức với cuộc sống đúng phiên bản và đính chính; văn bản mới còn hiệu lực và văn bản cũ còn hiệu lực tại thời điểm áp dụng. Ưu tiên Bộ, cổng văn bản chính thức và nhà xuất bản. Trang trường/OLM là tham khảo sư phạm, không thay văn bản gốc hoặc chứng minh hiệu lực pháp lý.
- Cần bản đồ yêu cầu cần đạt theo môn/lớp/bài, nguồn, trang/phiên bản và ngày đối chiếu. Prompt và nhãn trong dữ liệu không đủ làm bằng chứng đã kiểm định.
- Chỉ bỏ/thay khung vàng cho từng nội dung có đủ bằng chứng nghiệm thu; khi đó có thể dùng trạng thái gọn “Đã đối chiếu” và chi tiết nguồn. Không bỏ đồng loạt chỉ vì đã có tên bộ lọc.
- Chưa có xác nhận toàn bộ kiến thức, mọi SGK/SGV, mọi văn bản và mọi mức độ. Không đánh dấu các mục này hoàn tất từ ma trận UI 65 tổ hợp.

## Giọng đọc còn dang dở

- Giữ cả ba đường: đọc đoạn chọn, nghe nội dung, double-click/tô chọn. Kiểm tiếng phát thật, không lấy trạng thái “Đã đọc hết” làm bằng chứng có tiếng.
- Tiếng Việt: mong muốn giọng Nam Bộ, trầm ấm, ngắt nghỉ sư phạm và thuật ngữ/công thức đúng từng môn; ưu tiên phương án miễn phí, hiển thị đúng giọng thực tế. Giọng nữ Bắc không đáp ứng yêu cầu Nam Bộ. Tên giọng tiếng Việt không tự chứng minh vùng miền.
- Tiếng Anh: giữ lựa chọn giọng bản ngữ; phân biệt Anh–Việt ở từ/câu được chọn, có lựa chọn tay khi mơ hồ. Nhân bản giọng Việt không tự bảo đảm phát âm Anh bản ngữ.
- Người dùng đã gửi bản thu giọng của chính mình để thử nhân bản. Hiện mới đo tín hiệu tệp tại máy; chưa nghiệm thu bằng nghe, chưa tạo clone và chưa tích hợp. Không cam kết độ giống hoặc giá khi chưa thử công cụ phù hợp. Trước khi chuyển bản thu ra ngoài, làm rõ dịch vụ đích, cách lưu/xóa mẫu và chi phí; chưa có dịch vụ đích được duyệt.
- Thu âm và engine giọng thử phải tách khỏi bản vận hành cho đến khi người dùng nghe duyệt; không làm lại toàn hệ thống để đổi vùng giọng.

## Độ trễ và chi phí

- Đo riêng mở app lạnh, đổi môn/lớp, chuyển trạm nóng, xử lý/kiểm nội dung, chờ AI và đọc âm thanh. Ghi rõ máy/Cloud, cache nóng/lạnh, số mẫu và có giả lập hay không.
- Số đo hiện có: hai lượt UI cục bộ 65 tổ hợp; 285 test hồi quy; sáu lượt chuyển Cloud Toán 12 và hai lượt nội dung thật được quan sát. Chưa có thử tải đồng thời, P95 Cloud toàn bộ môn/lớp hoặc token/request vật lý đầy đủ.
- Mở Trạm 3 cold vẫn cần tối ưu. Không tăng cache vô hạn, bỏ bộ lọc hoặc cắt tính năng để làm đẹp số đo. Mục tiêu UX cần thỏa thuận và đo tiếp, không gọi số đo AppTest là thời gian người dùng thực.

## Những hạng mục chưa được phép ghi “xong hết”

- Kiểm chứng học thuật đầy đủ, nguồn chính thức có phiên bản/hiệu lực và cập nhật.
- Mọi trường hợp phục dựng/duy nhất đáp án, phục hồi đồng bộ Ngữ văn và yêu cầu tùy biến phức tạp.
- Phạm vi Lab đúng từng môn/lớp (đã thấy ví dụ menu Toán 6 còn mẫu bậc ba lớp 12).
- Phát tiếng thực tế cả ba đường, giọng Nam Bộ và giọng nhân bản đã được nghe duyệt.
- Đề khác thực chất giữa mọi phiên, số đo token/quota thật, tải đồng thời và độ trễ Cloud đủ mẫu.

Mỗi lần nghiệm thu phải ghi bản commit, môi trường, ca thử, kết quả và phần còn thiếu. Danh sách này cần cập nhật theo bằng chứng; không dùng như một danh sách quảng cáo tính năng đã đạt.
