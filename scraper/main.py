import os
import sys

from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from common import get_geocode
from locations.basingstoke import BasingstokeScraper
from locations.chlesea import ChelseaScraper
from locations.london import LondonScraper
from locations.reading import ReadingScraper


def get_opensearch():
    aws_access_key = os.getenv("AWS_ACCESS_KEY")
    aws_secret_key = os.getenv("AWS_SECRET_KEY")
    aws_region = "eu-west-2"
    aws_service = "es"

    aws_auth = AWS4Auth(aws_access_key, aws_secret_key, aws_region, aws_service)
    opensearch = OpenSearch(
        hosts=[
            "https://search-planning-search-35kjlvnypvrj5cqcmefsnktxla.eu-west-2.es.amazonaws.com/"
        ],
        http_auth=aws_auth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection,
    )
    return opensearch


def get_chrome_driver():
    chrome_options = Options()
    # chrome_options.add_argument("--headless=new")
    # chrome_options.add_argument("--window-size=1280,700")
    # chrome_options.add_argument("--headless")
    return webdriver.Chrome(options=chrome_options)


if __name__ == "__main__":
    index_name = os.getenv("INDEX_NAME", "index")
    google_maps_api_key = os.getenv("GOOGLE_MAPS_API_KEY")

    driver = get_chrome_driver()

    SCRAPERS = {
        "reading": ReadingScraper(driver),
        "london": LondonScraper(driver),
        "basingstoke": BasingstokeScraper(driver),
        "chelsea": ChelseaScraper(driver),
    }

    location = sys.argv[1]

    # Scrape location
    try:
        results = SCRAPERS[location].run()
    finally:
        driver.quit()

    # Geocode Results
    success_count, fail_count = 0, 0
    for i, r in enumerate(results):
        lat, lng = get_geocode(r["address"], google_maps_api_key)
        value = f"{lat},{lng}" if lat and lng else None
        results[i]["location"] = value
        if value:
            success_count += 1
        else:
            fail_count += 1
        if i % 10 == 0:
            print(f"Geocode success count: {success_count} - fail_count: {fail_count}")

    # Index Results
    opensearch = get_opensearch()

    for i in range(len(results) // 100 + 1):
        for doc in results[100 * i : 100 * (i + 1)]:
            doc["source"] = location
            document_id = doc["reference_no"]
            opensearch.index(index=index_name, id=document_id, body=doc)
        opensearch.indices.refresh(index=index_name)
        print(f"indexed {100 * (i + 1)} / {len(results)}")
    print("index success")
