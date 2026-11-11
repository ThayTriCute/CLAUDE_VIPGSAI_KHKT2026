"""Nạp ảnh bài làm học sinh an toàn: không bỏ qua im lặng, không tràn bộ nhớ.

Ảnh điện thoại 48–50MP (JPEG) được giải mã thu nhỏ ngay từ bộ giải mã (draft)
nên không cần cấp phát toàn bộ điểm ảnh. Ảnh bị từ chối luôn kèm lý do tiếng Việt.
"""
from PIL import Image, ImageOps

MAX_BYTES = 30 * 1024 * 1024
MAX_PIXELS_JPEG = 120_000_000
MAX_PIXELS_OTHER = 50_000_000
TARGET = (2200, 2200)


def load_student_image(file_obj, name="ảnh"):
    """Trả về (ảnh RGB đã thu nhỏ | None, thông báo cho học sinh | None)."""
    name = str(name or "ảnh")
    size = getattr(file_obj, "size", None)
    if isinstance(size, int) and size > MAX_BYTES:
        return None, (f"⚠️ Ảnh '{name}' nặng {size / 1048576:.0f} MB, vượt giới hạn 30 MB nên Thầy chưa nhận được. "
                      "Em chụp lại ở chế độ thường hoặc gửi ảnh chụp màn hình trang bài làm nhé.")
    try:
        file_obj.seek(0)
        with Image.open(file_obj) as raw:
            is_jpeg = (raw.format or "").upper() in ("JPEG", "MPO")
            pixels = raw.width * raw.height
            if pixels > (MAX_PIXELS_JPEG if is_jpeg else MAX_PIXELS_OTHER):
                return None, (f"⚠️ Ảnh '{name}' có độ phân giải quá lớn ({pixels / 1e6:.0f} triệu điểm ảnh) nên Thầy chưa nhận được. "
                              "Em chụp lại ở chế độ thường (không dùng chế độ 108MP/200MP) nhé.")
            if is_jpeg:
                raw.draft("RGB", TARGET)
            raw.load()
            image = ImageOps.exif_transpose(raw).convert("RGB")
        image.thumbnail(TARGET)
        return image, None
    except Exception as exc:
        text = str(exc).lower()
        if "heif" in text or "heic" in text or name.lower().endswith((".heic", ".heif")):
            return None, f"⚠️ Ảnh '{name}' lưu định dạng HEIC mà máy chủ chưa đọc được. Em hãy dùng Camera chụp trực tiếp gửi Thầy nhé!"
        return None, f"⚠️ Thầy chưa đọc được ảnh '{name}' (tệp có thể bị hỏng hoặc không phải ảnh). Em chọn lại ảnh khác nhé."
