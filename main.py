from components import (
    LookerStudioURLBuilder,
    ReportDownloader,
    GSheetService,
    fetch_emails
)
from urllib.parse import unquote, urlparse, parse_qs
from config import Sheets, SC_BASE_URL
from collections import defaultdict
import logging
import json

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(level)s - %(message)s'
)

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

def generate_looker_urls(
    base_url: str,
    emails: dict[str, list[dict]],
    year: int,
    month: int
):
    logging.info("Generating Looker Studio URLs...")
    looker_urls = []
    for _, employees in emails.items():
        for emp in employees:
            url = LookerStudioURLBuilder(
                base_url=base_url,
                year=year,
                month=month,
                employee_name=f"{emp['sc_firstname']} {emp['sc_lastname']}".upper(),
                lang="en"
            ).get_looker_url()
            looker_urls.append(url)
    return looker_urls

def parse_employee_names(urls: list[str]) -> list:
    names = []
    for url in urls:
        parsed = parse_qs(urlparse(url).query)
        params_encoded = parsed["params"][0]
        params_decoded = unquote(params_encoded)
        params_dict = json.loads(params_decoded)
        names.append(params_dict["ds0.sc_employee_name"])
    return names

def generate_employee_report_card(
    url: str,
    dept: str,
    employee_name: str,
    headless: bool = False
):
    logging.info(f"Generating report card for {employee_name}")
    downloader = ReportDownloader(
        url=url,
        dept=dept,
        employee_name=employee_name,
        headless=headless
    )
    logging.info("Done!")
    downloader.run_automation()

def generate_employee_links(
    base_url: str,
    year: int,
    month: int
):
    gsheet = GSheetService(
        service_account_file="licahr_email.json",
        spreadsheet_id=Sheets.EMAIL_MASTERLIST.id,
        spreadsheet_range=Sheets.EMAIL_MASTERLIST.range
    )
    emails = fetch_emails(gsheet=gsheet)
    grouped = group_by_boss(employees=emails)
    looker_urls = generate_looker_urls(base_url, grouped, year, month)
    employees = parse_employee_names(looker_urls)
    return {employee: url for employee, url in zip(employees, looker_urls)}

if __name__ == "__main__":
    links = generate_employee_links(base_url=SC_BASE_URL, year=2025, month=9)
    name = list(links.keys())[0]
    url = list(links.values())[0]
    generate_employee_report_card(
        url=url,
        dept="SC_TEST",
        employee_name=name,
        headless=False
    )