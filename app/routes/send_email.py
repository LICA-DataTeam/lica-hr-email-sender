from app.dependencies import get_gmail_service, get_gsheet_service
from components.utils import GmailService, GSheetService
from components import GoogleServiceFactory
from pydantic import BaseModel, EmailStr
from typing import Optional, Union
from enum import Enum
import logging
import json
import os
from config import (
    SUBJECT, BODY,
    SERVICE_FILE,
    Sheets
)
from app.common import (
    HTTPException,
    JSONResponse,
    APIRouter,
    Depends,
    status
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

router = APIRouter()

class Branch(str, Enum):
    SHAW = "HYUNDAI SHAW"
    BATANGAS = "HYUNDAI BATANGAS"
    LIPA = "HYUNDAI LIPA"
    CAINTA = "HYUNDAI CAINTA"
    TRUCKS_AND_BUSES = "HYUNDAI CAINTA TRUCKS AND BUSES"
    TEST = "TEST BRANCH"

class RecipientType(str, Enum):
    SC = "SC"
    GRM = "GRM"

class SendEmailRequest(BaseModel):
    recipients: Optional[Union[EmailStr, list[EmailStr]]] = None
    subject: Optional[str] = None
    body: Optional[str] = None

class BranchEmailRequest(SendEmailRequest):
    branch: Branch
    recipient_type: RecipientType = RecipientType.SC

def _split_name(full_name: str) -> tuple[str, str]:
    parts = full_name.strip().split()
    if not parts:
        return "", ""
    return parts[0], " ".join(parts[1:])

def _build_recipient_list(branch: Branch, recipient_type: RecipientType, gsheet_service: GSheetService) -> list[str]:
    logging.info("Building recipient list for branch=%s, target=%s", branch.value, recipient_type.value)
    
    branch_value = branch.value.upper()
    employees = [
        emp for emp in gsheet_service.fetch_emails()
        if emp.get("branch", "").strip().upper() == branch_value
    ]
    recipients: dict[str, dict] = {}

    for emp in employees:
        if recipient_type is RecipientType.GRM:
            email = emp.get("grm_email_address")
            if not email:
                continue
            first, last = _split_name(emp.get("grm_name", ""))
        else:
            email = emp.get("sc_email_address")
            if not email:
                continue
            first = emp.get("sc_firstname", "")
            last = emp.get("sc_lastname", "")

        email_key = email.lower()
        if email_key not in recipients:
            first_name = first.title() if first else ""
            last_name = last.title() if last else ""
            recipients[email_key] = {
                "email": email,
                "first_name": first_name,
                "last_name": last_name,
                "full_name": (first_name + " " + last_name).strip(),
                "data": emp
            }
    return list(recipients.values())

def _render_template(template: str, employee: dict, branch: Branch) -> str:
    context = {
        "first_name": employee["first_name"],
        "last_name": employee["last_name"],
        "full_name": employee["full_name"],
        "branch": branch.value
    }
    try:
        return template.format(**context)
    except KeyError as e:
        logging.warning("Missing placeholder %s in template; returning original text", e)
        return template

@router.post("/send-email")
def send_automated_email(
    payload: BranchEmailRequest,
    gmail_service: GmailService = Depends(get_gmail_service),
    gsheet_service: GSheetService = Depends(get_gsheet_service)
):
    """
    Sends an email to employees under specified branch.
    """
    recipients = _build_recipient_list(payload.branch, payload.recipient_type, gsheet_service)
    if not recipients:
        raise HTTPException(
            status_code=404,
            detail=f"No employees found for branch '{payload.branch}'."
        )
    
    sent = []
    skipped = []
    subject = payload.subject or SUBJECT
    body = payload.body or BODY
    try:
        for recipient in recipients:
            email = recipient["email"]
            if not email:
                skipped.append(recipient["data"])
                continue
            body_template = _render_template(body, recipient, payload.branch)
            gmail_service.send_email(email, subject, body_template)
            sent.append(email)
        return JSONResponse(
            content={
                "status": "success",
                "branch": payload.branch.value,
                "recipient_list": recipients,
                "recipient_type": payload.recipient_type.value,
                "sent": sent,
                "skipped": [rec["full_name"] for rec in recipients if rec["email"] is None]
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