from typing import Optional, Literal
from app.common import (
    JSONResponse,
    SC_BASE_URL,
    GRM_BASE_URL,
    APIRouter,
    status,
    Query,
    run
)

from components.run import generate_employee_links
import pyperclip

router = APIRouter()

@router.get("/get-report-card")
def get_report_card(
    dept: Literal["SC", "SC_TEST", "GRM"] = Query(..., description="Dept: SC or GRM"),
    year: int = Query(..., description="Year of data"),
    month: int = Query(..., ge=1, le=12, description="Month (1-12)"),
    limit: Optional[int] = Query(None, description="Number of employees"),
    employee_keys: Optional[list[str]] = Query(default=[], description="List of employee names"),
    grm_email: Optional[str] = Query(default=None, description="GRM email to filter employees under them")
):
    try:
        if dept:
            if dept == "SC" or dept == "SC_TEST":
                base_url = SC_BASE_URL
            elif dept == "GRM":
                base_url = GRM_BASE_URL
        run(
            base_url=base_url,
            dept=dept,
            year=year,
            month=month,
            limit=limit,
            employee_keys=employee_keys,
            headless=False,
            grm_email=grm_email
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

@router.get("/get-employee-url")
def get_employee_url(
    year: int = Query(..., description="Assessment year for the employee."),
    month: int = Query(..., description="Assessment month for the employee."),
    emp_key: list[str] = Query(None, description="Employee key you want to look up."),
    grm_email: str = Query(None, description="GRM you want to look up."),
    is_copy: bool = Query(False, description="Copy to clipboard.")
):
    try:
        base_url = GRM_BASE_URL if grm_email else SC_BASE_URL
        links = generate_employee_links(
            base_url=base_url,
            year=year,
            month=month,
            grm_email=grm_email if grm_email else None
        )

        if emp_key:
            links = {name: url for name, url in links.items() if any(key in name for key in emp_key)}

        url_list = []
        name_list = []
        branch_list = []

        for names, data in links.items():
            name_list.append(names)
            url_list.append(data['url'])
            branch_list.append(data['branch'])

        first_name, last_name = name_list[0].split()[0], name_list[0].split()[-1]
        if is_copy:
            pyperclip.copy(url_list[0])

        return JSONResponse(
            content={
                "status": "success",
                "content": {
                    "last_name": last_name,
                    "first_name": first_name,
                    "url": url_list[0],
                    "branch": branch_list[0]
                }
            },
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        print(f"Error occurred: {e}")
        return JSONResponse(
            content={
                "status": "error",
                "message": "Exception occurred while getting employee Looker Studio URL."
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )