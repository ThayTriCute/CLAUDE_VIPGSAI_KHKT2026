"""Dấu phiên bản đang chạy, đọc trực tiếp từ thư mục .git (không gọi tiến trình con).

Dùng để chủ dự án và các ca AI xác minh Cloud đã cập nhật đúng commit hay chưa.
Không có .git (bản tải zip) thì trả 'bản cục bộ'; mọi lỗi đọc đều trả an toàn.
"""
from datetime import datetime, timedelta, timezone
from pathlib import Path

T1_CONTEXT_REVISION = 2026111101
_ROOT = Path(__file__).resolve().parents[1]


def _resolve_ref(git_dir, ref):
    loose = git_dir / ref
    if loose.is_file():
        return loose.read_text(encoding='utf-8').strip(), loose.stat().st_mtime
    packed = git_dir / 'packed-refs'
    if packed.is_file():
        for line in packed.read_text(encoding='utf-8').splitlines():
            parts = line.split()
            if len(parts) == 2 and parts[1] == ref:
                return parts[0], packed.stat().st_mtime
    return '', 0.0


def build_info(root=None):
    """{'sha': 7 ký tự hoặc '', 'branch': tên nhánh hoặc '', 'updated': 'dd/mm/yyyy HH:MM' giờ VN hoặc ''}."""
    empty = {'sha': '', 'branch': '', 'updated': ''}
    try:
        git_dir = Path(root or _ROOT) / '.git'
        head = (git_dir / 'HEAD').read_text(encoding='utf-8').strip()
        if head.startswith('ref:'):
            ref = head.split(':', 1)[1].strip()
            sha, mtime = _resolve_ref(git_dir, ref)
            branch = ref.rsplit('/', 1)[-1]
        else:
            sha, mtime, branch = head, (git_dir / 'HEAD').stat().st_mtime, ''
        if len(sha) < 7 or any(c not in '0123456789abcdef' for c in sha.lower()):
            return empty
        updated = datetime.fromtimestamp(mtime, timezone(timedelta(hours=7))).strftime('%d/%m/%Y %H:%M') if mtime else ''
        return {'sha': sha[:7], 'branch': branch, 'updated': updated}
    except (OSError, ValueError, UnicodeError):
        return empty


def build_label(root=None):
    info = build_info(root)
    if not info['sha']:
        return 'Bản dựng: bản cục bộ (không có thông tin Git)'
    tail = f" · cập nhật {info['updated']}" if info['updated'] else ''
    return f"Bản dựng: {info['sha']}{tail}"
