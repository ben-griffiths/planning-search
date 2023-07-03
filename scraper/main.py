import importlib
import os
import sys

from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from common import get_geocode
from locations.public_access import PublicAccessScraper

NOT_SUPPORTED = {"https://my.redbridge.gov.uk/planning"}

PUBLIC_ACCESS_SOURCES = {
    "basingstoke": "https://planning.basingstoke.gov.uk/online-applications/search.do?action=weeklyList",
    "fulham": (
        "https://public-access.lbhf.gov.uk/online-applications/search.do?action=weeklyList",
        "Registered",
    ),
    "leeds": "https://publicaccess.leeds.gov.uk/online-applications/search.do?action=weeklyList",
    "manchester": "https://pa.manchester.gov.uk/online-applications/search.do?action=weeklyList",
    "newham": "https://pa.newham.gov.uk/online-applications/search.do?action=weeklyList",
    "watford": "https://pa.watford.gov.uk/publicaccess/search.do?action=weeklyList",
    "brentwood": "https://publicaccess.brentwood.gov.uk/online-applications/search.do?action=weeklyList",
    "eastsuffolk": "https://publicaccess.eastsuffolk.gov.uk/online-applications/search.do?action=weeklyList",
    "eastherts": "https://publicaccess.eastherts.gov.uk/online-applications/search.do?action=weeklyList",
    "cityoflondon": "https://www.planning2.cityoflondon.gov.uk/online-applications/search.do?action=weeklyList",
    "woking": "https://caps.woking.gov.uk/online-applications/search.do?action=weeklyList",
    "buckinghamshire": "https://publicaccess.buckscc.gov.uk/online-applications/search.do?action=weeklyList",
    "enfield": "https://planningandbuildingcontrol.enfield.gov.uk/online-applications/search.do?action=weeklyList",
    "eastriding": "https://newplanningaccess.eastriding.gov.uk/newplanningaccess/search.do?action=weeklyList",
    "chichester": "https://publicaccess.chichester.gov.uk/online-applications/search.do?action=weeklyList",
    "newark": "https://publicaccess.newark-sherwooddc.gov.uk/online-applications/search.do?action=weeklyList",
    "eling": "https://pam.ealing.gov.uk/online-applications/search.do?action=weeklyList",
    "maldon": "https://publicaccess.maldon.gov.uk/online-applications/search.do?action=weeklyList",
    "westminster": "https://idoxpa.westminster.gov.uk/online-applications/search.do?action=weeklyList",
    "dartford": "https://publicaccess.dartford.gov.uk/online-applications/search.do?action=weeklyList",
    "brent": "https://pa.brent.gov.uk/online-applications/search.do?action=weeklyList",
    "bromley": "https://searchapplications.bromley.gov.uk/online-applications/search.do?action=weeklyList",
}


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


def get_scrapers(index_results):
    scrapers = {}
    # Get the list of files in the 'locations/' directory
    file_list = os.listdir("locations/")

    # Iterate over the files in the directory
    for file_name in file_list:
        # Check if the file ends with '.py' and is not '__init__.py'
        if (
            file_name.endswith(".py")
            and not file_name.startswith("__init__")
            and not file_name == ("abstract.py")
            and not file_name == ("public_access.py")
        ):
            # Remove the '.py' extension from the file name
            module_name = file_name[:-3]

            # Create the file path
            module_path = os.path.join("locations", file_name)

            # Load the module dynamically
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Add the scraper to the SCRAPERS dictionary
            scraper_name = module_name.capitalize() + "Scraper"
            scrapers[module_name] = getattr(module, scraper_name)(driver, index_results)
    for module_name, args in PUBLIC_ACCESS_SOURCES.items():
        scrapers[module_name] = PublicAccessScraper(
            driver, index_results, *args if type(args) == tuple else (args,)
        )
    return scrapers


if __name__ == "__main__":
    index_name = os.getenv("INDEX_NAME", "index")
    google_maps_api_key = os.getenv("GOOGLE_MAPS_API_KEY")

    driver = get_chrome_driver()

    location = sys.argv[1]
    starting_week = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    opensearch = get_opensearch()

    def index_results(results):
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
        print(f"  Geocode success count: {success_count} - fail_count: {fail_count}")

        # Index Results
        for doc in results:
            doc["source"] = location
            document_id = doc["reference_no"]
            opensearch.index(
                index=index_name,
                id=document_id,
                body=doc,
                request_timeout=30,
            )
        opensearch.indices.refresh(index=index_name)
        print(f"  Indexed {len(results)}")

    SCRAPERS = get_scrapers(index_results)

    # Scrape location
    try:
        SCRAPERS[location].run(starting_week)
    finally:
        driver.quit()
