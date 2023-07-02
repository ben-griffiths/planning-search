import base64
import json
from datetime import datetime, timedelta

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from locations.abstract import AbstractScraper


class LondonScraper(AbstractScraper):
    def get_next_button(self):
        return [
            e
            for e in self.driver.find_elements(By.TAG_NAME, "button")
            if e.get_attribute("textContent") == "Next"
        ][0]

    def goto_results_page(self, week):
        dt = datetime.now() - timedelta(weeks=1 + week)
        data = {
            "category": "weekly_lists_valid",
            "start_date": dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "resource_name": "weekly_lists",
            "type": "soql",
            "url": "https://planning.london.gov.uk/pr/s/",
        }
        json_string = json.dumps(data)
        bytes_data = json_string.encode("utf-8")
        base64_encoded = base64.b64encode(bytes_data).decode("utf-8")

        self.driver.get(
            f"https://planning.london.gov.uk/pr/s/pr-search-results?search={base64_encoded}"
        )
        return True

    def parse_page(self, elements):
        columns_names = [
            e.get_attribute("textContent").replace("Sort ", "")
            for e in elements[0].find_elements(By.TAG_NAME, "th")
            if e.get_attribute("textContent").replace("Sort ", "")
        ] + ["detail_url"]
        data = [
            [
                e.get_attribute("textContent")
                for e in r.find_elements(By.TAG_NAME, "td")[1:]
            ]
            + [
                self.parse_url(g.get_attribute("href"))
                for g in r.find_elements(By.TAG_NAME, "a")
            ]
            for r in elements[1:]
        ]

        results = [{key: value for key, value in zip(columns_names, d)} for d in data]
        results = [
            {
                "address": r["Address"],
                "validation_date": r["Valid Date"],
                "proposal": r["Proposal"],
                "reference_no": r["Name"],
                "detail_url": r["detail_url"],
            }
            for r in results
            if r
        ]

        return results

    def get_elements(self):
        return self.driver.find_elements(By.TAG_NAME, "tr")

    def wait_for(self):
        return WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "table"))
        )
