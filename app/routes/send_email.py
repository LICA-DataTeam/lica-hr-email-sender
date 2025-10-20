from app.common import (
    JSONResponse,
    APIRouter,
    Depends,
    status
)
from app.dependencies import get_gmail_service
from components.utils import GmailService
from config import (
    TEST_EMAIL1, TEST_EMAIL2,
    SUBJECT, BODY
)

router = APIRouter()

@router.post("/send-email")
def send_automated_email(gmail_service: GmailService = Depends(get_gmail_service)):
    try:
        gmail_service.send_email(
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