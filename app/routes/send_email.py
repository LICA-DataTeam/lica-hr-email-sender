from app.dependencies import get_gmail_service
from components.utils import GmailService
from pydantic import BaseModel, EmailStr
from typing import Optional, Union
from config import (
    TEST_EMAIL1, TEST_EMAIL2,
    SUBJECT, BODY
)
from app.common import (
    HTTPException,
    JSONResponse,
    APIRouter,
    Depends,
    status
)

router = APIRouter()

class SendEmailRequest(BaseModel):
    recipients: Optional[Union[EmailStr, list[EmailStr]]] = None
    subject: Optional[str] = None
    body: Optional[str] = None

@router.post("/send-email")
def send_automated_email(
    payload: SendEmailRequest,
    gmail_service: GmailService = Depends(get_gmail_service)
):
    def _to_list(value: Union[EmailStr, list[EmailStr]]) -> list[EmailStr]:
        return [value] if isinstance(value, str) else value

    recipients = (
        _to_list(payload.recipients)
        if payload.recipients
        else [addr for addr in (TEST_EMAIL1, TEST_EMAIL2) if addr]
    )
    if not recipients:
        raise HTTPException(status_code=400, detail="At least one recipient is required")
    
    subject = payload.subject or SUBJECT
    body = payload.body or BODY
    try:
        gmail_service.send_email(
            recipient_email=recipients,
            subject=subject,
            body=body
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