import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError

from app.services.gmail_access import GmailAccessError, get_profile, load_local_tokens, verify_gmail_access
from app.services.google_oauth import OAuthTokens


class GmailAccessTests(unittest.TestCase):
    def test_loads_saved_grant_without_exposing_it(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "oauth_tokens.json"
            path.write_text(json.dumps({"access_token": "private-access", "refresh_token": "private-refresh"}))
            with patch("app.services.gmail_access.TOKEN_FILE", path):
                self.assertEqual(load_local_tokens(), OAuthTokens("private-access", "private-refresh"))

    def test_profile_request_uses_backend_bearer_token(self) -> None:
        with patch("app.services.gmail_access.urlopen", return_value=io.BytesIO(b'{"emailAddress":"me@example.com"}')) as send:
            profile = get_profile("private-access")
        self.assertEqual(profile.email_address, "me@example.com")
        request = send.call_args.args[0]
        self.assertEqual(request.full_url, "https://gmail.googleapis.com/gmail/v1/users/me/profile")
        self.assertEqual(request.get_header("Authorization"), "Bearer private-access")

    def test_expired_token_refreshes_and_retries_once(self) -> None:
        expired = HTTPError("https://gmail.googleapis.com/gmail/v1/users/me/profile", 401, "expired", {}, None)
        responses = [expired, io.BytesIO(b'{"access_token":"fresh-access"}'), io.BytesIO(b'{"emailAddress":"me@example.com"}')]
        with patch("app.services.gmail_access.load_local_tokens", return_value=OAuthTokens("old-access", "private-refresh")):
            with patch("app.services.gmail_access.configuration", return_value=("client-id", "client-secret", "redirect")):
                with patch("app.services.gmail_access.urlopen", side_effect=responses) as send:
                    profile = verify_gmail_access()
        self.assertEqual(profile.email_address, "me@example.com")
        self.assertEqual(send.call_count, 3)
        self.assertEqual(send.call_args.args[0].get_header("Authorization"), "Bearer fresh-access")
        refresh_request = send.call_args_list[1].args[0]
        self.assertEqual(refresh_request.full_url, "https://oauth2.googleapis.com/token")
        self.assertIn(b"grant_type=refresh_token", refresh_request.data)

    def test_missing_token_and_gmail_denial_are_safe_errors(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with patch("app.services.gmail_access.TOKEN_FILE", Path(directory) / "missing.json"):
                with self.assertRaisesRegex(GmailAccessError, "Connect Gmail first"):
                    load_local_tokens()
        denied = HTTPError("https://gmail.googleapis.com/gmail/v1/users/me/profile", 403, "private response", {}, None)
        with patch("app.services.gmail_access.urlopen", side_effect=denied):
            with self.assertRaises(GmailAccessError) as raised:
                get_profile("private-access")
        self.assertNotIn("private-access", str(raised.exception))
        self.assertNotIn("private response", str(raised.exception))


if __name__ == "__main__":
    unittest.main()
