from components.utils import GmailService, GSheetService
from config import GMAIL_TOKEN_FILE, OAUTH_FILE
from components import GoogleServiceFactory
from functools import lru_cache
from config import Sheets
from typing import cast
import json
import os

@lru_cache
def _gmail_service_factory() -> GmailService:
    config = {
        "gmail_token_file": GMAIL_TOKEN_FILE,
        "oauth_file": OAUTH_FILE
    }
    return cast(GmailService, GoogleServiceFactory.create("gmail", config))

@lru_cache
def _gsheet_service_factory() -> GSheetService:
    config = {
        "service_account_file": json.loads(os.environ["LICA_HR_SERVICE_INFO"]),
        "spreadsheet_id": Sheets.EMAIL_MASTERLIST.id,
        "spreadsheet_range": Sheets.EMAIL_MASTERLIST.range
    }
    return cast(GSheetService, GoogleServiceFactory.create("gsheet"), config)

def get_gmail_service() -> GmailService:
    return _gmail_service_factory()

def get_gsheet_service() -> GSheetService:
    return _gsheet_service_factory()