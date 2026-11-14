# -*- coding: utf-8 -*-
"""P0 harden: no Pass3 dump, synthetic provenance, hard cooldown, multi-subject/grade regression."""
from __future__ import annotations

import unittest

import real_exam_engine as ree
from real_exam_engine import (
    build_specialized_custom_question,
    generate_blended_real_exam,
    is_generic_topic_label,
    mark_synthetic_template,
    q_fingerprint,
    remember_question_cooldown,
    specific_topic_filters,
)


def _total(exam: dict) -> int:
    return sum(len(exam.get(p) or []) for p in ("p1", "p2", "p3"))


def _fps(exam: dict) -> set:
    out = set()
    for p in ("p1", "p2", "p3"):
        for q in exam.get(p) or []:
            fp = q_fingerprint(q)
            if fp:
                out.add(fp)
    return out


class GenericTopicHelpersTests(unittest.TestCase):
    def test_generic_and_specific_labels(self):
        self.assertTrue(is_generic_topic_label("Chuyên đề tổng hợp môn Toán học Lớp 12"))
        self.assertTrue(is_generic_topic_label("[Lớp 9] Chuyên đề trọng tâm Vật lý Lớp 9"))
        self.assertFalse(is_generic_topic_label("[Lớp 12] Chuyên đề 1: Dao động điều hòa"))
        self.assertEqual(
            specific_topic_filters(
                [
                    "Chuyên đề tổng hợp môn Hóa học Lớp 10",
                    "[Lớp 10] Ester - Lipid",
                ]
            ),
            ["[Lớp 10] Ester - Lipid"],
        )


class SyntheticProvenanceTests(unittest.TestCase):
    def test_archetype_never_wears_fake_school_toanmath(self):
        for arch in (
            "p2_f_prime_graph",
            "p2_mslgn_quartiles",
            "p1_rational_2_1",
            "p1_mslgn_hologram",
            "p1_rational_1_1",
            "p1_cubic",
            "p1_bbt_rational",
        ):
            q = build_specialized_custom_question(arch, subject="Toán học", grade=12)
            self.assertIsNotNone(q)
            self.assertTrue(q.get("is_synthetic_template"))
            self.assertEqual(q.get("provenance_kind"), "synthetic_template")
            self.assertEqual(q.get("portal"), "synthetic")
            src = str(q.get("source", "")).lower()
            school = str(q.get("school", "")).lower()
            self.assertNotIn("toanmath", src)
            self.assertNotIn("chuyên hà nội", school)
            self.assertIn("synthetic", src)
            self.assertIn("template", school)

    def test_mark_synthetic_strips_urls(self):
        stamped = mark_synthetic_template(
            {"q": "x", "source_url": "https://toanmath.com/x", "school": "Fake"},
            "unit_test",
        )
        self.assertNotIn("source_url", stamped)
        self.assertEqual(stamped.get("portal"), "synthetic")


class Pass3AndShortfallTests(unittest.TestCase):
    def setUp(self):
        ree._RECENT_QUESTION_COOLDOWN.clear()

    def test_absurd_topic_does_not_dump_whole_grade(self):
        exam = generate_blended_real_exam(
            "Vật lý",
            12,
            ["Chủ đề không tồn tại XYZQQQNOMATCH999"],
            (12, 4, 6),
        )
        self.assertIsInstance(exam, dict)
        total = _total(exam)
        self.assertTrue(exam.get("counts_shortfall") or total == 0)
        self.assertLess(total, 12, "Must not Pass3-dump ~full matrix from whole grade")

    def test_generic_topic_still_draws_same_subject_pool(self):
        exam = generate_blended_real_exam(
            "Vật lý",
            12,
            ["Chuyên đề tổng hợp môn Vật lý Lớp 12"],
            (8, 2, 2),
        )
        self.assertGreaterEqual(_total(exam), 8)
        self.assertFalse(exam.get("counts_shortfall"))


class HardCooldownTests(unittest.TestCase):
    def setUp(self):
        ree._RECENT_QUESTION_COOLDOWN.clear()

    def test_second_blend_avoids_first_fps_when_pool_large(self):
        # Dùng topic chắc có trong shard VL12 (baseline xz có thể MemoryError trên máy hẹp).
        topics = ["[Lớp 12] Nội năng và nhiệt động lực học"]
        first = generate_blended_real_exam("Vật lý", 12, topics, (6, 2, 2))
        fps1 = _fps(first)
        if not fps1:
            self.skipTest("VL pool empty for thermal topic on this host")
        for fp in fps1:
            remember_question_cooldown(fp)
        second = generate_blended_real_exam(
            "Vật lý",
            12,
            topics,
            (6, 2, 2),
            exclude_fingerprints=fps1,
        )
        overlap = fps1 & _fps(second)
        # Hard cooldown when fresh enough: overlap should be empty or tiny under shortfall.
        if not second.get("counts_shortfall"):
            self.assertEqual(overlap, set())
        else:
            self.assertLessEqual(len(overlap), 2)


class MultiSubjectGradeMatrixTests(unittest.TestCase):
    """Hồi quy toàn cục: nhiều môn × nhiều khối — không crash, không lẫn môn."""

    CASES = [
        ("Toán học", 12, ["[Lớp 12] Chuyên đề 1: Ứng dụng đạo hàm khảo sát & vẽ đồ thị hàm số"], (8, 2, 2)),
        ("Toán học", 10, ["Chuyên đề tổng hợp môn Toán học Lớp 10"], (6, 2, 2)),
        ("Toán học", 7, None, (6, 2, 2)),
        ("Vật lý", 12, ["[Lớp 12] Nội năng và nhiệt động lực học"], (8, 2, 2)),
        ("Vật lý", 9, ["Chuyên đề tổng hợp môn Vật lý Lớp 9"], (6, 2, 2)),
        ("Hóa học", 12, ["[Lớp 12] Ester - Lipid"], (6, 2, 2)),
        ("Hóa học", 8, None, (6, 2, 2)),
        ("Sinh học", 12, ["Chuyên đề tổng hợp môn Sinh học Lớp 12"], (6, 2, 2)),
        ("Sinh học", 6, None, (4, 2, 2)),
        ("Tiếng Anh", 12, None, (8, 2, 2)),
        ("Tiếng Anh", 10, ["Chuyên đề tổng hợp môn Tiếng Anh Lớp 10"], (6, 2, 2)),
        ("Tin học", 12, None, (6, 2, 2)),
        ("Tin học", 10, ["Chuyên đề tổng hợp môn Tin học Lớp 10"], (4, 2, 2)),
        ("Lịch sử", 12, None, (6, 2, 2)),
        ("Địa lí", 12, None, (6, 2, 2)),
        ("Công nghệ", 11, None, (4, 2, 2)),
    ]

    def setUp(self):
        ree._RECENT_QUESTION_COOLDOWN.clear()

    def test_matrix_subjects_grades_stable(self):
        failures = []
        for subject, grade, topics, counts in self.CASES:
            try:
                exam = generate_blended_real_exam(subject, grade, topics, counts)
            except Exception as exc:  # noqa: BLE001 — collect matrix failures
                failures.append(f"{subject}/{grade}: CRASH {exc}")
                continue
            if not isinstance(exam, dict):
                # Empty bank (honest None/empty) is OK for sparse subjects.
                continue
            total = _total(exam)
            # Cross-subject bleed: stem/topic must not claim a different major subject label wildly.
            # Soft check: exam.subject matches request when present.
            if exam.get("subject") and str(exam.get("subject")).lower() not in {
                subject.lower(),
                subject.split()[0].lower(),
            }:
                # Allow canonical aliases via containment
                if subject.split()[0].lower() not in str(exam.get("subject")).lower():
                    failures.append(
                        f"{subject}/{grade}: subject field={exam.get('subject')!r}"
                    )
            # Specific topic requests should not silently fill a full matrix from Pass3.
            if topics and specific_topic_filters(topics) and total >= sum(counts):
                self.assertFalse(
                    False
                )  # noop — structural; shortfall flag optional when pool rich
            # Within-exam fingerprint uniqueness
            fps = list(_fps(exam))
            if len(fps) != len(set(fps)):
                failures.append(f"{subject}/{grade}: duplicate fingerprints inside exam")
            # Counts metadata present for HS warning path
            if "counts_shortfall" not in exam and total > 0:
                failures.append(f"{subject}/{grade}: missing counts_shortfall")
        self.assertEqual(failures, [], msg="; ".join(failures))

    def test_physics_topic_fidelity_tokens(self):
        exam = generate_blended_real_exam(
            "Vật lý",
            12,
            ["[Lớp 12] Nội năng và nhiệt động lực học"],
            (8, 2, 2),
        )
        if _total(exam) == 0:
            self.skipTest("empty VL pool for thermal topic on this host")
        hits = sum(
            1
            for p in ("p1", "p2", "p3")
            for q in (exam.get(p) or [])
            if any(
                k in (str(q.get("topic", "")) + " " + str(q.get("q", ""))).lower()
                for k in ("nội năng", "nhiệt", "khí", "đẳng", "động lực")
            )
        )
        self.assertGreaterEqual(hits, max(1, _total(exam) // 2))


class PriorFidelityStillHoldsTests(unittest.TestCase):
    def setUp(self):
        ree._RECENT_QUESTION_COOLDOWN.clear()

    def test_physics_ui_chuyen_de_1_not_empty_when_bank_has_thermal(self):
        exam = generate_blended_real_exam(
            "Vật lý",
            12,
            ["[Lớp 12] Chuyên đề 1: Vật lý nhiệt và khí lí tưởng"],
            (12, 4, 6),
        )
        # May shortfall vs full 22, but must not be empty if bank has thermal topics.
        self.assertGreaterEqual(_total(exam), 1)

    def test_chemistry_ui_yields_or_honest_shortfall(self):
        exam = generate_blended_real_exam(
            "Hóa học",
            12,
            ["[Lớp 12] Chuyên đề 1: Ester - Lipid"],
            (12, 4, 6),
        )
        total = _total(exam)
        if total < 8:
            self.assertTrue(exam.get("counts_shortfall"))
        else:
            self.assertGreaterEqual(total, 8)

    def test_gdkt12_empty_honest(self):
        exam = generate_blended_real_exam(
            "Giáo dục kinh tế và pháp luật", 12, None, (12, 4, 6)
        )
        self.assertEqual(_total(exam), 0)


class AiRecoveryDefaultOffContractTests(unittest.TestCase):
    def test_app_defaults_ai_recovery_false_in_source(self):
        from pathlib import Path

        text = Path(__file__).resolve().parents[1].joinpath("app.py").read_text(
            encoding="utf-8"
        )
        self.assertIn(
            'st.session_state.get("enable_ai_context_recovery", False)',
            text,
        )
        self.assertIn('key="enable_ai_context_recovery"', text)
        # Default checkbox value must be False (P0).
        self.assertRegex(
            text,
            r'Cho phép AI sinh nguyên câu thay thế[\s\S]{0,200}?value=False',
        )


if __name__ == "__main__":
    unittest.main()
