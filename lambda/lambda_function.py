import json
import os
import requests
from opensearchpy import OpenSearch, RequestsHttpConnection
import boto3
from requests_aws4auth import AWS4Auth


def lambda_handler(event, context):
    # Extract the request path and body from the event
    request_path = event.get("rawPath", "")
    request_body = event.get("body", "")
    request_headers = event.get("headers", {})

    # Modify the request body or perform any necessary transformations

    if request_path.startswith("/maps"):
        # Proxy the request to the Google Maps API
        response = proxy_google_maps_api(request_headers)
        return {
            "statusCode": 200,
            "body": response,
            "headers": {"Content-Type": "text/html"},
        }

    else:
        # Forward the request to the OpenSearch service
        response = forward_request_to_opensearch(request_body)
        return {"statusCode": 200, "body": json.dumps(response)}


def forward_request_to_opensearch(request_body):
    region = "eu-west-2"
    service = "es"

    credentials = boto3.Session().get_credentials()
    aws_auth = AWS4Auth(
        credentials.access_key,
        credentials.secret_key,
        region,
        service,
        session_token=credentials.token,
    )

    # Send the request to OpenSearch
    opensearch = OpenSearch(
        hosts=[
            "https://search-planning-search-35kjlvnypvrj5cqcmefsnktxla.eu-west-2.es.amazonaws.com/"
        ],
        http_auth=aws_auth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection,
    )

    results = opensearch.search(index="index", body=request_body)

    return results


def proxy_google_maps_api(request_headers):
    api_key = os.getenv("GOOGLE_API_KEY")
    url = f"https://maps.googleapis.com/maps/api/js?key={api_key}&libraries=places"

    response = requests.get(
        url, headers={k: v for k, v in request_headers.items() if k != "host"}
    )
    return response.text
