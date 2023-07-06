import os
import random

from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth


def get_opensearch() -> OpenSearch:
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


if __name__ == "__main__":
    opensearch = get_opensearch()
    alias_name = "index"

    # Create a new index with the updated mapping
    mapping = {
        "properties": {
            "address": {"type": "text"},
            "validation_date": {"type": "text"},
            "proposal": {"type": "text"},
            "reference_no": {"type": "keyword"},
            "detail_url": {"type": "text"},
            "location": {"type": "geo_point"},
            "source": {"type": "keyword"},
            "related_industries": {
                "type": "nested",
                "properties": {
                    "code": {"type": "keyword"},
                    "relation_score": {"type": "float"},
                },
            },
        }
    }

    new_index = f"alias_name{random.randint(0, 1000)}"
    opensearch.indices.create(
        index=new_index, body={"mappings": mapping}, request_timeout=30
    )
    print(f"Created {new_index}")

    old_indices = opensearch.indices.get(index=f"{alias_name}*", request_timeout=30)
    print(f"Found: {old_indices}")

    for index in old_indices:
        # Reindex all documents from the existing index to the new index
        body = {"source": {"index": index}, "dest": {"index": new_index}}
        opensearch.reindex(body=body, wait_for_completion=True)
        print(f"Reindexed: {index}")
        opensearch.indices.refresh(index=new_index, request_timeout=30)

        # Delete the old index
        opensearch.indices.delete(index=index)
        print(f"Deleted: {index}")

    opensearch.indices.put_alias(index=new_index, name=alias_name, request_timeout=30)
