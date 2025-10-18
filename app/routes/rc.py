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

router = APIRouter()

@router.get("/get-report-card")
def get_report_card(
    dept: Literal["SC", "SC_TEST", "GRM"] = Query(..., description="Dept: SC or GRM"),
    year: int = Query(..., description="Year of data"),
    month: int = Query(..., ge=1, le=12, description="Month (1-12)"),
    limit: Optional[int] = Query(None, description="Number of employees"),
    employee_keys: Optional[list[str]] = Query(None, description="List of employee names"),
    grm_email: Optional[str] = Query(None, description="GRM email to filter employees under them")
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