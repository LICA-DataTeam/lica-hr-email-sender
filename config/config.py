from dotenv import load_dotenv
import os

load_dotenv()

SPREADSHEET_ID = os.getenv("EMAIL_MASTERLIST_ID")
SPREADSHEET_RANGE = "Sheet1!A1:G134"

SC_BASE_URL = os.getenv("SC_LOOKER_STUDIO_URL")
GRM_BASE_URL = os.getenv("GRM_LOOKER_STUDIO_URL")