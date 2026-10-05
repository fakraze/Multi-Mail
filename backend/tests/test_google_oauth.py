import asyncio
import io
import os
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlsplit

from app.api.google_oauth import callback, start
from app.services.google_oauth import OAuthExchangeError, configuration, exchange_code


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

    def test_exchange_checks_token_presence_without_returning_value(self) -> None:
        response = io.BytesIO(b'{"access_token":"private-value","refresh_token":"private-refresh"}')
        with patch("app.services.google_oauth.urlopen", return_value=response) as send:
            self.assertTrue(exchange_code("code", "id", "secret", "http://127.0.0.1:8000/auth/google/callback"))
        self.assertEqual(send.call_args.args[0].full_url, "https://oauth2.googleapis.com/token")

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

    def test_callback_reports_success_without_tokens(self) -> None:
        with patch.dict(os.environ, {"GOOGLE_CLIENT_ID": "test-id", "GOOGLE_CLIENT_SECRET": "test-secret"}):
            with patch("app.api.google_oauth.exchange_code", return_value=True):
                with self.assertLogs("uvicorn.error", level="INFO") as recorded:
                    response = asyncio.run(callback(code="private-code", state="expected", error=None, saved_state="expected"))
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(b"private-code", response.body)
        self.assertIn(b"No account was saved yet", response.body)
        self.assertIn("Max-Age=0", response.headers["set-cookie"])
        self.assertIn("access_token=True refresh_token=True", recorded.output[0])
        self.assertNotIn("private-code", recorded.output[0])


if __name__ == "__main__":
    unittest.main()
