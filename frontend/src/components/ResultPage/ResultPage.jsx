import React, { useState, useEffect } from "react";
import "./ResultPage.css";
import { useLocation } from "react-router-dom";
import SearchBar from "../SearchBar";
import { MapResult } from "./MapResult";
import config from "../../config";

export const ResultPage = () => {
  const [results, setResults] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [total, setTotal] = useState(0);

  const location = useLocation();
  const queryParams = new URLSearchParams(location.search);
  const searchTerm = queryParams.get("search");

  useEffect(() => {
    const fetchResults = async () => {
      try {
        const payload = JSON.stringify({
          query: {
            multi_match: {
              query: searchTerm,
              fields: ["address", "proposal"],
              lenient: true,
              zero_terms_query: "all",
            },
          },
          size: 100,
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

        const data = await response.json();

        setTotal(data.hits.total.value);
        setResults(data.hits.hits.map((r) => r._source));
        setIsLoading(false);
      } catch (error) {
        console.error("Error fetching results:", error);
      }
    };

    fetchResults();
  }, [searchTerm]);

  if (isLoading) {
    return <p>Loading...</p>;
  }

  return (
    <div className="result-page">
      <div className="search">
        <SearchBar searchTerm={searchTerm} />
      </div>
      <span>
        <h1>Search Results ({total})</h1>
      </span>
      {results.length > 0 ? (
        <>
          <MapResult results={results} />
          {results.map((result, index) => (
            <div key={index} className="result">
              <h2>{result.reference_no}</h2>
              <p>{result.address}</p>
              <p>{result.validation_date}</p>
              <p>{result.proposal}</p>
              <p>{result.location}</p>
            </div>
          ))}
        </>
      ) : (
        <div className="no-results">No results found for "{searchTerm}"</div>
      )}
    </div>
  );
};
