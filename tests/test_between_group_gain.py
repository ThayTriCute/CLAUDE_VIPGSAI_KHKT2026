"""Trạm 4 — kiểm thử phân tích GIỮA nhóm (dùng app vs không dùng app).

Chạy được tại chỗ: chỉ cần numpy + scipy (không cần streamlit). Khoá hành vi của
`qa_runtime.between_group_gain_statistics` để ca sau không vô tình phá quy ước thống kê.
"""
import math
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qa_runtime import between_group_gain_statistics


class TestBetweenGroupGain(unittest.TestCase):
    def test_app_group_gains_more(self):
        # Nhóm app tiến bộ rõ hơn nhóm chứng; nền tiền-test tương đương.
        # Có độ phân tán trong nhóm (dữ liệu HS thật), trung bình tăng 3.0 vs 1.0.
        pre_app = [5.0, 5.0, 5.0, 6.0, 6.0, 6.0]
        post_app = [7.0, 8.0, 9.0, 8.0, 9.0, 10.0]  # Δ = 2,3,4,2,3,4 -> mean 3.0
        pre_ctl = [5.0, 5.0, 5.0, 6.0, 6.0, 6.0]
        post_ctl = [5.5, 6.0, 6.5, 6.5, 7.0, 7.5]   # Δ = .5,1,1.5,.5,1,1.5 -> mean 1.0
        r = between_group_gain_statistics(pre_app, post_app, pre_ctl, post_ctl)
        self.assertEqual(r["n_app"], 6)
        self.assertEqual(r["n_control"], 6)
        self.assertAlmostEqual(r["gain_app"], 3.0, places=6)
        self.assertAlmostEqual(r["gain_control"], 1.0, places=6)
        self.assertAlmostEqual(r["gain_difference"], 2.0, places=6)
        self.assertIsNotNone(r["p"])
        self.assertLess(r["p"], 0.05)              # chênh lệch tiến bộ có ý nghĩa
        self.assertGreater(r["cohens_d"], 0.8)     # cỡ hiệu ứng lớn, hướng dương
        self.assertTrue(r["baseline_equivalent"])  # hai nhóm tương đương lúc đầu

    def test_hake_normalized_gain_per_group(self):
        # ⟨g⟩ = mean_gain / (10 - mean_pre). App: 3/(10-5)=0.6 ; chứng: 1/(10-5)=0.2
        pre_app = [5.0, 5.0, 5.0, 5.0]
        post_app = [8.0, 8.0, 8.0, 8.0]
        pre_ctl = [5.0, 5.0, 5.0, 5.0]
        post_ctl = [6.0, 6.0, 6.0, 6.0]
        r = between_group_gain_statistics(pre_app, post_app, pre_ctl, post_ctl)
        self.assertAlmostEqual(r["hake_app"], 0.6, places=6)
        self.assertAlmostEqual(r["hake_control"], 0.2, places=6)

    def test_baseline_imbalance_flagged(self):
        # Nhóm app xuất phát thấp hơn hẳn -> không tương đương nền -> cảnh báo.
        pre_app = [2.0, 2.5, 3.0, 2.0, 2.5, 3.0]
        post_app = [5.0, 5.5, 6.0, 5.0, 5.5, 6.0]
        pre_ctl = [8.0, 8.5, 9.0, 8.0, 8.5, 9.0]
        post_ctl = [9.0, 9.2, 9.5, 9.0, 9.2, 9.5]
        r = between_group_gain_statistics(pre_app, post_app, pre_ctl, post_ctl)
        self.assertIsNotNone(r["pretest_p"])
        self.assertLess(r["pretest_p"], 0.05)
        self.assertFalse(r["baseline_equivalent"])

    def test_nonparametric_fallback_present(self):
        pre_app = [5.0, 6.0, 4.0, 5.0, 6.0]
        post_app = [9.0, 9.5, 8.0, 9.0, 9.5]
        pre_ctl = [5.0, 6.0, 4.0, 5.0, 6.0]
        post_ctl = [5.5, 6.5, 4.5, 5.5, 6.5]
        r = between_group_gain_statistics(pre_app, post_app, pre_ctl, post_ctl)
        self.assertIsNotNone(r["mannwhitney_p"])
        self.assertGreaterEqual(r["mannwhitney_p"], 0.0)
        self.assertLessEqual(r["mannwhitney_p"], 1.0)

    def test_identical_gains_no_false_significance(self):
        # Hai nhóm tiến bộ y hệt -> không được báo khác biệt có ý nghĩa.
        pre_app = [5.0, 6.0, 4.0, 5.0]
        post_app = [7.0, 8.0, 6.0, 7.0]
        pre_ctl = [5.0, 6.0, 4.0, 5.0]
        post_ctl = [7.0, 8.0, 6.0, 7.0]
        r = between_group_gain_statistics(pre_app, post_app, pre_ctl, post_ctl)
        self.assertAlmostEqual(r["gain_difference"], 0.0, places=6)
        if r["p"] is not None:
            self.assertGreater(r["p"], 0.05)

    def test_validation_errors(self):
        with self.assertRaises(ValueError):  # dưới 2 cặp
            between_group_gain_statistics([5.0], [7.0], [5.0, 6.0], [6.0, 7.0])
        with self.assertRaises(ValueError):  # ngoài thang 0-10
            between_group_gain_statistics([5.0, 11.0], [7.0, 8.0], [5.0, 6.0], [6.0, 7.0])
        with self.assertRaises(ValueError):  # lệch độ dài trong một nhóm
            between_group_gain_statistics([5.0, 6.0, 7.0], [7.0, 8.0], [5.0, 6.0], [6.0, 7.0])


if __name__ == "__main__":
    unittest.main()
