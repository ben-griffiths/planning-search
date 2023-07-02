import functools
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

    def __init__(self, driver):
        self.driver = driver

    def run(self):
        results = []
        for i in range(self.WEEK_LIMIT):
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
                    break
                last_elements = elements
                ###

                results += self.parse_page(elements)

                print(f"page {i} complete - {len(results)} found")

                nextButton = self.get_next_button()
                if not nextButton or not nextButton.is_enabled():
                    break
                nextButton.click()
        except:
            traceback.print_exc()

        return results
