"""
Standalone Gmail auth test.
Run this first to verify OAuth is working before building the agent.

Prerequisites:
  1. Google Cloud Console → enable Gmail API
  2. OAuth consent screen → add yourself as a test user
  3. Create OAuth 2.0 credentials (Desktop app) → download as credentials.json
  4. Place credentials.json in the project root (same directory as this file)

Usage:
  python gmail_auth_test.py
"""

import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
CREDENTIALS_FILE = "credentials.json"
TOKEN_FILE = "token.json"


def get_gmail_service():
    """Returns (service, error). On success, error is None. On failure, service is None."""
    creds = None

    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                return None, f"Failed to refresh credentials: {e}"
        else:
            if not os.path.exists(CREDENTIALS_FILE):
                return None, f"'{CREDENTIALS_FILE}' not found. Download it from Google Cloud Console."
            try:
                flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
                creds = flow.run_local_server(port=0)
            except Exception as e:
                return None, f"OAuth flow failed: {e}"

        try:
            with open(TOKEN_FILE, "w") as f:
                f.write(creds.to_json())
        except Exception as e:
            return None, f"Failed to save token: {e}"

    try:
        service = build("gmail", "v1", credentials=creds)
        return service, None
    except Exception as e:
        return None, f"Failed to build Gmail service: {e}"


def list_recent_emails(service, count=5):
    results = service.users().messages().list(userId="me", maxResults=count).execute()
    messages = results.get("messages", [])

    if not messages:
        print("No messages found.")
        return

    print(f"Last {count} emails:\n")
    for i, msg in enumerate(messages, 1):
        detail = service.users().messages().get(
            userId="me",
            id=msg["id"],
            format="metadata",
            metadataHeaders=["Subject", "From", "Date"],
        ).execute()

        headers = {h["name"]: h["value"] for h in detail["payload"]["headers"]}
        print(f"{i}. From:    {headers.get('From', 'N/A')}")
        print(f"   Date:    {headers.get('Date', 'N/A')}")
        print(f"   Subject: {headers.get('Subject', 'N/A')}")
        print()


if __name__ == "__main__":
    try:
        service, error = get_gmail_service()
        if error:
            print(f"Authentication failed: {error}")
        else:
            print("Authentication successful.\n")
            list_recent_emails(service)
    except HttpError as e:
        print(f"Gmail API error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
