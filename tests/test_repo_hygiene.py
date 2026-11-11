"""Kho mã CÔNG KHAI: không được chứa khóa API, URL webhook hay mật khẩu thật.

Quét mọi tệp văn bản được Git theo dõi. Mẫu dò chỉ là dạng khóa (không chứa giá trị thật).
"""
import re
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATTERNS = {
    'Google API key': re.compile(rb'AIza[0-9A-Za-z_\-]{35}'),
    'Apps Script webhook': re.compile(rb'script\.google\.com/macros/s/AK[0-9A-Za-z_\-]{20,}'),
    'Supabase/JWT secret': re.compile(rb'eyJ[0-9A-Za-z_\-]{20,}\.[0-9A-Za-z_\-]{20,}\.[0-9A-Za-z_\-]{20,}'),
    'Private key block': re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
}


def tracked_files():
    try:
        out = subprocess.run(['git', 'ls-files', '-z'], cwd=ROOT, capture_output=True, timeout=30, check=True).stdout
    except (OSError, subprocess.SubprocessError):
        return None
    return [ROOT / p.decode('utf-8', 'replace') for p in out.split(b'\0') if p]


class RepoHygieneTests(unittest.TestCase):
    def test_no_secret_shaped_strings_in_tracked_files(self):
        files = tracked_files()
        if files is None:
            self.skipTest('Không phải bản Git (ví dụ thư mục tải zip).')
        leaks = []
        for path in files:
            try:
                if not path.is_file() or path.stat().st_size > 5_000_000:
                    continue
                data = path.read_bytes()
            except OSError:
                continue
            for label, pattern in PATTERNS.items():
                if pattern.search(data):
                    leaks.append(f'{label}: {path.relative_to(ROOT)}')
        self.assertEqual(leaks, [], 'Phát hiện chuỗi dạng bí mật trong kho công khai — gỡ và ĐỔI khóa ngay.')


if __name__ == '__main__':
    unittest.main()
