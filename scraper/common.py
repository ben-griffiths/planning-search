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
