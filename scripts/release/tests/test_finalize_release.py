import unittest
import urllib.error
from unittest.mock import patch

from scripts.release.finalize_release import _ensure_tag, resolve_release_tag_policy


class ReleaseTagPolicyTests(unittest.TestCase):
    def test_release_ready_targets_current_head_and_may_create_tag(self) -> None:
        target, allow_create = resolve_release_tag_policy(
            {"status": "release_ready"},
            "a" * 40,
        )

        self.assertEqual(target, "a" * 40)
        self.assertTrue(allow_create)

    def test_released_targets_recorded_commit_and_cannot_create_tag(self) -> None:
        target, allow_create = resolve_release_tag_policy(
            {
                "status": "released",
                "release_commit_sha": "b" * 40,
            },
            "c" * 40,
        )

        self.assertEqual(target, "b" * 40)
        self.assertFalse(allow_create)

    def test_released_requires_recorded_commit(self) -> None:
        with self.assertRaisesRegex(ValueError, "release_commit_sha"):
            resolve_release_tag_policy({"status": "released"}, "c" * 40)

    def test_unsupported_status_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "release_ready or released"):
            resolve_release_tag_policy({"status": "release_candidate"}, "c" * 40)


class EnsureReleaseTagTests(unittest.TestCase):
    @patch("scripts.release.finalize_release._request_json")
    def test_published_tag_is_verified_without_moving_it(self, request_json) -> None:
        request_json.return_value = {"object": {"sha": "d" * 40}}

        result = _ensure_tag(
            "https://api.github.test",
            "owner/repo",
            "token",
            "v0.1.0",
            "d" * 40,
            allow_create=False,
        )

        self.assertEqual(result, "verified_immutable")
        request_json.assert_called_once()

    @patch("scripts.release.finalize_release._request_json")
    def test_published_tag_mismatch_fails(self, request_json) -> None:
        request_json.return_value = {"object": {"sha": "e" * 40}}

        with self.assertRaisesRegex(RuntimeError, "published commit"):
            _ensure_tag(
                "https://api.github.test",
                "owner/repo",
                "token",
                "v0.1.0",
                "d" * 40,
                allow_create=False,
            )

    @patch("scripts.release.finalize_release._request_json")
    def test_missing_published_tag_fails_instead_of_recreating_it(self, request_json) -> None:
        request_json.side_effect = urllib.error.HTTPError(
            "https://api.github.test/ref",
            404,
            "not found",
            {},
            None,
        )

        with self.assertRaisesRegex(RuntimeError, "is missing"):
            _ensure_tag(
                "https://api.github.test",
                "owner/repo",
                "token",
                "v0.1.0",
                "d" * 40,
                allow_create=False,
            )

    @patch("scripts.release.finalize_release._request_json")
    def test_release_ready_tag_can_still_be_created(self, request_json) -> None:
        request_json.side_effect = [
            urllib.error.HTTPError(
                "https://api.github.test/ref",
                404,
                "not found",
                {},
                None,
            ),
            {},
        ]

        result = _ensure_tag(
            "https://api.github.test",
            "owner/repo",
            "token",
            "v0.2.0",
            "f" * 40,
            allow_create=True,
        )

        self.assertEqual(result, "created")
        self.assertEqual(request_json.call_count, 2)


if __name__ == "__main__":
    unittest.main()
