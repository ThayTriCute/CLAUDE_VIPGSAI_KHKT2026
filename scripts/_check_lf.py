from pathlib import Path
d = Path(__file__).resolve().parents[1] / "app.py"
b = d.read_bytes()
print("lf_only", b.count(b"\n") - b.count(b"\r\n"))
print("has_grade", b"grade_exam_by_profile" in b)
print("has_fallback", "chưa sẵn sàng".encode("utf-8") in b)
