from playwright.sync_api import (
    sync_playwright,
    Browser,
    Page
)
from typing import Literal
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class ReportDownloader:
    def __init__(
        self,
        url: str = None,
        dept: Literal["SC", "SC_TEST", "GRM"] = None,
        employee_name: str = None,
        headless: bool = False,
        slow_mo: int = 100
    ):
        self.logger = logging.getLogger(__name__)
        self.url = url
        self.dept = dept
        self.employee_name = employee_name
        self.headless = headless
        self.slow_mo = slow_mo
        
        self.sync_playwright_instance = None
        self.browser: Browser = None
        self.page: Page = None

    def _get_sync_playwright_instance(self):
        try:
            self.sync_playwright_instance = sync_playwright().start()
            self.logger.info(f"Created sync_playwright instance: {self.sync_playwright_instance}")
            return self.sync_playwright_instance
        except Exception as e:
            self.logger.error(f"Error creating playwright instance: {e}")

    def _launch_browser(self, playwright):
        self.logger.info("Launching chromium browser...")
        self.browser = playwright.chromium.launch(
            headless=self.headless,
            slow_mo=self.slow_mo
        )
        self.page = self.browser.new_page()

    def _navigate_to_page(self):
        self.logger.info(f"Opening website ({self.url})...")
        try:
            self.page.goto(
                self.url,
                wait_until="load",
                timeout=30000
            )
            self.logger.info("Page loaded!")
            self.page.wait_for_timeout(2000)
        except Exception as e:
            self.logger.error(f"Error loading web page: {e}")
            self._close_browser()
            raise

    def _close_browser(self):
        if self.browser:
            self.browser.close()

    def _download_report_card(self, dept: str, filename: str):
        self.logger.info("Downloading report card...")
        try:
            self.logger.info("Locating 'Download report' button...")
            self.page.click("mat-icon:has-text('arrow_drop_down')")
            self.page.click("button:has-text('Download report')")
            self.logger.info("Found! Clicked!")

            self.page.click("md-radio-button[aria-label='Select Pages']")
            self.logger.info(f"Selecting {dept}...")
            self.page.click(f"div.pageName:has-text('{dept}')")

            with self.page.expect_download() as file:
                self.page.click("button.download-button:has-text('Download')")
            download = file.value
            download.save_as(f"./tmp/report_cards/{dept}/{filename}.pdf")
            self.page.wait_for_timeout(2500)
            self.logger.info("Done downloading!")
        except Exception as e:
            self.logger.error(f"Error downloading report card: {e}")

    def run_automation(self):
        self.logger.info("Running automation...")
        p = self._get_sync_playwright_instance()
        try:
            self._launch_browser(p)
            self._navigate_to_page()
            self._download_report_card(dept=self.dept, filename=f"{self.dept}_{self.employee_name}")
        finally:
            self._close_browser()
            if self.sync_playwright_instance:
                self.sync_playwright_instance.stop()