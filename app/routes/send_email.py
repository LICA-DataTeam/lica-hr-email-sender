from app.dependencies import get_gmail_service, get_gsheet_service
from config.email_contents import generate_email, EMAIL_TEMPLATES
from components.utils import GmailService, GSheetService
from pydantic import BaseModel, EmailStr
from typing import Optional, Union
from config import SC_BASE_URL
from datetime import date
from enum import Enum
import logging
from app.common import (
    HTTPException,
    JSONResponse,
    APIRouter,
    Depends,
    Query,
    status
)

from components.run import generate_employee_links

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

def _default_month_year(year: int=None, month: int=None):
    if not year and not month:
        today = date.today()
        year = today.year
        month = today.month
    return year, month

def _split_name(full_name: str) -> tuple[str, str]:
    parts = full_name.strip().split()
    if not parts:
        return "", ""
    return parts[0], " ".join(parts[1:])

def _normalize_name(name: Optional[str]) -> str:
    if not name:
        return ""
    return " ".join(name.split()).strip().lower()

def _recipient_key_candidates(recipient: dict) -> list[str]:
    data = recipient.get("data", {})
    raw_candidates = [
        recipient.get("full_name"),
        f"{recipient.get('first_name', '')} {recipient.get('last_name', '')}",
        f"{data.get('sc_firstname', '')} {data.get('sc_lastname', '')}",
        data.get("grm_name"),
    ]
    candidates: list[str] = []
    seen: set[str] = set()

    for value in raw_candidates:
        normalized = _normalize_name(value)
        if normalized and normalized not in seen:
            seen.add(normalized)
            candidates.append(normalized)
    return candidates

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

def _format_link_block(entries: list[dict]) -> str:
    return "\n".join(
        f"    {idx}. {item['name']} → {item['url']}"
        for idx, item in enumerate(entries, start=1)
    )

def _render_grm_email(
    employee: dict,
    managed_links: list[dict],
    employee_month: int,
    employee_year: int,
    recipient_type: RecipientType
):
    context = {
        "first_name": employee["first_name"],
        "last_name": employee["last_name"],
        "email_address": employee["email"],
        "branch": employee["data"]["branch"],
        "month": employee_month,
        "year": employee_year,
        "department": recipient_type,
        "managed_links": _format_link_block(managed_links)
    }
    return generate_email(context, employee_month, employee_year, url="")

def _render_template(
    employee: dict,
    employee_month: int,
    employee_year: int,
    recipient_type: RecipientType,
    url: str,
) -> str:
    context = {
        "first_name": employee["first_name"],
        "last_name": employee["last_name"],
        "email_address": employee["email"],
        "url": url,
        "branch": employee["data"]["branch"],
        "month": employee_month,
        "year": employee_year,
        "department": recipient_type.value,
    }
    try:
        return generate_email(
            context,
            employee_month=employee_month,
            employee_year=employee_year,
            url=url,
        )
    except KeyError as e:
        logging.warning("Missing placeholder %s in template; returning original text", e)
        fallback_context = {
            "first_name": context.get("first_name", ""),
            "last_name": context.get("last_name", ""),
            "email_address": context.get("email_address", ""),
            "month": context.get("month", ""),
            "year": context.get("year", ""),
            "url": context.get("url", ""),
        }
        fallback_template = EMAIL_TEMPLATES["Default"]
        return fallback_template.format(**fallback_context)

@router.post("/send-sc-email")
def send_sc_url(
    payload: BranchEmailRequest,
    gmail_service: GmailService = Depends(get_gmail_service),
    gsheet_service: GSheetService = Depends(get_gsheet_service),
    year: int = Query(None, description="Assessment year for the employee."),
    month: int = Query(None, description="Assessment month for the employee."),
    emp_key: list[str] = Query(None, description="Employee key you want to look up.")
):
    recipients = _build_recipient_list(payload.branch, payload.recipient_type, gsheet_service)
    if not recipients:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No employees found for branch '{payload.branch}'"
        )

    sent = []
    skipped = []

    year, month = _default_month_year(year, month)

    try:
        logging.info("Collecting employee links...")
        links = generate_employee_links(
            base_url=SC_BASE_URL,
            year=year,
            month=month
        )

        if emp_key:
            links = {name: data for name, data in links.items() if any(key.lower() in name.lower() for key in emp_key)}

        link_lookup: dict[str, dict] = {}
        for names, data in links.items():
            normalized = _normalize_name(names)
            if not normalized:
                continue
            if normalized in link_lookup:
                logging.warning("Duplicate link entry detected for %s; overriding previous value", names)
            link_lookup[normalized] = {
                "name": names,
                "url": data.get("url"),
                "branch": data.get("branch"),
            }

        logging.info("Collecting recipients...")
        for recipient in recipients:
            email = recipient["email"]
            if not email:
                skipped.append(recipient["data"])
                continue

            link_info = None
            for candidate in _recipient_key_candidates(recipient):
                if candidate in link_lookup:
                    link_info = link_lookup.pop(candidate)
                    break

            if not link_info or not link_info.get("url"):
                logging.warning("No link found for recipient %s", recipient.get("full_name") or email)
                skipped.append(recipient["data"])
                continue

            body_template = _render_template(
                employee=recipient,
                employee_month=month,
                employee_year=year,
                recipient_type=payload.recipient_type,
                url=link_info["url"]
            )
            logging.info("Sending email to recipients...")
            gmail_service.send_email(email, f"RE: {payload.branch.value} Monthly Performance", body_template)
            sent.append(email)
        return JSONResponse(
            content={
                "status": "success"
            },
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        logging.error(f"Exception occurred: {e}")
        return JSONResponse(
            content={
                "status": "error",
                "message": str(e)
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@router.post("/send-grm-email")
def send_grm_url(
    payload: BranchEmailRequest,
    gmail_service: GmailService = Depends(get_gmail_service),
    gsheet_service: GSheetService = Depends(get_gsheet_service),
    year: int = Query(None, description="Assessment year for the employee."),
    month: int = Query(None, description="Assessment month for the employee."),
    grm_email: str = Query(..., description="GRM you want to look up.")
):
    recipients = _build_recipient_list(payload.branch, payload.recipient_type, gsheet_service)
    grm_email_lower = grm_email.lower()
    grm_recipient = next(
        (r for r in recipients if r["email"].lower() == grm_email_lower),
        None
    )

    if not grm_recipient:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No employees found for branch '{payload.branch}'"
        )

    year, month = _default_month_year(year, month)

    try:
        logging.info("Collecting employee links...")
        links = generate_employee_links(
            base_url=SC_BASE_URL,
            year=year,
            month=month,
            grm_email=grm_email
        )
        managed_links = [
            {"name": name.title(), "url": info["url"]}
            for name, info in links.items()
            if name.upper() != grm_recipient["data"]["grm_name"].upper()
        ]
        
        body_template = _render_grm_email(
            employee=grm_recipient,
            managed_links=managed_links,
            employee_month=month,
            employee_year=year,
            recipient_type=payload.recipient_type.value
        )
        logging.info("Sending email to recipients...")
        gmail_service.send_email(
            recipient_email=grm_email,
            subject=f"RE: {payload.recipient_type.value} {payload.branch.value} Monthly Performance Report",
            body=body_template
        )
        return JSONResponse(
            content={
                "status": "success"
            },
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        logging.error(f"Exception occurred: {e}")
        return JSONResponse(
            content={
                "status": "error",
                "content": "Error sending email."
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )