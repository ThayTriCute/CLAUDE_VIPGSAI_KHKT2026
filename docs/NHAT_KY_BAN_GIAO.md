# Nhật ký bàn giao — GSAI KHKT 2026

> Ca sau **đọc file này trước** khi sửa Trạm 1 / Trạm 3 / Socratic / JSON đề AI.  
> Cập nhật: **2026-11-16 ~08:45 giờ VN**. Người ghi: ca trợ lý (theo lệnh anh MINH).  
> Repo nguồn: `ThayTriCute/CLAUDE_VIPGSAI_KHKT2026`. `main` trước PR giọng nói này = **`68ae144`** (PR **#124**).  
> App Cloud: `https://claudevipgsaikhkt2026-bybgceinifcaqggqyyvatx.streamlit.app/`  
> Worktree máy anh: `D:\CLAUDE_FINAL KHKT 2026\_gh_compare`.

Mỗi lần vá code phải **cập nhật mục “Ca gần nhất”** của file này (và commit cùng PR), không viết nhật ký chỉ trong chat.

---

## 0. Chốt sư phạm — không được làm ngược

Anh MINH chốt (16/11/2026), áp **mọi môn × mọi khối 6–12**, Trạm 1 và Trạm 3:

1. HD Socratic là **lời thầy bình dân học vụ**: học sinh phải hiểu ngữ liệu câu hỏi **đang bắt làm gì**, **áp dụng công thức / thước đo nào**, **tư duy theo con đường nào** để tự đi tới đáp án.
2. HD **sát đúng câu AI vừa sinh** (stem + dữ kiện + trụ phương án). Cấm echo chung kiểu “Hướng đi từ đúng ngữ liệu: …” rồi nhắc lại nguyên câu.
3. **Tuyệt đối không giải hộ, không lộ đáp án:** không gắn chữ A–D, không Đúng/Sai hộ, không đáp số cuối, không thay số ra kết quả, không lấy field `explain` làm HD.
4. Lời HD là **1–2 câu hỏi**, **tối đa 3 dòng**, xưng thầy–em. Cấm tiêu đề máy móc và các chữ: "Ngữ liệu", "Việc 1", "Trích xuất dữ kiện", "Đề cho". Không đánh số bước.
5. Expander HD **mở được lúc đang làm bài**. `explain` chỉ sau khi nộp.
6. Tham chiếu kiểu đỡ đẻ: F VIP `computing_context_question` / Maieutics trong `F:\FINAL KHKT 2026\tmp\voice_https_worker\services\socratic_context.py` — học cách hỏi, **không** copy cả app VIP, **không** port wellbeing Trạm 4/5.

Hàm duy nhất: `build_tram3_socratic_guide` (= `build_socratic_guide`) trong `services/socratic_context.py`.  
`T1_CONTEXT_REVISION` của module đó **phải khớp** số trong `_refresh_t1_context_services()` của `app.py`. Hiện tại: **`2026111605`**.

---

## 1. Ca gần nhất — bốn luật cho nút Trộn siêu đề

Anh chốt 16/11: máy trộn Trạm 3 tự mâu thuẫn. Radio, panel, Ngữ văn, Tin học 12, Word/PDF, quét link, nạp đề thật và phòng làm bài **giữ nguyên**. Sửa `generate_blended_real_exam` và cổng mở đề.

1. Chip là lệnh chủ đề. Câu mẫu trong ô (“Chỉ lấy Bài 1, 2, 3 không lấy Oxyz…”) không phải lệnh (`effective_custom_prompt`). Không đè câu kho bằng mẫu khung synthetic.
2. Lọc theo field topic. Không khớp thì chỉ xét đề bài học sinh đọc. Lời giải không được kéo câu vào đề và không được cấm câu. Hết câu đúng chip thì báo thiếu, không vét cả môn.
3. Điểm hình (`f` / bảng biến thiên / mã vẽ) chỉ xếp trong tập đã lọc. Bỏ trùng theo đề bài trước khi đếm. Không nới họ mẫu rồi xóa sau khiến đề ngắn.
4. Đề kho và đề AI dùng một cổng: còn câu chơi được thì để riêng câu hỏng (`withheld_unplayable`) và mở phần còn lại. Hết câu chơi được thì vẫn chặn. Không bịa đáp án. Ô AI thay thế vẫn tối đa 2 câu và mặc định tắt.

Cảnh báo thiếu câu nói đúng số đang có, không còn câu “mở từ kho cùng môn–lớp”.

- File: `real_exam_engine.py`, `services/context_recovery.py`, `services/recovery_diagnostics.py`, `app.py`.
- Test: `tests/test_tram3_mix_one_law.py`. Đổi kỳ vọng đề kho ở `tests/test_ai_exam_incomplete.py` và `tests/test_context_recovery.py` (câu kho trùng không dùng lại thì để riêng, không chặn cả bài).
- Việc còn: hồi quy đầy đủ máy local, push nhánh, CI. Chưa merge. Chưa nghiệm thu live Cloud.
- Chọn đề có sẵn (radio “Làm nguyên đề thi thật” và kho offline): nạp `copy_stored_exam`, đúng toàn bộ câu và thứ tự của đề đã lưu. Không đi qua `enrich_exam_data`, nên không trộn và không để riêng câu.

## 1c. Ca trước — đề AI không chết cả bài vì một câu lệch

Ảnh Cloud 16/11 ~02:06: hai lần “Đã nhận phản hồi từ AI” rồi `Lỗi khởi tạo đề thi: Còn câu chưa đủ dữ liệu/đáp án hoặc chưa khớp yêu cầu… chưa mở lượt làm bài này.` Checkbox “Cho phép AI sinh nguyên câu thay thế” đang bật. `validate_exam_data` đã qua (nếu không, câu lỗi sẽ khác). `enrich_exam_data` gọi `repair_exam_context`; **một** câu `needs_review` làm `unresolved > 0` và hủy cả đề.

- Đề kho và đề AI cùng để riêng câu hỏng khi còn câu chơi được. Mục 1 (bốn luật) thay câu “đề kho giữ chặn cả bài” ở dưới.
- Bảng số liệu viết ngay trong stem (cột `|` hoặc ít nhất 3 dòng có số) không bị coi là thiếu hình. “Hình bên / đồ thị sau / bảng biến thiên” không có dữ liệu hình vẫn là lỗi.
- Khóa `B.` hoặc đúng nguyên văn phương án được đưa về A–D. Không khớp phương án nào thì không gán chữ.
- Câu hỏi **số cực trị** mà phương án là khoảng/lời văn không bị SymPy kết luận ảo giác. Phương án đếm (“2 điểm”, “có 2 cực trị”) vẫn đối chiếu.
- Màn làm bài hiện cảnh báo số câu đã để riêng.
- Test mới: `tests/test_ai_exam_incomplete.py`.
- CI PR #126 đỏ vì ba việc cũ trên main cộng khóa `withheld`: gộp hai mảng `p1` trùng khóa (không bỏ câu); `\n` trước `y'` của bảng biến thiên được tách dòng nhưng `\nearrow` giữ nguyên; JSON cắt vẫn từ chối, khóa `replacement_question` lặp thì giữ câu đã viết; đề Ngữ văn ghi `withheld: 0`.

## 1a. Ca trước — giọng HD Socratic (đã vào main #125)

Anh chốt lại lời thầy: chỉ hỏi để em tự nhớ công thức, không liệt kê.

- Hàm hiện: `_plain_midwife` trong `services/socratic_context.py`. `build_tram3_socratic_guide` chỉ in tối đa 3 dòng.
- `T1_CONTEXT_REVISION` = **`2026111605`** (khớp `app.py`).
- Câu ĐHPT mẫu: hỏi giả thiết chuyển động hỗn loạn, nhiệt độ–tốc độ, khoảng cách–kích thước, lực tương tác; em tự chỉ ý lệch. Không viết “rất mạnh”, không gắn A–D.
- Test: `test_socratic_stem_bound_multidiscipline` + `test_tram3_socratic_guide` và hồi quy hint = 34 OK.
- Việc còn: merge PR này, reload Cloud, mở expander câu ĐHPT xem đủ 3 dòng hỏi.

## 1b. Đêm 16/11/2026 đã vào main trước đó

| PR | Merge trên main | Việc |
|----|-----------------|------|
| #117 | `1367e3b` | AI JSON thử lại 1 lần khi khóa trùng; gói THCS Bài 2; HD GTLN bậc hai |
| #118 | `f7cae2b` | BBT Trạm 1: bảng xẹp, mũi tên, vá tại chỗ |
| #119 | `fb4d06b` | HD Socratic bắt đầu bám stem (nóng chảy vs hóa hơi vs \(mc\Delta T\)); Trạm 1 dùng cùng builder |
| #120 | `6004c9d` | Đỡ đẻ mô hình động học phân tử; hết echo generic |
| #122 | `a1a6ecf` | **Cloud sập** `ImportError: is_duplicate_key_error`. Import `services.ai_json` đưa lên đầu file, có fallback; bỏ import lồng trong `except` |
| #121 | `836d21e` | HD **bình dân**: thước đo SGK + con đường tư duy. ĐHPT 4 giả thiết; xác suất bám số liệu đề; Địa ĐBSCL; Ngữ đọc hiểu không lẫn nghị luận 200 chữ; chặn bleed \(pV=nRT\) sang môn khác. Conflict `app.py` với #122 chỉ là dòng trống — đã gộp, giữ cả hai |
| #123 | `b0e4f07` | AI lặp khóa **mảng** (`p1`/`p2`/`opt`…): **gộp câu đã sinh**, bỏ trùng nguyên văn. Giá trị giống nhau giữ một. Scalar mâu thuẫn (`ans` A khác B) **vẫn từ chối**. Không bịa câu |

### File đụng

- `services/socratic_context.py` — `_teacher_path_guide`, `_subject_stem_guide`, `_option_axis_labels` (trụ theo môn, không khớp nhầm “nhiệt độ” ↔ “nhiệt đới”), GTLN/xác suất giữ đường toán cũ.
- `data/socratic_anchors.py` — neo ĐHPT; từ khóa “nhiệt độ” tách khỏi neo nóng chảy; Ngữ văn ưu tiên đọc hiểu.
- `app.py` — revision `2026111604`; import `ai_json` an toàn; luồng tạo đề không import lại trong `except`.
- `services/ai_json.py` — `_merge_duplicate_values`.
- `services/__init__.py` — có, để Cloud nhận package.
- Test: `tests/test_socratic_stem_bound_multidiscipline.py`, `tests/test_tram3_socratic_guide.py`, `tests/test_ai_exam_json_clean.py` (+ subject / fallback / numeric). Ca này: stem-bound + tram3 = 17 OK; ai_json = 6 OK.

### Ảnh anh đã gửi — ý nghĩa, đừng hiểu sai

1. Câu Vật lý “Phát biểu nào **không đúng** về mô hình động học phân tử chất khí” mà HD còn “Hướng đi từ đúng ngữ liệu…” → **chưa đạt**. Bản #121 phải ra 4 giả thiết + 4 trụ (nhiệt độ–tốc độ, hỗn loạn, lực tương tác, kích thước/khoảng cách) và bước “tìm ý lệch”. **Không** được viết “lực tương tác rất mạnh” (đó là phương án sai).
2. Trang đỏ `ImportError … services.ai_json` → #122. Hết traceback thì Cloud sống lại.
3. “Lỗi khởi tạo đề thi: JSON có khóa trùng…” sau một lần thử lại → #123 gộp mảng. Nếu vẫn đỏ vì **ans/số mâu thuẫn**, đó là từ chối đúng, không gộp bừa.

### Việc ca sau làm ngay (chưa nghiệm thu live)

- [ ] Đợi Streamlit Cloud redeploy `b0e4f07`. Reload app.
- [ ] Mở lại đúng câu ĐHPT: expander phải có **Con đường tư duy**, không còn echo nguyên câu hỏi.
- [ ] Bấm **Khởi tạo đề mới**: nếu AI chỉ lặp khóa mảng, đề phải vào màn làm bài, không chết cả luồng.
- [ ] Không đụng Trạm 4/5 tư vấn. Không computer-use. Key Gemini là của anh, không ghi vào repo/nhật ký.

---

## 2. Luật cho mọi ca sau

1. Sửa xong thì **ghi tiếp mục mới trên đầu file này** (ngày, PR, SHA, file, test, việc còn mở) và commit **trong cùng PR** với code.
2. Không xóa chốt sư phạm mục 0.
3. Không lưu khóa API, mật khẩu, tên/điểm học sinh vào nhật ký hay Git.
4. `app.py` xuống dòng lẫn CRLF/LF — sửa bằng thay đúng đoạn, không format cả file.
5. PowerShell không dùng `&&`. Git commit dùng `git -c user.name=... -c user.email=...` (không `git config`).
6. HD Socratic: thêm chủ đề mới thì viết **thước đo + 3–4 việc**, có dữ kiện đề nếu đề cho số; cấm câu mẫu “nhắc định nghĩa rồi đối chiếu” khi đã biết hiện tượng.

---

## 3. Mốc cũ vẫn còn hiệu lực

Nhật ký Trạm 3 trước đêm 16/11 (PR #75–#116, live mẫu 6–12, không lộ đáp, explain sau nộp) nằm ở bàn giao ca 14–15/11. Không phá radio/portal/BBT đã ship (#111–#118).
