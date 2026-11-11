"""Dấu phiên bản đọc từ .git: đúng với ref rời, packed-refs, HEAD tách rời và thiếu .git."""
import tempfile
import unittest
from pathlib import Path

from services.build_info import build_info, build_label

SHA = 'a1b2c3d4e5f60718293a4b5c6d7e8f9012345678'


class BuildInfoTests(unittest.TestCase):
    def repo(self, head, loose=None, packed=None):
        root = Path(tempfile.mkdtemp())
        git = root / '.git'
        (git / 'refs/heads').mkdir(parents=True)
        (git / 'HEAD').write_text(head, encoding='utf-8')
        if loose:
            (git / 'refs/heads/main').write_text(loose + '\n', encoding='utf-8')
        if packed:
            (git / 'packed-refs').write_text(f'# pack-refs\n{packed} refs/heads/main\n', encoding='utf-8')
        return root

    def test_loose_ref(self):
        info = build_info(self.repo('ref: refs/heads/main\n', loose=SHA))
        self.assertEqual((info['sha'], info['branch']), ('a1b2c3d', 'main'))
        self.assertRegex(info['updated'], r'^\d{2}/\d{2}/\d{4} \d{2}:\d{2}$')

    def test_packed_ref_and_detached_head(self):
        self.assertEqual(build_info(self.repo('ref: refs/heads/main\n', packed=SHA))['sha'], 'a1b2c3d')
        self.assertEqual(build_info(self.repo(SHA + '\n'))['sha'], 'a1b2c3d')

    def test_missing_or_corrupt_git_is_safe(self):
        empty = {'sha': '', 'branch': '', 'updated': ''}
        self.assertEqual(build_info(Path(tempfile.mkdtemp())), empty)
        self.assertEqual(build_info(self.repo('ref: refs/heads/main\n', loose='not-a-sha')), empty)
        self.assertIn('bản cục bộ', build_label(Path(tempfile.mkdtemp())))
        self.assertTrue(build_label(self.repo(SHA)).startswith('Bản dựng: a1b2c3d'))


if __name__ == '__main__':
    unittest.main()
