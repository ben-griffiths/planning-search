import React, { useRef, useState } from "react";
import "./SearchBar.css";
import { useNavigate } from "react-router-dom";
import { useLocation } from "react-router-dom";
import sic from "../ResultPage/sic.json";

export const SearchBar = ({
  searchTerm,
  source,
  sourceOptions,
  code,
  codeOptions,
}) => {
  const ref = useRef();
  const navigate = useNavigate();
  const location = useLocation();
  const [selectedCodes, setSelectedCodes] = useState(code || []);

  const updateURLParameter = (key, value) => {
    const searchParams = new URLSearchParams(location.search);
    let path = location.pathname;

    if (!path.includes("/results")) {
      path += "/results";
    }

    if (key === "source" && searchParams.has(key)) {
      const existingValue = searchParams.get(key);
      const valueArray = existingValue.split(",");
      const index = valueArray.indexOf(value);

      if (index === -1) {
        valueArray.push(value);
      } else {
        valueArray.splice(index, 1);
      }

      searchParams.set(key, valueArray.join(","));
    } else {
      searchParams.set(key, value);
    }

    const newURL = `${path}?${searchParams.toString()}`;
    navigate(newURL);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    updateURLParameter("search", e.target[0].value);
  };

  const handleSourceFilterClick = (option) => {
    updateURLParameter("source", option.key);
  };

  const handleCodeFilterChange = (e) => {
    const selectedOptions = Array.from(
      e.target.selectedOptions,
      (option) => option.value
    );
    setSelectedCodes(selectedOptions);
    updateURLParameter("code", selectedOptions.join(","));
  };

  const handleCodeFilterOptionClick = (option) => {
    const selectedOptionIndex = selectedCodes.indexOf(option.key);
    if (selectedOptionIndex === -1) {
      const updatedSelectedCodes = [...selectedCodes, option.key];
      setSelectedCodes(updatedSelectedCodes);
      updateURLParameter("code", updatedSelectedCodes.join(","));
    } else {
      const updatedSelectedCodes = selectedCodes.filter(
        (key) => key !== option.key
      );
      setSelectedCodes(updatedSelectedCodes);
      updateURLParameter("code", updatedSelectedCodes.join(","));
    }
  };

  return (
    <div className="search-bar">
      <form onSubmit={handleSubmit}>
        <input
          ref={ref}
          type="text"
          placeholder="Search..."
          defaultValue={searchTerm}
        />
        <input type="submit" value="Search" />
      </form>
      {sourceOptions && (
        <div className="filter-wrapper">
          <span>Filter by Source:</span>
          {sourceOptions.map((option) => (
            <input
              key={option.key}
              type="button"
              value={`${option.key} (${option.count})`}
              className={
                source?.includes(option.key) ? "filter active" : "filter"
              }
              onClick={() => handleSourceFilterClick(option)}
            />
          ))}
        </div>
      )}
      {codeOptions && (
        <div className="filter-wrapper">
          <span>Filter by Code:</span>
          <select
            multiple
            value={selectedCodes}
            onChange={handleCodeFilterChange}
          >
            {codeOptions.map((option) => (
              <option key={option.key} value={option.key}>
                {sic[option.key]} ({option.count})
              </option>
            ))}
            {selectedCodes.map((code) => (
              <option key={code} value={code}>
                {sic[code]} (
                {codeOptions.find((option) => option.key === code)?.count})
              </option>
            ))}
          </select>
          {selectedCodes.length > 0 && (
            <div className="selected-options">
              {selectedCodes.map((code) => (
                <div
                  key={code}
                  className="selected-option"
                  onClick={() => handleCodeFilterOptionClick({ key: code })}
                >
                  {sic[code] || code}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
