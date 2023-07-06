import config from "../../config";

export const doOpensearchQuery = async (searchTerm, source, code) => {
  const query = {
    bool: {
      must: [
        {
          multi_match: {
            query: searchTerm || "",
            fields: ["reference_no", "address", "proposal", "source"],
            lenient: true,
            zero_terms_query: "all",
          },
        },
      ],
    },
  };

  if (code) {
    query.bool.must.push({
      nested: {
        path: "related_industries",
        query: {
          terms: {
            "related_industries.code": code.split(","),
          },
        },
      },
    });
  }

  if (source) {
    query.bool.filter = {
      terms: { source: source.split(",") },
    };
  }

  const payload = JSON.stringify({
    query,
    size: 100,
    track_total_hits: true,
    sort: [
      {
        _score: {
          order: "desc",
        },
      },
      {
        "related_industries.relation_score": {
          order: "desc",
        },
      },
    ],
    aggs: {
      source_options: {
        terms: {
          field: "source",
          size: 100,
          min_doc_count: 0,
        },
      },
      nested_related_industries: {
        nested: {
          path: "related_industries",
        },
        aggs: {
          code_terms: {
            terms: {
              field: "related_industries.code",
              size: 1000,
            },
          },
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
