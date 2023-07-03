from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait

from locations.abstract import AbstractScraper


class PublicAccessScraper(AbstractScraper):
    def __init__(self, driver, index_results, url, date_field="Validated"):
        self.url = url
        self.date_field = date_field
        super().__init__(driver, index_results)

    def get_next_button(self):
        try:
            return self.driver.find_element(By.CLASS_NAME, "next")
        except:
            return None

    def goto_results_page(self, week):
        self.driver.get(self.url)
        try:
            search = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "input[type='submit'][value='Search']")
                )
            )
            select = Select(self.driver.find_element(By.NAME, "week"))
            select.select_by_index(week)
        except:
            return False

        search.click()
        return True

    def parse_page(self, elements):
        results = []
        for e in elements:
            title = (
                e.find_element(By.TAG_NAME, "a").get_attribute("textContent").strip()
            )
            address = (
                e.find_element(By.CLASS_NAME, "address")
                .get_attribute("textContent")
                .strip()
            )
            metainfo_string = (
                e.find_element(By.CLASS_NAME, "metaInfo")
                .get_attribute("textContent")
                .strip()
            )
            metainfo_array = [
                k.replace("|", "").strip()
                for m in metainfo_string.split(":")
                for k in m.split("\n")
                if k.replace("|", "").strip()
            ]
            metainfo = {
                metainfo_array[2 * i]: metainfo_array[2 * i + 1]
                for i in range(len(metainfo_array) // 2)
            }

            detail_url = e.find_element(By.TAG_NAME, "a").get_attribute("href")

            results.append(
                {
                    "address": address,
                    "validation_date": metainfo["Validated"],
                    "proposal": title,
                    "reference_no": metainfo["Ref. No"],
                    "detail_url": detail_url,
                }
            )

        return results

    def get_elements(self):
        return self.driver.find_elements(By.CLASS_NAME, "searchresult")

    def wait_for(self):
        try:
            return WebDriverWait(self.driver, 1).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//*[contains(text(), 'No results')]")
                )
            )
        except:
            return WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "searchresults"))
            )
