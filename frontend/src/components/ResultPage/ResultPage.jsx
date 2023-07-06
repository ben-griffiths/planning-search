import React, { useState, useEffect } from "react";
import "./ResultPage.css";
import { useLocation } from "react-router-dom";
import SearchBar from "../SearchBar";
import { MapResult } from "./MapResult";
import Result from "./Result";
import { doOpensearchQuery } from "./logic";

export const ResultPage = () => {
  const [results, setResults] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [total, setTotal] = useState(0);
  const [sourceOptions, setSourceOptions] = useState([]);
  const [codeOptions, setCodeOptions] = useState([]);

  const location = useLocation();
  const queryParams = new URLSearchParams(location.search);
  const searchTerm = queryParams.get("search");
  const source = queryParams.get("source");
  const code = queryParams.get("code");

  useEffect(() => {
    const fetchResults = async () => {
      try {
        setIsLoading(true);
        const data = await doOpensearchQuery(searchTerm, source, code);

        setTotal(data.hits.total.value);
        setResults(data.hits.hits.map((r) => r._source));
        setSourceOptions(
          data.aggregations.source_options.buckets.map((bucket) => ({
            key: bucket.key,
            count: bucket.doc_count,
          }))
        );
        setCodeOptions(
          data.aggregations.nested_related_industries.code_terms.buckets.map(
            (bucket) => ({
              key: bucket.key,
              count: bucket.doc_count,
            })
          )
        );
        setIsLoading(false);
      } catch (error) {
        console.error("Error fetching results:", error);
      }
    };

    fetchResults();
  }, [searchTerm, source, code]);

  return (
    <div className="result-page">
      <div className="search">
        <SearchBar
          searchTerm={searchTerm}
          source={source}
          sourceOptions={sourceOptions}
          code={code}
          codeOptions={codeOptions}
        />
      </div>
      <h1>Search Results ({total})</h1>
      <p className="results-note">Displaying up to 100 results</p>
      <MapResult results={results} />
      {isLoading ? (
        <div className="loading">
          <div className="spinner"></div>
          <p>Loading...</p>
        </div>
      ) : results.length > 0 ? (
        results.map((result, index) => <Result key={index} result={result} />)
      ) : (
        <div className="no-results">No results found for "{searchTerm}"</div>
      )}
    </div>
  );
};
