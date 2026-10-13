"""One-time local script: obtains a Google Calendar OAuth refresh token via
browser consent and saves it to apps/api/.secrets/token.json.

Run once from apps/api/:
    .venv\\Scripts\\python.exe scripts\\google_oauth_setup.py

Requires apps/api/.secrets/credentials.json (OAuth "Desktop app" client,
downloaded from Google Cloud Console) to already exist.
"""

from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/calendar"]

SECRETS_DIR = Path(__file__).resolve().parent.parent / ".secrets"
CREDENTIALS_PATH = SECRETS_DIR / "credentials.json"
TOKEN_PATH = SECRETS_DIR / "token.json"


def main() -> None:
    if not CREDENTIALS_PATH.exists():
        raise SystemExit(
            f"Missing {CREDENTIALS_PATH} — download it from Google Cloud Console first."
        )

    creds = None
    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_PATH), SCOPES)
            creds = flow.run_local_server(port=0)
        TOKEN_PATH.write_text(creds.to_json())

    print(f"Saved refresh token to {TOKEN_PATH}")


if __name__ == "__main__":
    main()
