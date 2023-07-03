from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from locations.abstract import AbstractScraper


class ReadingScraper(AbstractScraper):
    WEEK_LIMIT = 1

    def get_next_button(self):
        return self.driver.find_element(
            By.XPATH,
            "//a[contains(text(), 'Next')]",
        )

    def goto_results_page(self, week):
        if week > 0:
            return False
        self.driver.get("http://planning.reading.gov.uk/fastweb_PL/welcome.asp")
        view = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//a[contains(text(), 'View current application')]")
            )
        )
        view.click()
        return True

    def parse_page(self, elements):
        results = []
        for element in elements:
            field_dict = {}
            for td_element in element.find_elements(
                By.XPATH, ".//td[@class='RecordTitle' or @class='RecordDetail']"
            ):
                # Get the field name from the <td> element with class 'RecordTitle'
                if td_element.get_attribute("class") == "RecordTitle":
                    field_name = td_element.text.strip(":")
                # Get the field value from the <td> element with class 'RecordDetail'
                elif td_element.get_attribute("class") == "RecordDetail":
                    field_value = td_element.text.strip()
                    # Store the field name and value in the dictionary
                    if field_name and field_value:
                        field_dict[field_name] = field_value

                a_tags = td_element.find_elements(By.TAG_NAME, "a")
                if a_tags:
                    field_dict["detail_url"] = self.parse_url(
                        a_tags[0].get_attribute("href")
                    )
            if field_dict:
                results.append(field_dict)

        results = [
            {
                "address": r["Site Address"],
                "validation_date": r["Received Date"],
                "proposal": r["Description"],
                "reference_no": r["App. No."],
                "detail_url": r["detail_url"],
            }
            for r in results
            if r
            and r.get("Site Address")
            and r.get("Received Date")
            and r.get("Description")
            and r.get("App. No.")
            and r.get("detail_url")
        ]
        return results

    def get_elements(self):
        return self.driver.find_elements(By.TAG_NAME, "tbody")

    def wait_for(self):
        return WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "table"))
        )
