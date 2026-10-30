# Tích hợp nhập văn bản trước — 31/10/2026

Đã tích hợp ý text-first vào real_exam_engine.parse_file_direct_with_ai cho TXT/TEX/MD (không phân biệt hoa thường). Trước đây khi có ai_caller, các tệp này đi qua bytes multimodal rồi mới fallback text; nay gọi extractor và parse_raw_exam_text hiện có trực tiếp. Giữ nguyên subject/grade/school/title/user_prompt và ai_caller để bộ parser quyết định fallback theo logic cũ. Không thêm API/provider/retry/dependency/UI.

PDF/Word giữ nhánh visual: không đủ bằng chứng chỉ text bảo toàn ảnh/MathType để đổi rộng. Không nhập500câu manifest vì thiếu shard; không áp classifier ép KNTT/mức độ. Chưa thêm checkpoint batch vì ứng dụng hiện không có luồng batch tương ứng; tránh sinh module không được dùng.

Kiểm thử: tests.test_text_first_import + tests.test_live_patch:29/29qua5.545s,logTEXT_FIRST_IMPORT_TEST_20261031.log. Kiểm bảo toàn ngữ cảnh Tiếng Anh6,3extension,PDF/DOCX giữ bytespath,existingWord/PDF tests. Provider mock/offline,API0. Expected negative-score/grade logs trong suite không phải lỗi production; ResourceWarningSQLite có sẵn. gitdiffcheckqua. Chưa đo tốc độCloud/chưaChromeUI/chưa push/CI; đây không nghiệm thu học thuật đa môn đa lớp. Tác dụng giảm lượt multimodal không cần thiết cho plain text; không khẳng định mọi tệp0API vì parser cófallback khi cần.

Bổ sung xác minh: full unittest discover348/348qua233.388s(EXPERT_CONTINUATION_FULL_20261031.log). Restart localserver session86002/8502 lúc02:57:01VN; Chrome213freshT1snapshot94→T3snapshot95ready,khôngAPI. Đây smokeUI,không phải kiểm nội dung đủmọimôn/lớp. ChưaCloud cho thayđổi này.
