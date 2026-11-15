# Nhật ký bàn giao — GSAI KHKT 2026

> Ca sau **đọc file này trước** khi sửa Trạm 1 / Trạm 3 / Socratic / JSON đề AI.  
> Cập nhật: **2026-11-16 ~01:45 giờ VN**. Người ghi: ca trợ lý (theo lệnh anh MINH).  
> Repo nguồn: `ThayTriCute/CLAUDE_VIPGSAI_KHKT2026`. `main` = **`b0e4f07`** (PR **#123**).  
> App Cloud: `https://claudevipgsaikhkt2026-bybgceinifcaqggqyyvatx.streamlit.app/`  
> Worktree máy anh: `D:\CLAUDE_FINAL KHKT 2026\_gh_compare`.

Mỗi lần vá code phải **cập nhật mục “Ca gần nhất”** của file này (và commit cùng PR), không viết nhật ký chỉ trong chat.

---

## 0. Chốt sư phạm — không được làm ngược

Anh MINH chốt (16/11/2026), áp **mọi môn × mọi khối 6–12**, Trạm 1 và Trạm 3:

1. HD Socratic là **lời thầy bình dân học vụ**: học sinh phải hiểu ngữ liệu câu hỏi **đang bắt làm gì**, **áp dụng công thức / thước đo nào**, **tư duy theo con đường nào** để tự đi tới đáp án.
2. HD **sát đúng câu AI vừa sinh** (stem + dữ kiện + trụ phương án). Cấm echo chung kiểu “Hướng đi từ đúng ngữ liệu: …” rồi nhắc lại nguyên câu.
3. **Tuyệt đối không giải hộ, không lộ đáp án:** không gắn chữ A–D, không Đúng/Sai hộ, không đáp số cuối, không thay số ra kết quả, không lấy field `explain` làm HD.
4. Khung chữ trên UI: **Công thức / hướng (thầy chỉ lối, không giải hộ)** rồi **Con đường tư duy** (tối đa 4 bước; câu khó giữ đủ bước).
5. Expander HD **mở được lúc đang làm bài**. `explain` chỉ sau khi nộp.
6. Tham chiếu kiểu đỡ đẻ: F VIP `computing_context_question` / Maieutics trong `F:\FINAL KHKT 2026\tmp\voice_https_worker\services\socratic_context.py` — học cách hỏi, **không** copy cả app VIP, **không** port wellbeing Trạm 4/5.

Hàm duy nhất: `build_tram3_socratic_guide` (= `build_socratic_guide`) trong `services/socratic_context.py`.  
`T1_CONTEXT_REVISION` của module đó **phải khớp** số trong `_refresh_t1_context_services()` của `app.py`. Hiện tại: **`2026111604`**.

---

## 1. Ca gần nhất — đêm 16/11/2026 (đã vào main)

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
