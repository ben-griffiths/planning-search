import functools
import time
import traceback
from abc import ABC, abstractmethod
from urllib.parse import urljoin, urlparse


def ignore_errors(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"Error occurred in {func.__name__}: {str(e)}")

    return wrapper


class AbstractScraper(ABC):
    WEEK_LIMIT = 52
    PAGE_LIMIT = 100

    def parse_url(self, href):
        parsed_url = urlparse(href)
        if parsed_url.netloc == "":
            # Relative URL
            absolute_url = urljoin(self.driver.current_url, href)
        else:
            # Absolute URL
            absolute_url = href
        return absolute_url

    @ignore_errors
    @abstractmethod
    def goto_results_page(self, week):
        pass

    @abstractmethod
    def get_next_button(self):
        pass

    @abstractmethod
    def parse_page(self, elements):
        pass

    @abstractmethod
    def get_elements(self):
        pass

    @abstractmethod
    def wait_for(self):
        pass

    def __init__(self, driver, index_results):
        self.driver = driver
        self.index_results = index_results

    def run(self, starting_week=0):
        results = []
        for i in range(starting_week, self.WEEK_LIMIT):
            if not self.goto_results_page(i):
                break
            week_results = self.scrape_table()
            print(f"scraped {len(week_results)} - week {i}")
            results += week_results
        return results

    def scrape_table(self):
        results = []
        last_elements = None

        try:
            self.wait_for()

            for i in range(self.PAGE_LIMIT):
                elements = self.get_elements()

                ### Broken next button safety check
                if elements == last_elements:
                    print(f"page {i} no change detected")
                    break
                last_elements = elements
                ###

                page = self.parse_page(elements)
                results += page

                self.index_results(page)
                print(f"page {i} complete - {len(page)} found")

                nextButton = self.get_next_button()
                if not nextButton or not nextButton.is_enabled():
                    break
                nextButton.click()
                time.sleep(0.2)
        except:
            print("HANDLED ERROR:")
            traceback.print_exc()

        return results
