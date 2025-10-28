from typing import Literal, Optional, Union
from pydantic import BaseModel, EmailStr
import calendar

EMAIL_TEMPLATES = {
    "GRM": """
Hi {first_name} {last_name}, 

Good day!

As part of the HR Performance Management initiative, we are pleased to share the updated Performance Report Cards of your team under the Vehicle Sales Department for the month of {month} {year}.

These report cards summarize each team member’s individual performance based on the established KPIs and departmental targets. We encourage you to review these results to assess your team’s overall progress, identify top-performing employees, and address areas that may require additional coaching or support.

Please find attached the consolidated links for your reference.

SC Report Cards:

{managed_links}

Thank you for your continued leadership and support in driving the department’s success.
    """,
    "SC": """
To: {email_address}

Hi {first_name} {last_name}, 

Good day!

As part of our commitment to support your growth and success, we are sharing with you your Performance Report Card for the month of {month} {year}.

This report provides a summary of your individual performance and achievements during the month, reflecting your progress against the department’s goals and expectations. We encourage you to review the details and take note of both your strengths and the areas where improvements can be made.

Please find your updated Monthly Performance Report Card attached for your reference.

Should you have any questions or would like to discuss your results further, feel free to reach out to your immediate supervisor."

View it here: {url}
""",
"Default": """
Hello {first_name} {last_name},

Your latest report is ready.
View it here: {url}
    """
}

class User(BaseModel):
    first_name: str
    last_name: str
    email_address: EmailStr
    month: int
    year: int
    department: Literal["SC", "GRM"]
    url: Optional[str] = None
    managed_links: Optional[str] = None

def _format_month(month_value: Optional[Union[int, str]]) -> str:
    if month_value is None:
        return ""
    try:
        month_int = int(month_value)
    except (TypeError, ValueError):
        return str(month_value)

    if 1 <= month_int <= 12:
        return calendar.month_name[month_int]
    return str(month_value)

def generate_email(user: Union[User, dict], employee_month: int, employee_year: int, url: str):
    user_model = User(**user) if isinstance(user, dict) else user

    template = EMAIL_TEMPLATES.get(
        user_model.department, EMAIL_TEMPLATES["Default"]
    ) or EMAIL_TEMPLATES["Default"]

    month_value = employee_month if employee_month else user_model.month
    year_value = employee_year if employee_year else user_model.year
    url_value = url if url else user_model.url
    managed_links = user_model.managed_links if user_model.department == "GRM" else None

    return template.format(
        first_name=user_model.first_name,
        last_name=user_model.last_name,
        email_address=user_model.email_address,
        month=_format_month(month_value),
        year=year_value,
        url=url_value,
        managed_links=managed_links
    )
