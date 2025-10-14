from typing import Optional, Literal
from app.common import (
    JSONResponse,
    SC_BASE_URL,
    APIRouter,
    status,
    Query,
    run
)

router = APIRouter()

@router.get("/get-sc")
def get_sc(
    dept: Literal["SC", "SC_TEST", "GRM"] = Query(..., description="SC or GRM"),
    year: int = Query(..., description="Year of data"),
    month: int = Query(..., ge=1, le=12, description="Month (1-12)"),
    limit: Optional[int] = Query(None, description="Number of employees"),
    employee_keys: Optional[list[str]] = Query(None, description="List of employee names")
):
    try:
        run(
            base_url=SC_BASE_URL,
            dept=dept,
            year=year,
            month=month,
            limit=limit,
            employee_keys=employee_keys,
            headless=False
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