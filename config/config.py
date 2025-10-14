from dataclasses import dataclass
from dotenv import load_dotenv
import os

load_dotenv()

@dataclass(frozen=True)
class Spreadsheet:
    id: str
    range: str

class Sheets:
    EMAIL_MASTERLIST = Spreadsheet(os.getenv("EMAIL_MASTERLIST_ID"), "Sheet1!A1:G134")
    SC_LOOKER_STUDIO_NAME_LIST = Spreadsheet(os.getenv("SC_LOOKER_STUDIO_NAME_LIST"), "Sheet1!A1:A1539")
    GRM_LOOKER_STUDIO_NAME_LIST = Spreadsheet(os.getenv("GRM_LOOKER_STUDIO_NAME_LIST"), "Sheet1!A1:A150")

SC_BASE_URL = os.getenv("SC_LOOKER_STUDIO_URL")
GRM_BASE_URL = os.getenv("GRM_LOOKER_STUDIO_URL")

SERVICE_FILE = os.getenv("LICA_HR_SERVICE_ACCOUNT_FILE")
OAUTH_FILE = os.getenv("LICA_HR_OAUTH_FILE")
GMAIL_TOKEN_FILE = os.getenv("GMAIL_TOKEN_FILE")

TEST_EMAIL1 = os.getenv("TEST_EMAIL1")
TEST_EMAIL2 = os.getenv("TEST_EMAIL2")
SUBJECT = "Test"
BODY = """
Hello, World!
"""