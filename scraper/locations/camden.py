from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from locations.abstract import AbstractScraper


class CamdenScraper(AbstractScraper):
    WEEK_LIMIT = 1

    def get_next_button(self):
        try:
            return self.driver.find_element(
                By.ID, "searchForm:j_idt132:commandLinkNext"
            )
        except:
            print("fail")
            return None

    def goto_results_page(self, week):
        self.driver.get(
            "https://accountforms.camden.gov.uk/planning-search/index.xhtml?faces-redirect=true&search=*&page=1&sortBy=RELEVANCY"
        )
        return True

    def parse_page(self, elements):
        results = []
        for e in elements:
            field_elements = []
            for p in e.find_elements(By.TAG_NAME, "p"):
                field_elements += p.find_elements(By.TAG_NAME, "span") or [p]
            data = [f.get_attribute("textContent").strip() for f in field_elements]
            detail_url = e.find_element(By.TAG_NAME, "a").get_attribute("href")

            results.append(
                {
                    "address": data[0].split("(")[0].strip(),
                    "validation_date": data[2]
                    .split("\n")[0]
                    .translate(str.maketrans("", "", "()-"))
                    .strip(),
                    "proposal": data[3],
                    "reference_no": data[0]
                    .split("(")[1]
                    .translate(str.maketrans("", "", "()-"))
                    .strip(),
                    "detail_url": detail_url,
                }
            )

        return results

    def get_elements(self):
        return self.driver.find_elements(By.CLASS_NAME, "planning-application-item")

    def wait_for(self):
        return WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "planning-application-item"))
        )
