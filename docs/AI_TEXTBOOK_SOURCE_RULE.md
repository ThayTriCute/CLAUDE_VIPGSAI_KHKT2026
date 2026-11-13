# Quy luật nguồn SGK — mọi AI / mọi ca (owner 13/11/2026)

Tài liệu này là **luật vận hành**. Mọi ca AI/mô hình vào hệ thống phải đọc và tuân thủ trước khi lập gói neo, sửa grounding, hoặc sinh bài Trạm 1–3.

Rule Cursor: `.cursor/rules/textbook-source-grounding.mdc` (`alwaysApply: true`).  
Đồng bộ: `AGENTS.md`, `docs/AI_CURRICULUM_GROUNDING.md`, `ACADEMIC_GROUNDING_GUIDANCE` trong `services/curriculum_policy.py`.

## 1. Ba cổng chính thức

| # | Cổng | URL |
|---|---|---|
| 1 | VniTeach — Sách điện tử KNTT | https://www.vniteach.com/sach-dien-tu-ket-noi-tri-thuc/ |
| 2 | Tập huấn NXBGDVN | https://taphuan.nxbgd.vn/tap-huan?tab=public |
| 3 | Trường Học Số Quốc Gia (THSQG) | https://www.thsqg.vn/sach |

Đây là **ba cột thư viện** trong app — không phải ba loại sách (SGK/SGV/SBT) hay ba bộ sách khác nhau.  
Nhãn **Bộ sách Thống Nhất** trên THSQG = **KNTT thống nhất** (chủ dự án xác nhận 08/11/2026).

## 2. Ngưỡng ĐẠT khi neo / đối chiếu bài

| Kết quả đối chiếu | Trạng thái |
|---|---|
| **≥ 2 / 3** cổng đã kiểm đúng môn–lớp–cuốn–bài (có URL + locator + edition) | **ĐẠT** |
| 0 hoặc 1 cổng | **CHƯA ĐẠT** — không merge gói neo như đã đủ căn cứ |

**Không bắt buộc đủ cả 3.** Ưu tiên đủ 2 cổng rõ ràng + ghi nguồn còn thiếu.

### Không được đếm sai

- Cùng một cuốn trên nhiều cổng mà chưa đọc nội dung → chỉ là **trùng danh mục**, không tự thành 2 bằng chứng nội dung độc lập.
- Chỉ có link/danh mục → **chưa đọc sách**.
- PDF có stamp **BẢN MẪU** → không dùng làm bản chính thức thay THSQG.
- Kho F chỉ **ĐỌC**; gói neo ghi vào repo (D + GitHub).

## 3. Bắt buộc ghi rõ căn cứ khi sinh bài

Mọi gói `textbook_archive_6_12/reviewed_lesson_packets/*.json.xz` và mọi bài/đề/lời giải sinh từ grounding phải:

1. Liệt kê **sources[]** đã dùng: `title`, `url`, `locator`, `edition_note`, `reviewed_excerpt` (diễn giải đã đọc — không phải toàn văn).
2. Trong `coverage_note` / lời bàn giao: nêu **đã dùng cổng nào**, **thiếu cổng nào** trong bộ 3.
3. **Cấm** cụm từ kiểu “đã đối chiếu đủ ba nguồn” / “đủ VniTeach + NXBGD + THSQG” khi thực tế chỉ có 1–2.
4. Runtime: chỉ tin `textbook_grounding.status == reviewed_excerpt_packet_loaded`; thiếu gói → nói rõ chưa xác minh, không bịa trang/YCCĐ.

## 4. Quy trình gói neo (P3-3)

1. Đọc kho local F (nếu có) trước; thiếu thì mở ≥2 cổng online.
2. Đọc đúng bài/trang trên reader (ưu tiên THSQG bản chính thức khi có).
3. Viết gói diễn giải nhỏ (`.json.xz`) + cập nhật `index.json` (sha256).
4. Kiểm: `python -m unittest tests.test_bundled_grounding_packets tests.test_packet_source_rule -v`
5. PR → chủ dự án merge → pull về D. Không ghi F.

## 5. Phạm vi

Áp dụng **mọi môn, lớp 6–12** (THCS và THPT). Neo THCS 6–9 dùng cùng luật với THPT.
