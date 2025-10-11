from google.auth.credentials import Credentials
from googleapiclient.discovery import build
from google.oauth2 import service_account
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class GSheetService:
    SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

    def __init__(self, service_account_file: str, spreadsheet_id: str, spreadsheet_range: str):
        self.logger = logging.getLogger(__name__)
        self.service_account_file = service_account_file
        self.creds = self._authenticate()
        self.service = build("sheets", "v4", credentials=self.creds, cache_discovery=False)
        self.spreadsheet_id = spreadsheet_id
        self.spreadsheet_range = spreadsheet_range

    def _authenticate(self) -> Credentials:
        return service_account.Credentials.from_service_account_file(
            self.service_account_file, scopes=self.SCOPES
        )

def fetch_emails(gsheet: GSheetService) -> list[dict]:
    gsheet.logger.info("Fetching emails...")
    sheet = gsheet.service.spreadsheets()
    result = sheet.values().get(
        spreadsheetId=gsheet.spreadsheet_id,
        range=gsheet.spreadsheet_range
    ).execute()
    values = result.get("values", [])
    col = values[0]
    rows = values[1:]
    return [dict(zip(col, row)) for row in rows]