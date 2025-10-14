from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from email.mime.multipart import MIMEMultipart
from googleapiclient.discovery import build
from typing import Optional, Union, List
from email.mime.text import MIMEText
import logging
import base64
import json
import os

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class GmailService:
    SCOPES = [
        "https://www.googleapis.com/auth/gmail.send",
        "https://www.googleapis.com/auth/gmail.readonly"
    ]

    def __init__(self, *, token_file: str, token_key: str, oauth_file: str, oauth_key: str):
        """Initialize Gmail client with authentication."""
        self.logger = logging.getLogger(__name__)
        self.creds = self._authenticate(token_file, token_key, oauth_file, oauth_key)
        self.service = build('gmail', 'v1', credentials=self.creds, cache_discovery=False)
        self.sender_email = self._get_sender_email()
        self.logger.info(f"Gmail service authenticated as {self.sender_email!r}")

    def _authenticate(self, token_file: str, token_key: str, oauth_file: str, oauth_key: str) -> Credentials:
        """Handle Gmail authentication with token refresh and OAuth fallback."""
        # Try to load existing token
        user_token, token_source = self._load_token(token_file, token_key)
        creds = None

        if user_token:
            creds = Credentials.from_authorized_user_info(user_token, self.SCOPES)
            self.logger.info(f"Credentials loaded from {token_source}")

            # Refresh if expired
            if creds.expired and creds.refresh_token:
                creds = self._refresh_credentials(creds)
                with open(token_file, 'w') as f:
                    f.write(creds.to_json())

        # OAuth flow if no valid credentials
        if not creds:
            creds = self._oauth_flow(oauth_file, oauth_key, token_file)

        return creds

    def _load_token(self, token_file: str, token_key: str) -> tuple[Optional[dict], Optional[str]]:
        """Load user token from environment or file."""
        if token_key in os.environ:
            return json.loads(os.environ[token_key]), "environment"
        elif os.path.exists(token_file):
            with open(token_file, 'r') as f:
                return json.load(f), "local file"
        else:
            self.logger.info("User token not found. Falling back to OAuth")
            return None, None

    def _refresh_credentials(self, creds: Credentials) -> Optional[Credentials]:
        """Attempt to refresh expired credentials."""
        self.logger.info("Credentials expired. Attempting to refresh token...")
        try:
            creds.refresh(Request())
            self.logger.info("Token successfully refreshed")
            return creds
        except Exception as e:
            self.logger.error("Failed to refresh credentials. Re-authenticating via OAuth", exc_info=True)
            return None

    def _oauth_flow(self, oauth_file: str, oauth_key: str, token_file: str) -> Credentials:
        """Run OAuth flow to get new credentials."""
        client_config, oauth_source = self._load_oauth_config(oauth_file, oauth_key)

        flow = InstalledAppFlow.from_client_config(client_config, self.SCOPES)
        creds = flow.run_local_server(port=0)
        self.logger.info(f"Credentials loaded from OAuth using {oauth_source}")

        # Save token for future use
        with open(token_file, 'w') as f:
            f.write(creds.to_json())
        self.logger.info("Local user token file created")

        return creds

    def _load_oauth_config(self, oauth_file: str, oauth_key: str) -> tuple[dict, str]:
        """Load OAuth configuration from environment or file."""
        if oauth_key in os.environ:
            return json.loads(os.environ[oauth_key]), "environment"
        elif os.path.exists(oauth_file):
            with open(oauth_file, 'r') as f:
                return json.load(f), "local file"
        else:
            raise ValueError("Neither token nor OAuth configuration found")

    def _get_sender_email(self) -> str:
        """Get authenticated user's email address."""
        profile = self.service.users().getProfile(userId='me').execute()
        return profile['emailAddress']

    def _format_recipients(self, recipients: Union[str, List[str]]) -> str:
        """Convert recipients to comma-separated string."""
        if isinstance(recipients, str):
            return recipients
        elif isinstance(recipients, list):
            return ', '.join(recipients)
        else:
            raise TypeError("Recipients must be a string or list of strings")

    def _create_message(self, to: Union[str, List[str]], subject: str, body: str) -> dict:
        """Create basic email message."""
        message = MIMEMultipart()
        message['To'] = self._format_recipients(to)
        message['From'] = self.sender_email
        message['Subject'] = subject
        message.attach(MIMEText(body, 'plain'))

        return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

    def send_email(self, recipient_email: Union[str, List[str]], subject: str, body: str) -> str:
        """Send a basic email."""
        message = self._create_message(recipient_email, subject, body)
        result = self.service.users().messages().send(userId='me', body=message).execute()
        message_id = result['id']

        recipients = self._format_recipients(recipient_email)
        self.logger.info(f"Email sent to {recipients}! Message ID: {message_id}")
        return message_id