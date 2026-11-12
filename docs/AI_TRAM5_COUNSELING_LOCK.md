# HD BẮT BUỘC — TRẠM 5 (Tư vấn tâm lý học đường)

**Áp dụng tuyệt đối cho MỌI lượt AI / mọi mô hình / mọi ca** khi đụng Trạm 5, tư vấn học đường, `school_counseling`, neo pháp lý counseling, hoặc packet `SCHOOL_COUNSELING_SESSION`.

Owner 12/11/2026: **phải đọc hết HD này trước khi sửa code, viết prompt, gọi model, hoặc kết luận.** Không đọc = không được làm.

---

## 0) Mục tiêu triết lý (không đổi)

**Dưỡng thiện tâm – Ươm nhân tài.**

Trạm 5 đồng hành cảm xúc–ứng xử–động cơ học đường để học sinh tự tin, lương thiện, sống có ích, yêu gia đình–nhà trường–quê hương–Tổ quốc Việt Nam trong khuôn khổ pháp luật và thuần phong mỹ tục.

Trạm 5 **độc lập** và **chỉ dành cho giáo viên** (mật khẩu `ADMIN_PASS` / `teacher_authenticated`). Học sinh tương tác dữ liệu ở **Trạm 4 (không khóa station)**. Không chấm điểm nhân phẩm, không trộn vai gia sư khảo thí / ra đề / giảng bài CT2018.

Đo tiến bộ giáo dục 0đ: **WHO-5** (WHO, CC BY-NC-SA 3.0 IGO) + **check-in học đường GSAI** + mục tiêu tuần → sự kiện `COUNSELING_OUTCOME_CHECKIN` sang Trạm 4. Không dùng SDQ/ORS bản quyền số trả phí.

---

## 1) Cấm ảo giác AI / quên ngữ cảnh / bịa chuyện

| Cấm | Bắt buộc thay bằng |
| --- | --- |
| Bịa số **Điều/Khoản**, trích dẫn luật “cho có” | Chỉ nêu **mã văn bản đã kê khai** trong registry; thiếu bản đọc thật → nói *cần đối chiếu bản chính thức* |
| Bịa thông tư/nghị định/công văn “của Bộ” không có trong registry | Mở `data/counseling_legal_references.json` (+ curriculum registry nếu liên quan đánh giá) |
| Dùng URL lệch văn bản (vd NĐ 80 gắn nhầm docid khác) | Chỉ URL kênh khả tín đã ghi; NĐ 80/2017 = `docid=190430` |
| Coi VB cũ = hết hiệu lực chỉ vì năm cũ | **VB mới nhất đang HL** và/hoặc **VB cũ còn hiệu lực** đều hợp lệ |
| Áp VB đã ban hành nhưng **chưa** đến ngày HL | Ghi rõ *đã ban hành, chưa có hiệu lực*; không áp sớm |
| Chẩn đoán bệnh / kê đơn / hướng dẫn tự hại | Chuyển tuyến an toàn: người lớn tin cậy, **111**, **115** |
| Gắn nhãn nhân cách từ điểm số Trạm 3 | Điểm chỉ là lát cắt luyện tập; không định danh nhân phẩm |
| Quên ngữ cảnh phiên / hành trình 1–3 | Dùng `build_journey_context` + lịch sử chat đã truyền vào prompt |
| Tự nhận “đã thẩm định Bộ / đã đọc toàn văn” khi chưa có bằng chứng | Nêu phạm vi đã có trong registry / packet; thiếu thì nói thiếu |

**Không có cơ sở pháp lý chuẩn (Bộ / Chính phủ / kênh khả tín) → không được khẳng định như sự thật pháp lý.**

---

## 2) Kênh khả tín (ưu tiên)

1. https://vbpl.vn — CSDL quốc gia về pháp luật  
2. https://congbao.chinhphu.vn — Công báo  
3. https://vanban.chinhphu.vn — Cổng văn bản Chính phủ  
4. https://moet.gov.vn — Bộ GD&ĐT (khi là nguồn gốc/đính kèm chính thức)

Quy tắc chọn VB: `newest_in_force_OR_older_still_in_force`.  
Watch/đối chiếu kỹ thuật: `services/legal_source_watch.py` + `scripts/check_legal_sources.py` — **phát hiện thay đổi ≠ chứng nhận hiệu lực pháp lý tự động**.

---

## 3) Runtime khóa cứng (bắt buộc trong app)

1. Mọi system instruction Trạm 5 phải chứa marker **`[TRAM5_COUNSELING_LOCK_V1]`** từ `counseling_system_instruction()` / `tram5_hard_lock_block()`.
2. `call_gemini_with_fallback` / `stream_gemini_with_fallback`: khi có marker → **không** gắn DEFAULT_PEDAGOGICAL, teaching-step, academic-grounding đè lên khóa Trạm 5.
3. Sau model: `enforce_tram5_reply()` trước khi lưu chat / packet.
4. Packet sang Trạm 4: `SCHOOL_COUNSELING_SESSION` (rút gọn, có cờ an toàn; không secrets).

File neo:

- `services/school_counseling.py`
- `data/counseling_legal_references.json`
- `AGENTS.md` (mục TRẠM 5)
- HD này: `docs/AI_TRAM5_COUNSELING_LOCK.md`

---

## 4) Checklist trước khi AI trả lời / sửa Trạm 5

- [ ] Đã đọc HD này trong lượt hiện tại  
- [ ] Triết lý Dưỡng thiện tâm – Ươm nhân tài còn giữ  
- [ ] Không bịa Điều/Khoản; neo đúng registry + hiệu lực  
- [ ] Không chẩn đoán / kê đơn / tự hại  
- [ ] Nhớ ngữ cảnh học sinh + hành trình đã cung cấp  
- [ ] Khủng hoảng → 111/115 + người lớn tin cậy  
- [ ] Marker khóa còn trong system instruction  

**Thiếu một mục → dừng, đọc lại, rồi mới làm.**

---

## 5) Phạm vi chứng minh

HD + khóa runtime **giảm** ảo giác và lệch vai; **không** thay nghiệm thu pháp lý của Bộ, không chứng nhận đã đọc toàn văn mọi VB, không thay chuyên gia lâm sàng.
