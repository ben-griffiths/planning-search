import config from "../../config";

export const doOpensearchQuery = async (searchTerm, source) => {
  const query = {
    bool: {
      must: {
        multi_match: {
          query: searchTerm || "",
          fields: ["reference_no", "address", "proposal", "source"],
          lenient: true,
          zero_terms_query: "all",
        },
      },
    },
  };

  if (source) {
    query.bool.filter = {
      terms: { source: source.split(",") },
    };
  }

  const payload = JSON.stringify({
    query,
    size: 100,
    sort: [
      {
        _doc: {
          order: "desc",
        },
      },
    ],
    aggs: {
      source_options: {
        terms: {
          field: "source",
          size: 10,
          min_doc_count: 0,
        },
      },
    },
  });

  const response = await fetch(config.apiUrl, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: payload,
    mode: "cors",
  });

  if (!response.ok) {
    throw new Error("Failed to fetch results");
  }

  return response.json();
};
