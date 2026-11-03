"""Read large exam shards incrementally; share only immutable strings."""
import gzip
import lzma
import hashlib
import json
from copy import deepcopy
from collections import OrderedDict
from pathlib import Path

import ijson


def mark_ai_exam_provenance(exam):
    """Do not launder a generated exam into an official school paper."""
    result = deepcopy(exam)
    result.update(is_ai_harvested=True, is_real_bank_question=False,
                  provenance_kind='ai_generated', source_verification='not_official_exam')
    for part in ('p1', 'p2', 'p3', 'part_viet'):
        for question in result.get(part, []) or []:
            if isinstance(question, dict):
                question.update(is_ai_generated=True, is_real_bank_question=False,
                    provenance_kind='ai_generated', source_verification='not_official_exam')
    return result


def calibration_eligibility(question, review, *, subject, grade, part):
    """Separate legacy practice material from independently verified anchors.

    Review must come from the maintained source-review registry, not question
    metadata. An ADN, famous school name or is_real flag cannot approve a task.
    """
    reasons = []
    if question.get('is_ai_generated') or question.get('provenance_kind') == 'ai_generated':
        reasons.append('generated_material_not_official_anchor')
    identity = content_identity(question, subject=subject, grade=grade, part=part,
                                shared_context=question.get('shared_context'))
    if not isinstance(review, dict):
        review = {}
    if review.get('content_adn') != identity['content_adn']:
        reasons.append('no_matching_independent_content_review')
    if (review.get('subject'), review.get('grade'), review.get('part')) != (subject, grade, part):
        reasons.append('review_context_mismatch')
    for field in ('paper_source_url', 'paper_sha256', 'answer_source_url', 'answer_sha256',
                  'source_locator', 'reviewer', 'reviewed_on', 'curriculum_outcome_locator'):
        if not isinstance(review.get(field), str) or not review[field].strip():
            reasons.append('missing_' + field)
    for field in ('original_item_match', 'answer_check', 'curriculum_mapping'):
        if review.get(field) != 'passed':
            reasons.append('unverified_' + field)
    if review.get('unresolved_issues'):
        reasons.append('unresolved_source_or_answer_issue')
    return {'eligible': not reasons, 'reasons': reasons,
            'content_adn': identity['content_adn'],
            'scope': 'reference_anchor_eligibility_not_ministry_level_certification'}


def content_identity(question, *, subject, grade, part, shared_context=None):
    """A reproducible content ID is not a certificate of correct knowledge."""
    from dedupe_bank import q_fingerprint
    payload = [str(subject), str(grade), str(part), q_fingerprint(question), shared_context or {}]
    digest = hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True,
        separators=(',', ':')).encode()).hexdigest()
    result = dict(question)
    legacy = list(result.get('legacy_qids') or [])
    old = result.get('qid')
    new = 'ADN1_' + digest
    if old and old != new and old not in legacy:
        legacy.append(old)
    result.update(qid=new, content_adn=digest, identity_revision='sha256-exact-v1', legacy_qids=legacy)
    return result


class BoundedCache(OrderedDict):
    """Small LRU; caller serializes compound cache operations."""
    def __init__(self, max_entries):
        super().__init__()
        self.max_entries = max_entries

    def __getitem__(self, key):
        value = super().__getitem__(key)
        self.move_to_end(key)
        return value

    def get(self, key, default=None):
        return self[key] if key in self else default

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        self.move_to_end(key)
        while len(self) > self.max_entries:
            self.popitem(last=False)

    def popitem(self, last=True):
        # Python 3.10's OrderedDict.popitem can re-enter our __getitem__ after
        # unlinking the key. Its recency update then raises KeyError. Remove
        # explicitly through base methods so eviction never refreshes recency.
        if not self:
            raise KeyError("dictionary is empty")
        key = next(reversed(self)) if last else next(iter(self))
        value = super().__getitem__(key)
        super().__delitem__(key)
        return key, value


def iter_exam_shard(path, grade=None):
    """Support JSON object/array and XZ/GZ without materializing the JSON text.

    Questions remain independent mutable dictionaries. Repeated question text and
    option strings share storage, without changing their values or provenance.
    """
    path = Path(path)
    opener = lzma.open if path.suffix == ".xz" else gzip.open if path.suffix == ".gz" else open
    strings = {}

    def compact(value):
        if isinstance(value, str):
            # Bound the temporary intern table for unexpected/user-produced banks.
            if value in strings:
                return strings[value]
            if len(strings) < 50000:
                strings[value] = value
            return value
        if isinstance(value, list):
            for i, item in enumerate(value):
                value[i] = compact(item)
        elif isinstance(value, dict):
            return {compact(key): compact(item) for key, item in value.items()}
        return value

    with opener(path, "rb") as stream:
        first = stream.read(1)
        while first and first.isspace():
            first = stream.read(1)
        if first not in (b"{", b"["):
            raise ValueError("Exam bank must be a JSON object or array")
        stream.seek(0)
        prefix = "exams.item" if first == b"{" else "item"
        for exam in ijson.items(stream, prefix, use_float=True):
            if grade is not None and str(exam.get('grade')) != str(grade):
                continue
            yield compact(exam)


def read_exam_shard(path, grade=None):
    """Compatibility list API; streaming consumers should use iter_exam_shard."""
    return list(iter_exam_shard(path, grade=grade))


def append_exam_atomic(path, exam):
    """Idempotent exact import; reject conflicting identity and concurrent writes."""
    import os
    import tempfile
    path = Path(path)
    before = hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None
    rows = list(iter_exam_shard(path)) if path.exists() else []
    fields = ('subject', 'grade', 'year', 'code', 'school', 'exam_type')
    identity = lambda row: tuple(str(row.get(k, '')) for k in fields)
    def payload(row):
        return {k: v for k, v in row.items() if k != 'added_at'}
    for row in rows:
        if identity(row) == identity(exam):
            if payload(row) == payload(exam):
                return False
            raise ValueError('Conflicting existing exam identity; review before replacement')
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary = tempfile.mkstemp(prefix=path.name + '.', suffix='.tmp', dir=path.parent)
    os.close(handle)
    try:
        with lzma.open(temporary, 'wt', encoding='utf-8', preset=6) as stream:
            json.dump({'exams': [exam] + rows, 'total': len(rows) + 1}, stream, ensure_ascii=False)
        current = hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None
        if current != before:
            raise RuntimeError('Shard changed during import; no overwrite performed')
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    return True
