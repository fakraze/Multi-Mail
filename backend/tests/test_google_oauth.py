import asyncio
import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlsplit

from app.api.google_oauth import callback, start
from app.services.google_oauth import (
    OAuthConfigError,
    OAuthExchangeError,
    OAuthStorageError,
    OAuthTokens,
    configuration,
    exchange_code,
    save_tokens,
)


class GoogleOAuthTests(unittest.TestCase):
    def test_backend_env_file_and_shell_override(self) -> None:
        contents = "GOOGLE_CLIENT_ID=file-id\nGOOGLE_CLIENT_SECRET='file-secret'\n"
        with patch("app.services.google_oauth.Path.read_text", return_value=contents):
            with patch.dict(os.environ, {}, clear=True):
                self.assertEqual(configuration()[:2], ("file-id", "file-secret"))
                os.environ["GOOGLE_CLIENT_ID"] = "shell-id"
                self.assertEqual(configuration()[:2], ("shell-id", "file-secret"))

    def test_start_redirects_with_state_and_offline_access(self) -> None:
        with patch.dict(os.environ, {"GOOGLE_CLIENT_ID": "test-id", "GOOGLE_CLIENT_SECRET": "test-secret"}):
            response = start()

        query = parse_qs(urlsplit(response.headers["location"]).query)
        self.assertEqual(query["client_id"], ["test-id"])
        self.assertEqual(query["access_type"], ["offline"])
        self.assertEqual(query["state"][0] in response.headers["set-cookie"], True)
        self.assertIn("httponly", response.headers["set-cookie"].lower())
        self.assertNotIn("test-secret", response.headers["location"])

    def test_exchange_returns_token_values_for_backend_storage(self) -> None:
        response = io.BytesIO(b'{"access_token":"private-value","refresh_token":"private-refresh"}')
        with patch("app.services.google_oauth.urlopen", return_value=response) as send:
            tokens = exchange_code("code", "id", "secret", "http://127.0.0.1:8000/auth/google/callback")
        self.assertEqual(tokens, OAuthTokens("private-value", "private-refresh"))
        self.assertEqual(send.call_args.args[0].full_url, "https://oauth2.googleapis.com/token")

    def test_save_tokens_replaces_previous_grant(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            token_file = Path(directory) / "oauth_tokens.json"
            with patch("app.services.google_oauth.TOKEN_FILE", token_file):
                save_tokens(OAuthTokens("old-access", "old-refresh"))
                save_tokens(OAuthTokens("new-access", None))
            self.assertEqual(
                json.loads(token_file.read_text(encoding="utf-8")),
                {"access_token": "new-access", "refresh_token": None},
            )

    def test_save_failure_preserves_existing_grant(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            token_file = Path(directory) / "oauth_tokens.json"
            token_file.write_text('{"access_token":"old-access"}', encoding="utf-8")
            with patch("app.services.google_oauth.TOKEN_FILE", token_file):
                with patch("app.services.google_oauth.os.replace", side_effect=OSError("disk error")):
                    with self.assertRaises(OAuthStorageError):
                        save_tokens(OAuthTokens("new-access", "new-refresh"))
            self.assertEqual(json.loads(token_file.read_text(encoding="utf-8")), {"access_token": "old-access"})
            self.assertEqual(list(Path(directory).glob(".oauth_tokens-*.tmp")), [])

    def test_exchange_handles_google_error(self) -> None:
        error = HTTPError("https://oauth2.googleapis.com/token", 400, "bad request", {}, None)
        with patch("app.services.google_oauth.urlopen", side_effect=error):
            with self.assertRaises(OAuthExchangeError):
                exchange_code("bad-code", "id", "secret", "http://127.0.0.1:8000/auth/google/callback")

    def test_callback_rejects_wrong_state_before_exchange(self) -> None:
        with patch("app.api.google_oauth.exchange_code") as exchange:
            response = asyncio.run(callback(code="code", state="wrong", error=None, saved_state="expected"))
        self.assertEqual(response.status_code, 400)
        exchange.assert_not_called()

    def test_callback_handles_denial_and_missing_code_without_exchange(self) -> None:
        with patch("app.api.google_oauth.exchange_code") as exchange:
            denied = asyncio.run(callback(code=None, state="expected", error="access_denied", saved_state="expected"))
            missing = asyncio.run(callback(code=None, state="expected", error=None, saved_state="expected"))
        self.assertEqual(denied.status_code, 400)
        self.assertIn(b"not approved", denied.body)
        self.assertEqual(missing.status_code, 400)
        self.assertIn(b"authorization code", missing.body)
        exchange.assert_not_called()

    def test_callback_handles_exchange_error_without_saving(self) -> None:
        with patch("app.api.google_oauth.configuration", return_value=("id", "secret", "redirect")):
            with patch("app.api.google_oauth.exchange_code", side_effect=OAuthExchangeError()):
                with patch("app.api.google_oauth.save_tokens") as save:
                    response = asyncio.run(callback(code="private-code", state="expected", error=None, saved_state="expected"))
        self.assertEqual(response.status_code, 502)
        save.assert_not_called()

    def test_callback_handles_missing_configuration_and_storage_error(self) -> None:
        with patch("app.api.google_oauth.configuration", side_effect=OAuthConfigError()):
            unavailable = asyncio.run(callback(code="code", state="expected", error=None, saved_state="expected"))
        with patch("app.api.google_oauth.configuration", return_value=("id", "secret", "redirect")):
            with patch("app.api.google_oauth.exchange_code", return_value=OAuthTokens("private-access", None)):
                with patch("app.api.google_oauth.save_tokens", side_effect=OAuthStorageError()):
                    unsaved = asyncio.run(callback(code="code", state="expected", error=None, saved_state="expected"))
        self.assertEqual(unavailable.status_code, 503)
        self.assertEqual(unsaved.status_code, 500)
        self.assertNotIn(b"private-access", unsaved.body)

    def test_callback_reports_success_without_tokens(self) -> None:
        with patch.dict(os.environ, {"GOOGLE_CLIENT_ID": "test-id", "GOOGLE_CLIENT_SECRET": "test-secret"}):
            with patch("app.api.google_oauth.exchange_code", return_value=OAuthTokens("private-access", "private-refresh")):
                with patch("app.api.google_oauth.save_tokens") as save:
                    with self.assertLogs("uvicorn.error", level="INFO") as recorded:
                        response = asyncio.run(callback(code="private-code", state="expected", error=None, saved_state="expected"))
        self.assertEqual(response.status_code, 303)
        self.assertEqual(response.headers["location"], "http://localhost:5173/?gmail=connected")
        self.assertNotIn("private-code", response.headers["location"])
        self.assertNotIn("private-access", response.headers["location"])
        self.assertIn("Max-Age=0", response.headers["set-cookie"])
        self.assertIn("access_token=True refresh_token=True", recorded.output[0])
        self.assertNotIn("private-code", recorded.output[0])
        self.assertNotIn("private-access", recorded.output[0])
        save.assert_called_once_with(OAuthTokens("private-access", "private-refresh"))


if __name__ == "__main__":
    unittest.main()
