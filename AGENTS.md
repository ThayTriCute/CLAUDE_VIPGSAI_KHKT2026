## Owner yêu cầu làm liên tục theo Goal — 07/11/2026

Owner09/11/2026: trước sửa xuất/infographic, đọc docs/AI_SYSTEM_WIDE_VERIFICATION.md. Phiếu học sinh không lộ CORRECT/HINT/EXPLAIN; giữ JSON/parser gốc, tách phụ lục giáo viên đóng mặc định. Dùng chung student_assessment_text/lesson_body_html cho mọi môn/lớp, đo phương án sau dựng công thức/font để chọn4/2/1cột và kiểmChrome. Nhãn giao diện tiếngViệt, không dịch ngữ liệu ngoại ngữ thật. Không chỉ vá một fileHTML hoặc xóa đáp án trong dữ liệu gốc; không tự nhận đạt mọi thể thức đềBộ.

Goal của chat đã được kích hoạt theo yêu cầu owner: tiếp công việc được giao qua các lượt, không dừng chỉ để báo trạng thái hoặc ghi bàn giao. Tự đọc/ghi checkpoint sau mốc rồi làm bước kế tiếp. Chỉ chờ khi đang có tác vụ phụ thuộc thực sự, cần đầu vào bắt buộc, hoặc giới hạn hệ thống; không tạo scheduler/chat/AI bổ sung. Không tuyên bố chạy nền nếu Goal/tác vụ không thực sự hoạt động. Các quy tắc nguồn, không gọi AI trùng, nghiệm thu đúng bằng chứng và phát hành theo khối vẫn giữ nguyên.
## Quy tắc owner xác nhận 07/11/2026 — bảo toàn bài đã duyệt khi xây bộ lọc

- Hoàn thành nghiệm thu tất cả môn khối 10, 11, 12 trước, sau đó mới hoàn thiện bộ lọc CT2018 – KNTT – YCCĐ – văn bản pháp quy.
- Bài mới phải qua kiểm tra theo nguồn và phạm vi áp dụng trước khi nghiệm thu.
- Bài đã được chủ dự án duyệt phải giữ nguyên nội dung, thứ tự/khóa đáp án, trạng thái nghiệm thu và bằng chứng đúng phiên bản. Bộ lọc mới không tự sửa, xóa, chặn sử dụng hoặc hủy nghiệm thu các bài này.
- Rà soát lại bài đã duyệt chỉ ghi cảnh báo/điểm cần đối chiếu. Chỉ mở lại nghiệm thu khi phát hiện lỗi cụ thể có căn cứ; lưu bản cũ và bằng chứng trước/sau, không bắt duyệt lại toàn bộ chỉ vì thay bộ lọc.
- Đây là quy tắc owner đã xác nhận, thay cho trạng thái “đề xuất thiết kế” trong các đoạn lịch sử. Quy tắc chưa phải bằng chứng cơ chế bảo toàn đã được code/kiểm hoàn chỉnh.
- Bản chính nhật ký, bài lưu và bằng chứng nằm tại F:/FINAL KHKT 2026/qa_evidence/. Ca sau phải đọc checkpoint và quy tắc này trước sửa bộ lọc.
## Lưu trữ thống nhất theo owner — 07/11/2026

Bản chính của bài lưu, bản đã đối chiếu, báo cáo và bằng chứng dự án đặt trong F:/FINAL KHKT 2026/qa_evidence/. Chrome Downloads chỉ là vùng tải tạm; sau mỗi lần tải phải sao chép bản chính về F, kiểm dung lượng/hash và ghi đường dẫn F trong checkpoint/lời bàn giao. Không đổi cấu hình Downloads chung hoặc xóa bản cũ ngoài dự án. Mã nguồn tiếp tục trong release_station1_20261031. Không lưu khóa hay dữ liệu học sinh vào thư mục QA/Git; kho bí mật được mã hóa giữ nguyên cơ chế riêng.

## Ưu tiên owner 07/11/2026 — bộ lọc làm sau nghiệm thu THPT

Kiểm xong tất cả môn khối10,11,12 rồi mới tiếp tục hoàn thiện bộ lọc CT2018/KNTT/YCCĐ/văn bản. Phần ràng buộc API đã vá giữ nguyên; đọc docs/AI_CURRICULUM_GROUNDING.md trước sửa tiếp. Không coi prompt là bộ kiểm định học thuật hoàn chỉnh.

## Quy tắc ưu tiên 07/11/2026 — AI sinh bài và bố cục bước

- Trước sửa prompt/sinh bài/renderer/export, đọc checkpoint và `docs/AI_TEACHING_STEPS_LAYOUT_PROMPT.txt`. Owner đã duyệt bố cục xuống đoạn từng bước; giữ đóng bằng chứng đã duyệt khi không có lỗi mới.
- API không mặc nhiên đọc tệp local. Mọi đường gọi model phải nhận quy tắc qua `with_teaching_step_layout` tại ranh giới API, gồm JSON/streaming/model dự phòng; không chỉ thêm hướng dẫn vào tài liệu. Đường/provider mới phải có kiểm thử contract tương ứng.
- Giữ formatter dùng chung sau sinh, bảo toàn toán/mã/đáp án; không vá riêng một môn/lớp hoặc mẫu bài. Không thêm lượt AI, tăng retry hoặc sinh lại bài đã lưu để kiểm bố cục.
- Phát hành theo quyết định owner mới nhất: hoàn thành local khối nào mới push đợt khối đó; quy tắc này ưu tiên các mục lịch sử yêu cầu push từng bản vá nhỏ.

# Hướng dẫn bổ sung cho BBT và đồ thị

## Chủ dự án nhắc lại 07/11/2026: mọi bản vá phải xét toàn hệ thống

Yêu cầu nhân sinh mới nhất áp dụng đủ Trạm1, Trạm2, Trạm3: đọc docs/AI_CONTEXTUAL_PHILOSOPHY_CLOSURE.md trước sửa/sinh phản hồi gia sư. Khi HS hiểu và không còn hỏi, phải đúc kết rồi giảng nhân sinh sâu theo ngữ cảnh, đa dạng Á–Âu/cổ–hiện đại và tránh lặp qua phiên/trạm. Hướng dẫn phải vào API, không chỉ tồn tại trong file. Ghi rõ giới hạn lịch sử runtime/Cloud và kho nguồn hữu hạn; không tự tuyên bố mọi bài giảng đã mới/đúng từ test cơ chế.

Trước vá/sinh bài, đọc docs/AI_CURRICULUM_GROUNDING.md và docs/AI_TEACHING_STEPS_LAYOUT_PROMPT.txt. Tìm nguyên nhân ở tầng dùng chung đa môn/đa lớp, không chỉ sửa ca mẫu rồi báo đạt toàn hệ thống. Quy tắc phải đi vào system instruction tại ranh giới API cho cả JSON/streaming/model dự phòng; không mặc định API đã đọc file local. Thêm provider phải kiểm contract này. Quy tắc chuyên môn chỉ áp trong ngữ cảnh thích hợp; giữ bài owner đã duyệt và phân biệt kiểm cơ chế với nghiệm thu kiến thức. Ghi nguyên nhân, phạm vi, bằng chứng trước/sau và phần chưa kiểm trong bàn giao.

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
# Owner 08/11/2026 — tiếp việc khi đang chờ xác nhận tùy chọn

Sau phần tự kiểm, lưu bằng chứng/mục chờ owner (như phân trang in), rồi tự tiếp công việc độc lập hoặc cặp tiếp theo; không chờ owner phản hồi mới tiến hành. Giữ nguyên pending trong nhật ký, không suy im lặng là duyệt. Quyết định này ưu tiên quy tắc cũ phải đóng mọi xác nhận cặp trước mới chuyển. Chỉ dừng bước phụ thuộc vì thiếu đầu vào bắt buộc thật hoặc giới hạn hệ thống. Không gọi AI trùng hoặc tự tạo scheduler/chat.

## Owner 08/11/2026 — rà soát Lịch sử, GDCD, GDKT&PL

Với Lịch sử, GDCD và Giáo dục kinh tế và pháp luật ở mọi lớp/trạm: rà kỹ các khẳng định về đường lối, chính sách, chính trị và pháp luật Việt Nam. Ba nguồn sách chủ dự án yêu cầu là VniTeach, Nền tảng Tập huấn NXBGDVN và Trường Học Số Quốc Gia, đúng ba cột thư viện trong ứng dụng; không hiểu thành ba loại SGK/SGV/SBT hoặc ba bộ sách. Rà soát bài liên quan qua cả ba nguồn này, xác minh đúng môn/lớp/bộ KNTT/ấn bản và phạm vi đã đọc. Cùng một cuốn được dẫn lại ở nhiều cổng không phải ba bằng chứng độc lập; ghi rõ nguồn trùng, thiếu hoặc không truy cập được, không tự coi đã đọc. Bài mẫu không đại diện toàn cuốn. Tách sự kiện/tư liệu gốc, diễn giải lịch sử, nội dung sách và quy định pháp luật hiện hành; không tự gán tác giả, động cơ, lập trường hoặc lời trích cho tư liệu. Nhận thức có góc nhìn khác nhau không có nghĩa mọi nhận định đều đúng hoặc tùy tiện. Khẳng định pháp lý phải có văn bản chính thức đã đọc, điều/khoản liên quan, ngày hiệu lực, sửa đổi và phạm vi áp dụng tại ngày đánh giá; phân biệt bối cảnh lịch sử với luật hiện hành. Thiếu một nguồn bắt buộc thì ghi rõ chưa đối chiếu đủ, không chứng nhận đạt pháp luật Việt Nam hoặc đã đối chiếu đủ ba nguồn sách. Không tự sửa bài đã được chủ dự án duyệt chỉ vì bổ sung hướng dẫn này.

Quy tắc được truyền qua ACADEMIC_GROUNDING_GUIDANCE tại cả hai transport JSON/streaming trước model dự phòng. Đây là yêu cầu kiểm chứng, không phải bộ kiểm định tự động hoặc bằng chứng đã kiểm hết sách/pháp luật. Hồ sơ nghiệm thu phải lưu tên/ấn bản/phạm vi đã đọc, nguồn chính thức cho từng khẳng định cần đối chiếu, lỗi và trạng thái chưa xác minh. Giữ bản gốc và các phần owner đã duyệt.

## Owner 08/11/2026 — ưu tiên kho nén ba nguồn tại local

Ba nguồn VniTeach, Tập huấn NXBGDVN, Trường Học Số Quốc Gia đã có dữ liệu nén trong F:/FINAL KHKT 2026/textbook_archive_6_12. Trước tìm online/tải lại, đọc manifest.json, offline_book_inventory.json, book_index.json và metadata liên quan; kiểm cả .xz/.tar.xz, không chỉ .zip/.rar/.7z. Giải nén có chọn lọc để đọc đúng bài, giữ bản gốc. Phân biệt PDF/ảnh trang sách với HTML danh mục/liên kết; tên kho hoặc giải nén thành công không chứng minh đã đủ sách hay đã nghiệm thu nội dung. Evidence khám phá: F:/FINAL KHKT 2026/qa_evidence/THREE_SOURCE_LOCAL_ARCHIVE_DISCOVERY_20261108.json.

## Quyết định owner 08/11/2026 — chỉ tra online khi có lý do cụ thể

Bắt buộc dùng kho nén F:/FINAL KHKT 2026/textbook_archive_6_12 trước: tra chỉ mục/metadata và nội dung nén liên quan đúng môn, lớp, bộ, cuốn, bài; tái dùng bằng chứng còn đúng phiên bản. Chỉ tra VniTeach, Tập huấn NXBGDVN hoặc Trường Học Số Quốc Gia khi (1) kho thiếu đúng sách/nội dung cần dùng sau khi đã kiểm có mục tiêu, hoặc (2) cần xác tín thêm điểm cụ thể như ấn bản, trang cập nhật, mâu thuẫn nguồn. Trước tra online ghi ngắn phần local đã kiểm và lý do cần tra; sau tra lưu nguồn/bằng chứng về F để dùng lại. Không tìm link, tải lại, gọi AI hoặc đọc lại toàn cuốn chỉ vì chưa xem kỹ kho; không coi chỉ mục cũ là bằng chứng toàn kho thiếu. Không tự tăng retry hoặc sinh lại bài đã có. Đây là điều kiện bắt buộc, không chỉ khuyến nghị ưu tiên local. Giữ kiểm chứng cần thiết, không tự công bố kiến thức/pháp luật đã đạt.

## Owner xác nhận 08/11/2026 — nhãn Bộ sách Thống Nhất

Chủ dự án xác nhận “Bộ sách Thống Nhất” trong kho/THSQG này chính là KNTT thống nhất. Không coi khác nhãn Thống Nhất/KNTT tự nó là sai bộ sách hoặc lý do bắt buộc tra online. Dùng đối chiếu tiếp theo xác nhận này; vẫn kiểm đúng môn/lớp/cuốn/bài/trang và các cập nhật cụ thể khi có căn cứ cần xác tín.

## Owner 08/11/2026 — căn cứ kho XZ khi Trạm1 sinh bài

Mọi AI sinh bài Trạm1 phải dùng căn cứ đúng môn/lớp/cuốn/bài/trang từ kho local trước; chỉ bổ sung từ ba nguồn khi phần căn cứ còn thiếu hoặc cần xác tín điểm cụ thể. CT2018 cùng sửa đổi còn hiệu lực và KNTT/KNTT thống nhất là chuẩn; bộ lọc hoàn chỉnh làm sau nghiệm thu các môn/lớp, không coi prompt là đã hoàn thành bộ lọc. API không tự đọc filesystem hay tra web: ứng dụng phải truyền nội dung nguồn vào request.

Cơ chế hiện tại: lesson_generation_request gọi local_textbook_grounding trước API và đưa kết quả vào textbook_grounding trong user context. Đọc index.json và đúng một gói json.xz đã đối chiếu ở textbook_archive_6_12/reviewed_lesson_packets, kiểm SHA/đường dẫn/đúng môn-lớp-bài/trạng thái/phạm vi, giới hạn kích thước. Biến GSAI_TEXTBOOK_ARCHIVE_ROOT chỉ nơi mount kho trên máy khác; không có kho thì archive_unavailable, không giả vờ Cloud truy cập F. Gói là trích diễn giải theo bằng chứng đã đọc, không phải toàn văn sách. Không tự biến HTMLcatalog/PDF chưa đọc thành kiến thức chuẩn. Thiếu gói ghi no_exact_reviewed_packet; gói lỗi ghi invalid_reviewed_packet, không đưa nguồn lỗi vào API. Hướng dẫn chung cả hai transport yêu cầu phân biệt thiếu căn cứ và nội dung đã đọc, không tự tuyên bố đủ ba nguồn/YCCĐ/luật.

Mới có gói Bài1 Lịch sử10 từ bằng chứng SGK6–10/SGV23–31 đã đọc; chưa đủ mọi môn/lớp, chưa có OCR/tự đọc ảnhPDF/XZ toàn kho hoặc bộ tra web tự động. Cần lần lượt lập gói đúng bài từ kho và lưu vị trí/phiên bản, kiểm nội dung thật. Không tự sinh lại bài đã duyệt để thử cơ chế. Bộ lọc tương lai phải bảo toàn bài owner-approved và chỉ mở lại khi có lỗi cụ thể có căn cứ.

## 08/11/2026 — Lab đối chiếu nguồn local

Lệnh chính xác “Đối chiếu tư liệu theo bài học” lấy cấu hình source_workshop từ hồ sơ đúng môn/lớp/bài. Cards là diễn giải sư phạm có phạm vi, không trích nguyên văn hoặc chứng nhận pháp lý. Renderer và chấm nhận xét chạy local, không AI; khi thiếu cấu hình của lệnh này phải báo thiếu, không tự chuyển sang API. Cấu hình hiện có cho Bài1 Lịch sử10, Bài5 Địa lí10, Bài11 GDKT&PL10. Kiểm cơ chế/renderer khác nghiệm thu nguồn toàn chương trình; UI từng bài phải có bằng chứng riêng. Không đưa bộ câu hỏi/đáp án workshop vào prompt sinh bài vì không cần trả token cho phần chạy local.

## Owner08/11/2026 — kho khóa kiểm local được ủy quyền

Owner cung cấp key mới và cho phép mã hóa để các ca AI kiểm local không phải chờ nhập lại. File duy nhất: C:/Users/pmtgi/AppData/Local/GSAI/credentials/gemini_qa.dpapi, Windows DPAPI theo tài khoản Windows hiện tại. Đã kiểm giải mã được; chưa coi là API đã xác thực trước khi có yêu cầu thật thành công. Khi cần, giải mã trong bộ nhớ của luồng thao tác rồi nhập đúng ô password của app local bằng Chrome MCP; tuyệt đối không in giá trị ra tool output, không lấy dump mọi input/DOM có password, không ghi vào QA/log/code/Git, không dùng lại key cũ đã lộ. Không tự động gọi AI chỉ để ping nếu có lượt bài cần làm thực sự. Ghi trạng thái pending trước yêu cầu và lưu full JSON sau nhận. Không đưa file DPAPI lên GitHub/Cloud: nó gắn với tài khoản Windows; Cloud dùng kho Secrets riêng khi triển khai được ủy quyền. Không khẳng định key cũ đã được thu hồi khi chưa có bằng chứng. Quyền sử dụng kiểm thử này tiếp tục qua ca theo checkpoint; không hỏi lại việc nhập key khi có thể dùng kho đã cấp.

## Owner: bắt buộc kiểm chứng toàn hệ thống

Mọi AI làm việc với repo phải đọc docs/AI_SYSTEM_WIDE_VERIFICATION.md cùng checkpoint. Sửa đúng tầng dùng chung, kiểm local trước, Chrome khi nghi vấn hoặc kiểm đại diện; bảo toàn owner-approved. Model sinh nội dung nhận quy tắc cốt lõi qua system instruction dùng chung JSON/streaming trước fallback, không phải tự đọc filesystem. Không tự coi prompt hoặc audit không cảnh báo là nghiệm thu kiến thức.

## Lab UTC local — chi tiết

Công cụ Đổi giờ và ngày theo UTC nằm trong thư viện Lab của Địa lý mọi lớp, nhãn tham khảoKNTT10. fixed_offset_clock dùng chung kiểm ngày, độ lệch nguyên phút và tràn lịch; renderer hiển thị A/UTC/B và đổi ngày khi thay dữ kiện. Chỉ dùng độ lệch được cho, không tự suy giờ pháp định/DST theo tên thành phố, kinh độ hoặc hướng đi. Không phải mô phỏng chuyển động TráiĐất, không chứng nhận toànchươngtrình. Không gọiAI. Khi kiểm/sửa tái dùng tests/test_fixed_offset_clock.py và bằng chứng T1_DIALY10_UTC_*_UI_20261108.json; giữUI/tínhnăngkhác và không sinh lại bài đã lưu.

Ngữ cảnh sinh bài chỉ gửi nguồn/tiêu chí/grounded_facts cần thiết; source_workshop, content_corrections và assessment_proposals là dữ liệu xử lý local, không gửi lại bản nháp sai/khóa câu hỏi trong request sinh bài. Giữ nguyên cơ chế sửa ở renderer/export/quiz; không xóa hồ sơ sửa để giảm token. Bằng chứng cấu trúc và so sánh số ký tự không phải số token hoặc chi phí API thực tế.

## THSQG — danh mục tải thêm khi cuộn (owner nhắc 08/11/2026)

Danh mục THSQG có thể chỉ tải20sách ban đầu. Phải cuộn đúng vùng danh mục `overflow-auto` và đối chiếu danh sách tải thêm trước khi kết luận thiếu sách; không chỉ cuộn body. Ngày08/11/2026 lớp11 tăng từ20lên30sách, bổ sung đúng2nhánh Công nghệ và10chỉ mục đã lưu vềF. Mở Mục lục trước khi chọn Chương/Bài trong reader; số trangreader có bìa có thể lệch trangin. Link/danh mục/sốtrang không chứng minh nội dung đã đọc. Ghi chính xác bài/trang/phiên bản, nguồn trùng/khác; dừng yêu cầu tải trả403, không đổiheader/đườngdẫnbypass. Có thể đọc nội dung đang được trình đọc hiển thị hợp lệ qua ChromeMCP; không tựcoi đãtải/lưuảnhkhibịtooltừchối. EvidenceT1_THSQG11_EXPANDED_CATALOG_20261108.json,T1_CN11_THSQG_REVIEW_20261108.json.


## Owner 08/11/2026 — ẩn metadata kỹ thuật trên mọi bản học sinh

OUTCOME/COGNITIVE_REASON/COGNITIVE_STEPS là khóa nội bộ, không phải chữ hiển thị cho học sinh. Mọi AI tiếp quản phải giữ schema/dữ liệu gốc, dùng student_essay_text ở tầng hiển thị/xuất/infographic/prompt ảnh cho mọi môn/lớp; không vá riêng một bài hoặc chỉ đổi nhãn sang tiếng Việt. Đọc docs/AI_SYSTEM_WIDE_VERIFICATION.md; kiểm JSON nhiều dòng, code examples, bài kế tiếp và bản xuất thật. Lỗi được owner chỉ ra trên bản QA Vật lí11 là ca tái hiện, không giới hạn phạm vi.


## LUẬT BẮT BUỘC owner 09/11/2026 — làm việc nghiêm cẩn, có bằng chứng, không chủ quan (áp dụng MỌI ca AI)

Bài học xương máu: một ca AI đã KẾT LUẬN khi mới đọc một phần code (chỉ đọc `exact_plot_coordinate` của func_3 rồi suy rộng "mọi luồng đã chuẩn"), và đã VÁ làm hỏng một test có sẵn (`test_visual_table_answer_leak` → NameError `_MOET_SYM_RE`) mà không biết vì chưa chạy lại toàn bộ test. Đó là lỗi chủ quan, lanh chanh, quá tự tin. Từ nay MỌI ca AI bắt buộc tuân thủ:

1. ĐỌC TRƯỚC KHI LÀM. Trước khi sửa/kết luận, đọc và rà toàn bộ phạm vi liên quan trên GitHub (file, thư mục, TỪNG DÒNG, kể cả dấu chấm), nếu ca trước chưa làm. Không suy rộng từ một nhánh/một hàm ra toàn hệ thống. Mọi khẳng định phải kèm bằng chứng cụ thể: trích đúng `đường_dẫn:dòng`, kết quả lệnh, hoặc so sánh baseline. Không đoán qua loa, không báo cáo khi chưa xác tín.

2. CHẠY TEST ĐỐI CHIẾU BASELINE sau MỌI thay đổi code. "Tick xanh" của repo là CI `.github/workflows/ci.yml`: `py_compile app.py precision_visual_engine.py real_exam_engine.py database.py lesson_infographic_engine.py` + `python -m unittest discover -s tests -p "test_*.py"`. Quy trình bắt buộc: (a) py_compile 5 file; (b) chạy toàn bộ `tests/` trên nhánh của mình VÀ trên `main` (5dbe486 hoặc main hiện hành); (c) so tập test FAIL hai bên — BẤT KỲ test nào fail trên nhánh mình mà không fail trên main là HỒI QUY do mình, phải vá trước khi báo xong. Không được phá "tick xanh".

3. PHÂN BIỆT LỖI THIẾU-THƯ-VIỆN vs LỖI THẬT. Container kiểm thử thường THIẾU sympy/streamlit/plotly/google-genai/ijson/pymupdf (CI có đủ qua requirements.txt). NHƯNG test fail do `ModuleNotFoundError` tại chỗ là test CHƯA KIỂM ĐƯỢC, KHÔNG phải bằng chứng "không hồi quy": lỗi thật của mình có thể nằm ngay trong test đó (sự cố 09/11: tập FAIL nhánh == main nhưng CI đỏ 144 lỗi NameError ở `test_lesson_named_variation_tables`/`test_teacher_lesson_tables`, bị lỗi thiếu sympy che). Cách kiểm tại chỗ: chạy lại với sympy giả lập (`PYTHONPATH=<thư mục có sympy.py stub>`) cho các test liên quan; bằng chứng cuối cùng LUÔN là CI GitHub xanh. Chỉ lo lỗi thật (fail cả khi có dep, hoặc fail trên nhánh mình mà main không fail). Khi nghi ngờ, CHẠY NGẦM để minh chứng cụ thể (đối chiếu giá trị bằng công cụ độc lập, render hình thật nếu có matplotlib, v.v.).

4. KHÔNG CHỦ QUAN khi không test được tại chỗ. Nếu phần sửa phụ thuộc sympy/streamlit/plotly mà container không chạy được, phải NÓI RÕ "chưa render-test tại chỗ, cần CI/Cloud xác minh" — không tuyên bố "đã chuẩn". Mô phỏng đúng pattern đã chạy trong chính repo; đối chiếu toán bằng công cụ độc lập đã có.

5. app.py XUỐNG DÒNG HỖN HỢP (giữ đúng 477 dòng LF): sửa app.py bằng thay-thế-byte-chính-xác, kiểm "LF-only unchanged" sau mỗi lần; KHÔNG dùng công cụ chuẩn hóa toàn file. Cẩn trọng với `git stash`/`git checkout -- .` kẻo mất thay đổi chưa commit.

6. QUY TRÌNH PHÁT HÀNH: mỗi bản vá một nhánh riêng off main + test riêng; push + mở PR qua REST (`gh api .../pulls`, KHÔNG `gh pr create` vì GraphQL bị chặn 403; Đọc CI được qua REST: `gh api repos/<repo>/actions/runs`, `.../actions/runs/<id>/jobs`, `.../actions/jobs/<id>/logs`, `.../commits/<sha>/check-runs`; chỉ `actions/permissions` và artifact bị chặn). Không báo "xong" khi chưa có CI GitHub xanh cả 3.10 + 3.11 trên đúng head commit. Merge vào main do owner bấm. Sau mỗi mốc cập nhật nhật ký bàn giao đầy đủ.

7. TẤT CẢ là tối ưu toàn cục cho hệ thống ĐA MÔN, ĐA LỚP 6→12, mọi môn, theo CT2018 cùng sửa đổi còn hiệu lực, bộ sách KNTT/KNTT thống nhất, và các văn bản pháp quy của Bộ CÒN HIỆU LỰC tính đến ngày giờ hệ thống hiện tại. Giữ nguyên bài/owner-approved; chỉ mở lại khi có lỗi cụ thể có căn cứ.

8. THÊM HÀM/BIẾN MODULE-LEVEL VÀO app.py ⇒ BẮT BUỘC `grep -rn "load_function\|ast.parse\|exec(compile" tests/` tìm MỌI test trích hàm từ app.py bằng AST, cập nhật bộ nạp của TẤT CẢ (vd `tests/test_expert_patch_regressions.py::load_function` nạp kèm `_MOET_*` + `_SUPPORT_FUNCS`; `tests/test_visual_table_answer_leak.py::_load_renderer`). Hàm mới được renderer gọi mà test không nạp ⇒ NameError bị try/except nuốt ⇒ bảng không render. Sự cố này lặp 2 lần (08/11, 09/11) — không được để lần 3.

9. THƯ MỤC LÀM VIỆC CỦA OWNER: `D:\CLAUDE_FINAL KHKT 2026\VIP_DEMO_GSAITHPT2026-main_THẨM ĐỊNH LÚC 10H_NGÀY 9_11_2026)\` — lưu nhật ký bàn giao và đồng bộ mã đã kiểm vào đây (chỉ ghi file đã đổi, không xóa file, không ghi DB/khóa).
