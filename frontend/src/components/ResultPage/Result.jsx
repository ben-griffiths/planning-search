import React from "react";
import sic from "./sic.json";

const Result = ({ result }) => {
  const renderIndustryCodes = () => {
    if (result.related_industries && result.related_industries.length > 0) {
      return result.related_industries
        .filter((i) => i.code in sic)
        .map((industry) => (
          <div key={industry.code} className="lozenge">
            {sic[industry.code]}
          </div>
        ));
    }
    return null;
  };

  return (
    <div className="result">
      <div className="result-details">
        <h2>{result.reference_no}</h2>
        <p>{result.address}</p>
        <p>{result.validation_date}</p>
        <p>{result.proposal}</p>
      </div>
      <div className="result-industry">{renderIndustryCodes()}</div>
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
