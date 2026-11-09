"""Admin area must be locked when ADMIN_PASS is unset — no shared default password.

app.py passes "" as the fallback (no baked-in hash), so an empty `configured`
must never authenticate, while a correctly configured sha256 secret
authenticates only its own preimage.
"""
import hashlib
import unittest

from qa_runtime import admin_password_matches


class TestAdminAuthBoundary(unittest.TestCase):
    def test_unset_secret_rejects_everything(self):
        for candidate in ("", " ", "admin", "123456", "sha256:deadbeef"):
            self.assertFalse(admin_password_matches(candidate, ""),
                             msg=f"empty secret must reject {candidate!r}")

    def test_configured_sha256_matches_only_its_preimage(self):
        secret = "sha256:" + hashlib.sha256("Thay_Tri_2026".encode()).hexdigest()
        self.assertTrue(admin_password_matches("Thay_Tri_2026", secret))
        self.assertFalse(admin_password_matches("wrong", secret))
        self.assertFalse(admin_password_matches("", secret))

    def test_plain_secret_compares_exactly(self):
        self.assertTrue(admin_password_matches("plain-pass", "plain-pass"))
        self.assertFalse(admin_password_matches("plain-pass", ""))
        self.assertFalse(admin_password_matches("", "plain-pass"))

    def test_malformed_sha256_secret_is_rejected(self):
        self.assertFalse(admin_password_matches("anything", "sha256:tooshort"))


if __name__ == "__main__":
    unittest.main()
