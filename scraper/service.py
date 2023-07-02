import base64
import json
from datetime import datetime, timedelta
import os

import requests
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.select import Select

import requests


def get_geocode(address, api_key):
    endpoint = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": address,
        "region": "gb",
        "key": api_key,
    }

    try:
        response = requests.get(endpoint, params=params)
        data = response.json()

        if response.status_code == 200 and data["status"] == "OK":
            # Extract the geocode information
            results = data["results"]
            if results:
                geometry = results[0].get("geometry")
                if geometry:
                    location = geometry.get("location")
                    if location:
                        lat = location.get("lat")
                        lng = location.get("lng")
                        return lat, lng

    except requests.exceptions.RequestException as e:
        pass

    return None, None


def scrape_table(driver):
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "table"))
    )

    results = []
    last_elements = None
    for _ in range(10):
        elements = driver.find_elements(By.TAG_NAME, "tr")

        ### Broken next button safety check
        if elements == last_elements:
            break
        last_elements = elements
        ###

        columns_names = [
            e.get_attribute("textContent").replace("Sort ", "")
            for e in elements[0].find_elements(By.TAG_NAME, "th")
            if e.get_attribute("textContent").replace("Sort ", "")
        ]
        data = [
            [
                e.get_attribute("textContent")
                for e in r.find_elements(By.TAG_NAME, "td")
            ][1:]
            for r in elements
        ]
        results += [{key: value for key, value in zip(columns_names, d)} for d in data]

        ### Next page
        nextButton = [
            e
            for e in driver.find_elements(By.TAG_NAME, "button")
            if e.get_attribute("textContent") == "Next"
        ][0]
        if not nextButton.is_enabled():
            break
        nextButton.click()
        ##
    return results


def scrape_list(driver):
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "searchresults"))
    )
    results = []
    last_elements = None
    for _ in range(10):
        elements = driver.find_elements(By.CLASS_NAME, "searchresult")

        ### Broken next button safety check
        if elements == last_elements:
            break
        last_elements = elements
        # ###

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

        ### Next page
        try:
            nextButton = driver.find_element(By.CLASS_NAME, "next")
            nextButton.click()
        except Exception as e:
            break
    return results


def scrape_london(driver: webdriver.Chrome, dt: datetime):
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

    driver.get(
        f"https://planning.london.gov.uk/pr/s/pr-search-results?search={base64_encoded}"
    )

    results = scrape_table(driver)
    results = [
        {
            "address": r["Address"],
            "validation_date": r["Valid Date"],
            "proposal": r["Proposal"],
            "reference_no": r["Name"],
        }
        for r in results
        if r
    ]

    return results


def scrape_basingstoke(driver: webdriver.Chrome, i: int):
    results = None
    driver.get(
        "https://planning.basingstoke.gov.uk/online-applications/search.do?action=weeklyList"
    )

    search = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "input[type='submit'][value='Search']")
        )
    )
    select = Select(driver.find_element(By.NAME, "week"))
    select.select_by_index(i)

    search.click()

    try:
        WebDriverWait(driver, 1).until(
            EC.presence_of_element_located(
                (By.XPATH, "//*[contains(text(), 'No results')]")
            )
        )
        return []
    except:
        pass

    results = scrape_list(driver)

    results = [
        {
            "address": r["address"],
            "validation_date": r["Validated"],
            "proposal": r["title"],
            "reference_no": r["Ref. No"],
        }
        for r in results
        if r
    ]

    return results


if __name__ == "__main__":
    aws_access_key = os.get_env("AWS_ACCESS_KEY")
    aws_secret_key = os.get_env("AWS_SECRET_KEY")
    google_maps_api_key = os.get_env("GOOGLE_MAPS_API_KEY")
    aws_region = "eu-west-2"
    aws_service = "es"

    aws_auth = AWS4Auth(aws_access_key, aws_secret_key, aws_region, aws_service)

    chrome_options = Options()
    # chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--window-size=1280,700")
    # chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)
    index_name = "index"

    opensearch = OpenSearch(
        hosts=[
            "https://search-planning-search-35kjlvnypvrj5cqcmefsnktxla.eu-west-2.es.amazonaws.com/"
        ],
        http_auth=aws_auth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection,
    )
    try:
        results = []
        for i in range(52):
            page = scrape_basingstoke(driver, i)
            print(f"week {i} - found: {len(page)}")
            results += page

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
                print(f"success count: {success_count} - fail_count: {fail_count}")

        for doc in results:
            document_id = doc["reference_no"]
            opensearch.index(index=index_name, id=document_id, body=doc)

        opensearch.indices.refresh(index=index_name)
        print("index successful")
    except Exception as e:
        raise e
    finally:
        driver.quit()
