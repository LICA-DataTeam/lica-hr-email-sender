from pydantic import BaseModel, EmailStr
from typing import Literal

EMAIL_TEMPLATES = {
    "GRM": None,
    "SC": """
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

def generate_email(user: User, url: str):
    template = EMAIL_TEMPLATES.get(
        user.department, EMAIL_TEMPLATES["Default"]
    )

    return template.format(
        first_name=user.first_name,
        last_name=user.last_name,
        url=url
    )