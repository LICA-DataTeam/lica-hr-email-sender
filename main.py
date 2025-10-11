from components import (
    LookerStudioURLBuilder,
    ReportDownloader,
    GSheetService,
    fetch_emails
)
from config import (
    SPREADSHEET_RANGE,
    SPREADSHEET_ID,
    SC_BASE_URL
)
from collections import defaultdict
import pyperclip
import logging
import json

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(level)s - %(message)s'
)

# FLOW:
# START -> Collect emails from GSheet -> LookerStudioURLBuilder & ReportDownloader to generate the employee report card -> Email Notifier Automation
def group_by_boss(employees: list[dict]) -> dict[str, list[dict]]:
    """
    Groups the SC employees by GRM.

    Returns a structure like this:

    ```python
    {
        "boss1@email.com": [
            {emp1},
            {emp2},
            ...
        ]
    }
    ```
    """
    grouped = defaultdict(list)
    for emp in employees:
        grouped[emp["grm_email_address"]].append(emp)
    return grouped

if __name__ == "__main__":
    # @app.get
    # def route1() -> str - get looker studio url
    # name: str, year: int, month: int, lang: Literal["en", "es", etc], is_clip: bool
    # name = "zian rosales"
    # url = LookerStudioURLBuilder(
    #     base_url=sc_url,
    #     year=2024,
    #     month=9,
    #     employee_name=name.upper(),
    #     lang="en",
    #     is_clip=True
    # ).get_looker_url()
    # logging.info("Done building URL!")
    # logging.info(url)

    # logging.info("Generating employee dashboard...")
    # downloader = ReportDownloader(
    #     url=url,
    #     dept="SC",
    #     headless=False
    # )
    # downloader.run_automation()
    gsheet = GSheetService(
        service_account_file="licahr_email.json",
        spreadsheet_id=SPREADSHEET_ID,
        spreadsheet_range=SPREADSHEET_RANGE
    )
    emails = fetch_emails(gsheet=gsheet)
    # print(json.dumps(
    #     emails,
    #     indent=2,
    #     ensure_ascii=False
    # ))
    grouped = group_by_boss(employees=emails)
    # print(json.dumps(grouped, indent=2, ensure_ascii=False))

    looker_urls = []
    for grm_email, employees in grouped.items():
        attachments = []
        for emp in employees[:1]:
            url = LookerStudioURLBuilder(
                base_url=SC_BASE_URL,
                year=2025,
                month=9,
                employee_name=f"{emp['sc_lastname']} {emp['sc_firstname']}".upper(),
                lang="en"
            ).get_looker_url()
            looker_urls.append(url)

    # Must have unified SC & GRM naming convention (Dashboard and Masterlist)
    print(json.dumps(
        looker_urls,
        indent=4,
        ensure_ascii=False
    ))
    pyperclip.copy(looker_urls[1])

    # sc_name = "analie azanon"
    # url = LookerStudioURLBuilder(
    #     base_url=SC_BASE_URL,
    #     year=2024,
    #     month=1,
    #     employee_name=sc_name.upper(),
    #     lang="en"
    # ).get_looker_url()

    # import pyperclip
    # pyperclip.copy(url)