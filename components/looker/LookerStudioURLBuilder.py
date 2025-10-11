import urllib.parse
import pyperclip
import logging
import json

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class LookerStudioURLBuilder:
    def __init__(
        self,
        base_url: str,
        year: int,
        month: int, # 1-12
        employee_name: str,
        lang: str,
        is_clip: bool = False
    ):
        self.logger = logging.getLogger(__name__)
        self.base_url = base_url
        self.year = year
        self.month = month
        self.employee_name = employee_name
        self.lang = lang
        self.is_clip = is_clip

    def _params_builder(self):
        params = {
            "ds0.sc_employee_year": self.year,
            "ds0.sc_employee_month": self.month,
            "ds0.sc_employee_name": self.employee_name
        }
        return params

    def get_looker_url(self):
        encoded = urllib.parse.quote(json.dumps(self._params_builder()))
        full_url = f"{self.base_url}?hl={self.lang}&params={encoded}"
        if self.is_clip:
            self.logger.info("Copied to clipboard!")
            pyperclip.copy(full_url)
        return full_url