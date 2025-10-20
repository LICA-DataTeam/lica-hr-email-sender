from components import (
    LookerStudioURLBuilder,
    GoogleServiceFactory,
    ReportDownloader
)
from urllib.parse import unquote, urlparse, parse_qs
from collections import defaultdict
from config import (
    SERVICE_FILE,
    GRM_BASE_URL,
    SC_BASE_URL,
    Sheets
)
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

def group_by_branch(employees: list[dict]) -> dict[str, list[dict]]:
    """
    Groups the employees by branch.

    Returns:
    
    ```python
    {
        "Shaw": [emp1, emp2, ...],
        "Batangas": [emp1, emp2, ...],
        ...
    }
    ```
    """
    grouped = defaultdict(list)
    for emp in employees:
        grouped[emp["branch"]].append(emp)
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
            if base_url == SC_BASE_URL:
                emp_name = f"{emp['sc_firstname']} {emp['sc_lastname']}"
            elif base_url == GRM_BASE_URL:
                emp_name = f"{emp['grm_name']}" # do some processing
            url = LookerStudioURLBuilder(
                base_url=base_url,
                year=year,
                month=month,
                employee_name=emp_name.upper(),
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
    month: int,
    grm_email: str = None
):
    config = {
        "service_account_file": SERVICE_FILE,
        "spreadsheet_id": Sheets.EMAIL_MASTERLIST.id,
        "spreadsheet_range": Sheets.EMAIL_MASTERLIST.range
    }
    gsheet = GoogleServiceFactory.create("gsheet", config)
    emails = gsheet.fetch_emails()

    if grm_email:
        employee_under_grm = [emp for emp in emails if emp["grm_email_address"].lower() == grm_email.lower()]
        if not employee_under_grm:
            raise ValueError(f"No employees found for: {grm_email}")

        grm_full_name = employee_under_grm[0]["grm_name"].upper()
        logging.info(f"GRM FULL NAME: {grm_full_name}")

        employee_under_grm.append({
            "sc_firstname": grm_full_name.split()[0],
            "sc_lastname": " ".join(grm_full_name.split()[1:]),
            "grm_email_address": grm_email,
            "grm_name": grm_full_name
        })
        emails = employee_under_grm

    grouped = group_by_boss(employees=emails)
    looker_urls = generate_looker_urls(base_url, grouped, year, month)
    employees = parse_employee_names(looker_urls)
    return {employee: url for employee, url in zip(employees, looker_urls)}

def run(
    base_url: str,
    dept: str,
    year: int,
    month: int,
    employee_keys: list[str] = None,
    limit: int = None,
    headless: bool = False,
    grm_email: str = None
):
    try:
        links = generate_employee_links(
            base_url=base_url,
            year=year,
            month=month,
            grm_email=grm_email
        )

        if employee_keys:
            links = {name: url for name, url in links.items() if any(emp_key in name for emp_key in employee_keys)}

        if limit:
            logging.info(f"Limit set to: {limit}")
            links = dict(list(links.items())[:limit])

        for name, url in links.items():
            generate_employee_report_card(
                url=url,
                dept=dept,
                employee_name=name,
                headless=headless
            )
    except Exception as e:
        import traceback
        traceback.print_exc()
        logging.error(f"Exception occurred: {e}")
        raise