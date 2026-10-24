"""Read large exam shards incrementally; share only immutable strings."""
import gzip
import lzma
from collections import OrderedDict
from pathlib import Path

import ijson


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


def read_exam_shard(path):
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
        return [compact(exam) for exam in ijson.items(stream, prefix, use_float=True)]
