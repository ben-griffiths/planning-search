from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait

from locations.abstract import AbstractScraper


class ChelseaScraper(AbstractScraper):
    def get_next_button(self):
        return None

    def goto_results_page(self, week):
        self.driver.get("https://www.rbkc.gov.uk/planning/scripts/weeklyform.asp")
        try:
            search = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "input[type='submit'][value='search']")
                )
            )
            select = Select(self.driver.find_element(By.NAME, "WeekEndDate"))
            select.select_by_index(week)
        except:
            return False

        search.click()
        return True

    def parse_page(self, elements):
        columns_names = [
            e.get_attribute("textContent").strip()
            for e in elements[0].find_elements(By.TAG_NAME, "th")
            if e.get_attribute("textContent").strip()
        ] + ["detail_url"]
        data = [
            [
                e.get_attribute("textContent").strip()
                for e in r.find_elements(By.TAG_NAME, "td")
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
                "validation_date": r["Received"],
                "proposal": r["Proposal"],
                "reference_no": r["TP no."],
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
