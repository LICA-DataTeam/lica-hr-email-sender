from app.common import (
    JSONResponse,
    APIRouter,
    status
)
from components import GoogleServiceFactory
from config import (
    GMAIL_TOKEN_FILE, OAUTH_FILE,
    TEST_EMAIL1, TEST_EMAIL2,
    SUBJECT, BODY
)

router = APIRouter()

@router.post("/send-email")
def send_automated_email():
    try:
        config = {
            "gmail_token_file": GMAIL_TOKEN_FILE,
            "oauth_file": OAUTH_FILE
        }
        GoogleServiceFactory.create("gmail", config).send_email(
            recipient_email=[TEST_EMAIL1, TEST_EMAIL2],
            subject=SUBJECT,
            body=BODY
        )
        return JSONResponse(
            content={
                "status": "success"
            },
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return JSONResponse(
            content={
                "status": "error",
                "message": str(e)
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )