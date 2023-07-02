import React, { useRef } from "react";
import "./SearchBar.css";
import { useNavigate } from "react-router-dom";
import { useLocation } from "react-router-dom";

export const SearchBar = ({ searchTerm, source, sourceOptions }) => {
  const ref = useRef();
  const navigate = useNavigate();
  const location = useLocation();

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

  const handleFilterClick = (option) => {
    updateURLParameter("source", option.key);
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
              onClick={() => handleFilterClick(option)}
            />
          ))}
        </div>
      )}
    </div>
  );
};
