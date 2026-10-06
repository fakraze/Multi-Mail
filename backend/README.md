# Local Google OAuth check

1. In Google Cloud, enable the Gmail API, configure the OAuth consent screen, and create a **Web application** OAuth client. Add the Google account you will use as a test user if the app is in testing mode. Register this exact authorized redirect URI: `http://127.0.0.1:8000/auth/google/callback`.
2. From `backend/`, install dependencies with `python -m pip install -r requirements.txt`.
3. Copy `backend/.env.example` to `backend/.env` and replace the client ID and secret with the values from Google Cloud. The backend loads this file automatically; existing shell environment variables take precedence. Optionally set `GOOGLE_REDIRECT_URI` to another loopback URL whose path is `/auth/google/callback`, and set frontend `VITE_BACKEND_URL` to the matching backend origin. Do not commit `backend/.env` or the credentials.
4. From `backend/`, run `python run.py`. This launcher disables HTTP access logs because callback URLs contain short-lived authorization codes. For auto-reload, use `uvicorn app.main:app --reload --no-access-log`; plain `uvicorn ... --reload` prints authorization codes in request logs.
5. From `frontend/`, run `npm install` and `npm run dev`. Click **Connect Gmail**, then **Continue with Google**.

The backend callback page reports success or failure without showing tokens. On success, the backend saves the latest grant's access token and optional refresh token to the ignored `backend/oauth_tokens.json` file, then logs only whether each token is present. Google may omit a refresh token after an earlier grant; a later grant replaces the file even when the new response has no refresh token. The file is plain JSON containing live credentials: keep it on your local machine and restrict access to your user account. No account data is stored, and the sample inbox is not connected to Gmail yet.

Run backend tests from `backend/` with `python -m unittest discover -s tests`.
