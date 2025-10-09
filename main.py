from components import ReportDownloader
from dotenv import load_dotenv
import os

load_dotenv()

if __name__ == "__main__":
    sc_url = os.getenv("SC_LOOKER_STUDIO_URL")

    downloader = ReportDownloader(
        url=sc_url,
        dept="SC",
        headless=False
    )

    downloader.run_automation()