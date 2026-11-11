"""Trạm 2: ảnh bài làm lớn/hỏng không được bỏ qua im lặng."""
import io
import unittest

from PIL import Image

from services.upload_images import MAX_BYTES, load_student_image


def photo(width, height, fmt="JPEG", exif_orientation=None):
    buf = io.BytesIO()
    image = Image.new("RGB", (width, height), (250, 250, 250))
    kwargs = {}
    if exif_orientation:
        exif = Image.Exif(); exif[0x0112] = exif_orientation; kwargs["exif"] = exif
    image.save(buf, fmt, **kwargs)
    buf.seek(0)
    return buf


class LoadStudentImageTests(unittest.TestCase):
    def test_50mp_phone_jpeg_is_accepted_and_downscaled(self):
        image, notice = load_student_image(photo(8160, 6120), "bai.jpg")
        self.assertIsNone(notice)
        self.assertLessEqual(max(image.size), 2200)
        self.assertEqual(image.mode, "RGB")

    def test_rotated_phone_photo_is_stood_upright(self):
        image, _ = load_student_image(photo(400, 200, exif_orientation=6), "xoay.jpg")
        self.assertEqual(image.size, (200, 400))

    def test_png_and_webp_accepted(self):
        for fmt in ("PNG", "WEBP"):
            with self.subTest(fmt=fmt):
                image, notice = load_student_image(photo(1200, 900, fmt), f"a.{fmt.lower()}")
                self.assertIsNone(notice)
                self.assertEqual(image.size, (1200, 900))

    def test_every_rejection_has_a_message(self):
        class Huge(io.BytesIO):
            size = MAX_BYTES + 1
        cases = {
            "nang.jpg": Huge(b"x"),
            "hong.jpg": io.BytesIO(b"not an image"),
            "anh.heic": io.BytesIO(b"\x00\x00\x00\x18ftypheic"),
            "qua-lon.png": photo(8000, 7000, "PNG"),
        }
        for name, data in cases.items():
            with self.subTest(name=name):
                image, notice = load_student_image(data, name)
                self.assertIsNone(image)
                self.assertIn(name, notice)

    def test_app_no_longer_skips_uploads_silently(self):
        with open("app.py", encoding="utf-8") as handle:
            source = handle.read()
        self.assertIn("load_student_image(up_f", source)
        self.assertNotIn("up_f.size > 12 * 1024 * 1024", source)


if __name__ == "__main__":
    unittest.main()
