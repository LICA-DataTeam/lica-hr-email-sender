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
        """
        Authenticates using the service account information.

        Excpects type `str` or `dict`, e.g., `"service_account.json"`, or `{"type": "service_account", ...}`
        """
        if isinstance(self.service_account_file, str) and self.service_account_file.endswith(".json"):
            return service_account.Credentials.from_service_account_file(
                self.service_account_file, scopes=self.SCOPES
            )
        elif isinstance(self.service_account_file, dict) or isinstance(self.service_account_file, str):
            return service_account.Credentials.from_service_account_info(
                self.service_account_file, scopes=self.SCOPES
            )
        else:
            raise ValueError("Invalid service account information.")

    def fetch_emails(self, filter_by: dict = None) -> list[dict]:
        self.logger.info("Fetching emails...")
        sheet = self.service.spreadsheets()
        result = sheet.values().get(
            spreadsheetId=self.spreadsheet_id,
            range=self.spreadsheet_range
        ).execute()
        values = result.get("values", [])
        col = values[0]
        rows = values[1:]
        employees = [dict(zip(col, row)) for row in rows]

        if filter_by:
            filtered = []
            for employee in employees:
                match = all(
                    employee.get(key) == value
                    for key, value in filter_by.items()
                )
                if match:
                    filtered.append(employee)
            return filtered

        return employees