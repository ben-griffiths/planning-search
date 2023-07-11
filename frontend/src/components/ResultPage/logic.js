import config from "../../config";

export const doOpensearchQuery = async (
  searchTerm,
  source,
  code,
  latlng,
  from,
  until
) => {
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

  if (from || until) {
    query.bool.must.push({
      range: {
        validation_date: { gte: from, lte: until, format: "YYYY-MM-DD" },
      },
    });
  }

  if (source) {
    query.bool.filter = {
      terms: { source: source.split(",") },
    };
  }

  if (latlng) {
    query.bool.filter = {
      ...query.bool.filter,
      geo_distance: {
        distance: "1km",
        location: latlng,
      },
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

export const geocodeAddress = async (address) => {
  const geocoder = new window.google.maps.Geocoder();
  const { results } = await geocoder.geocode({ address: address });
  const location = results[0].geometry.location;
  return `${location.lat()},${location.lng()}`;
};

export const isCoordinate = (coordinates) => {
  const latLngRegex = /^(-?\d+(\.\d+)?),\s*(-?\d+(\.\d+)?)$/;
  return latLngRegex.test(coordinates);
};
