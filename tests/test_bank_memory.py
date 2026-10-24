import gzip
import json
import lzma
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from services.bank_storage import BoundedCache, read_exam_shard


class TestBankMemory(unittest.TestCase):
    def test_all_formats_keep_exact_content_and_mutation_isolation(self):
        sample = [{"code": str(i), "p1": [{"q": "Một chuỗi câu hỏi lặp lại", "opt": ["cùng đáp án", "khác"], "ans": "A"}]} for i in range(3)]
        with tempfile.TemporaryDirectory() as directory:
            for suffix, opener in ((".json", open), (".json.gz", gzip.open), (".json.xz", lzma.open)):
                for root in (sample, {"exams": sample}):
                    path = Path(directory) / ("bank" + suffix)
                    with opener(path, "wt", encoding="utf-8") as stream:
                        json.dump(root, stream, ensure_ascii=False)
                    actual = read_exam_shard(path)
                    self.assertEqual(actual, sample)
                    self.assertIs(actual[0]["p1"][0]["q"], actual[1]["p1"][0]["q"])
                    actual[0]["p1"][0]["opt"][0] = "changed"
                    self.assertEqual(actual[1]["p1"][0]["opt"][0], "cùng đáp án")

    def test_lru_evicts_least_recently_used(self):
        cache = BoundedCache(2)
        cache["one"] = 1
        cache["two"] = 2
        self.assertEqual(cache.get("one"), 1)
        cache["three"] = 3
        self.assertEqual(set(cache), {"one", "three"})

    def test_explicit_removal_preserves_order_and_empty_behavior(self):
        cache = BoundedCache(3)
        for key in ("one", "two", "three"):
            cache[key] = key.upper()
        self.assertEqual(cache.popitem(last=False), ("one", "ONE"))
        self.assertEqual(cache.popitem(), ("three", "THREE"))
        self.assertEqual(cache.popitem(), ("two", "TWO"))
        with self.assertRaises(KeyError):
            cache.popitem()

    def test_scanned_exam_remix_missing_helper_regression(self):
        import real_exam_engine as engine
        exam = {"code": "qa", "p1": [{"q": "Câu hỏi chữ", "opt": ["A. 1", "B. 2"], "ans": "A"}], "p2": [], "p3": []}
        enriched = engine.enrich_exam_visuals_jit(exam, "Lịch sử", 12)
        self.assertEqual(exam["p1"][0]["ans"], enriched["p1"][0]["ans"])
        enriched["p1"][0]["opt"][0] = "changed"
        self.assertEqual(exam["p1"][0]["opt"][0], "A. 1")

    def test_third_subject_releases_derived_caches(self):
        import real_exam_engine as engine
        with patch.object(engine, "_SHARD_CACHE", BoundedCache(2)), \
             patch.object(engine, "_QUESTIONS_POOL_CACHE", BoundedCache(4)), \
             patch.object(engine, "_FAST_EXAM_LIST_CACHE", BoundedCache(8), create=True), \
             patch.object(engine, "_MULTI_INDEX_BY_TOPIC_LEVEL", {}), \
             patch.object(engine, "_MULTI_INDEX_BY_TOPIC", {}), \
             patch.object(engine, "_MULTI_INDEX_BY_PART", {}), \
             patch.object(engine, "_QUESTION_STORE_BY_QID", {}), \
             patch.object(engine, "_INDEXED_SUBJECTS", set()), \
             patch.object(engine, "get_raw_baseline_data", return_value={}), \
             patch.object(engine.os.path, "exists", return_value=False):
            engine.get_shard_exams("qa-one")
            engine.get_shard_exams("qa-two")
            engine._QUESTIONS_POOL_CACHE["old"] = ["stale"]
            engine._MULTI_INDEX_BY_PART["old"] = ["stale"]
            engine.get_shard_exams("qa-three")
            self.assertEqual(len(engine._SHARD_CACHE), 2)
            self.assertFalse(engine._QUESTIONS_POOL_CACHE)
            self.assertFalse(engine._MULTI_INDEX_BY_PART)
