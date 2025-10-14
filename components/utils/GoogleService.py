from .GSheetService import GSheetService
from .GmailService import GmailService
from typing import Literal

class GoogleServiceFactory:
    @staticmethod
    def create(service: Literal["gsheet", "gmail"], config: dict):
        if service == "gsheet":
            return GSheetService(
                service_account_file=config["service_account_file"],
                spreadsheet_id=config["spreadsheet_id"],
                spreadsheet_range=config["spreadsheet_range"]
            )
        elif service == "gmail":
            return GmailService(
                token_file=config["gmail_token_file"],
                token_key="GMAIL_TOKEN_LICAHR",
                oauth_key="LICAHR_EMAIL_OAUTH",
                oauth_file=config["oauth_file"]
            )
        else:
            raise ValueError(f"Unsupported service type: {service}")