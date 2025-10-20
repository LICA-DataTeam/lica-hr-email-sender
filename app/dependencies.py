from config import GMAIL_TOKEN_FILE, OAUTH_FILE
from components import GoogleServiceFactory
from components.utils import GmailService
from functools import lru_cache
from typing import cast

@lru_cache
def _gmail_service_factory() -> GmailService:
    config = {
        "gmail_token_file": GMAIL_TOKEN_FILE,
        "oauth_file": OAUTH_FILE
    }
    return cast(GmailService, GoogleServiceFactory.create("gmail", config))

def get_gmail_service() -> GmailService:
    return _gmail_service_factory()