from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait

from locations.abstract import AbstractScraper


class BasingstokeScraper(AbstractScraper):
    def get_next_button(self):
        return self.driver.find_element(By.CLASS_NAME, "next")

    def goto_results_page(self, week):
        self.driver.get(
            "https://planning.basingstoke.gov.uk/online-applications/search.do?action=weeklyList"
        )
        search = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "input[type='submit'][value='Search']")
            )
        )
        select = Select(self.driver.find_element(By.NAME, "week"))
        select.select_by_index(week)

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

            data = {"title": title, "address": address, **metainfo}
            results.append(data)
        return results

    def get_elements(self):
        return self.driver.find_elements(By.CLASS_NAME, "searchresult")

    def wait_for(self):
        return WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "searchresults"))
        )


# def scrape_list(driver):
#     WebDriverWait(driver, 10).until(
#         EC.presence_of_element_located((By.ID, "searchresults"))
#     )
#     results = []
#     last_elements = None
#     for _ in range(10):
#         elements = driver.find_elements(By.CLASS_NAME, "searchresult")

#         ### Broken next button safety check
#         if elements == last_elements:
#             break
#         last_elements = elements
#         # ###

#         for e in elements:
#             title = (
#                 e.find_element(By.TAG_NAME, "a").get_attribute("textContent").strip()
#             )
#             address = (
#                 e.find_element(By.CLASS_NAME, "address")
#                 .get_attribute("textContent")
#                 .strip()
#             )
#             metainfo_string = (
#                 e.find_element(By.CLASS_NAME, "metaInfo")
#                 .get_attribute("textContent")
#                 .strip()
#             )
#             metainfo_array = [
#                 k.replace("|", "").strip()
#                 for m in metainfo_string.split(":")
#                 for k in m.split("\n")
#                 if k.replace("|", "").strip()
#             ]
#             metainfo = {
#                 metainfo_array[2 * i]: metainfo_array[2 * i + 1]
#                 for i in range(len(metainfo_array) // 2)
#             }

#             data = {"title": title, "address": address, **metainfo}
#             results.append(data)

#         ### Next page
#         try:
#             nextButton = driver.find_element(By.CLASS_NAME, "next")
#             nextButton.click()
#         except Exception:
#             break
#     return results


# def scrape(driver: webdriver.Chrome, i: int):
#     results = None
#     driver.get(
#         "https://planning.basingstoke.gov.uk/online-applications/search.do?action=weeklyList"
#     )
#     search = WebDriverWait(driver, 10).until(
#         EC.presence_of_element_located(
#             (By.CSS_SELECTOR, "input[type='submit'][value='Search']")
#         )
#     )
#     select = Select(driver.find_element(By.NAME, "week"))
#     select.select_by_index(i)

#     search.click()

#     try:
#         WebDriverWait(driver, 1).until(
#             EC.presence_of_element_located(
#                 (By.XPATH, "//*[contains(text(), 'No results')]")
#             )
#         )
#         return []
#     except:
#         pass

#     results = scrape_list(driver)

#     results = [
#         {
#             "address": r["address"],
#             "validation_date": r["Validated"],
#             "proposal": r["title"],
#             "reference_no": r["Ref. No"],
#         }
#         for r in results
#         if r
#     ]

#     return results
