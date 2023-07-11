import React from "react";

const Result = ({ result }) => {
  return (
    <div className="result">
      <div className="result-details">
        <h2>{result.reference_no}</h2>
        <p>{result.address}</p>
        <p>{result.validation_date}</p>
        <p>{result.proposal}</p>
      </div>
      <div className="result-source">
        <p>Source: {result.source}</p>
      </div>
      {result.detail_url && (
        <div className="result-link">
          <a href={result.detail_url}>View Details</a>
        </div>
      )}
    </div>
  );
};

export default Result;
