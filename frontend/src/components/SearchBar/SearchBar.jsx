import React, { useRef, useState } from "react";
import "./SearchBar.css";
import { useNavigate } from "react-router-dom";
import { useLocation } from "react-router-dom";

export const SearchBar = ({
  searchTerm,
  source,
  sourceOptions,
  location,
  from,
  until,
}) => {
  const ref = useRef();
  const navigate = useNavigate();
  const navLocation = useLocation();
  const [locationLoading, setLocationLoading] = useState(false);

  const updateURLParameter = (params) => {
    const searchParams = new URLSearchParams(navLocation.search);
    let path = navLocation.pathname;

    if (!path.includes("/results")) {
      path += "/results";
    }

    for (const p of params) {
      const [key, value] = p;
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
    }

    const newURL = `${path}?${searchParams.toString()}`;
    navigate(newURL);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    updateURLParameter([
      ["search", e.target[0].value],
      ["location", e.target[2].value],
      ["from", e.target[4].value],
      ["until", e.target[5].value],
    ]);
  };

  const handleSourceFilterClick = (option) => {
    updateURLParameter([["source", option.key]]);
  };

  return (
    <div className="search-bar">
      <form onSubmit={handleSubmit}>
        <span className="filter-wrapper">
          <input
            type="text"
            placeholder="Search..."
            defaultValue={searchTerm}
          />
          <input type="submit" value="Search" />
        </span>
        <span className="filter-wrapper">
          <label for="location">Location</label>
          <input
            ref={ref}
            id="location"
            type="text"
            placeholder="Enter location"
            defaultValue={location}
          />
          <button
            id="my-location"
            disabled={locationLoading}
            onClick={async (e) => {
              e.preventDefault();
              setLocationLoading(true);
              const response = await new Promise((resolve) =>
                navigator.geolocation.getCurrentPosition(resolve)
              );
              const latlng = `${response.coords.latitude},${response.coords.longitude}`;
              ref.current.value = latlng;
              updateURLParameter([("location", latlng)]);
              setLocationLoading(false);
            }}
          >
            {locationLoading ? (
              "Loading"
            ) : (
              <span className="material-symbols-outlined">my_location</span>
            )}
          </button>
        </span>
        <span className="filter-wrapper">
          <label for="from">From</label>
          <input id="from" type="datetime-local" defaultValue={from} />
          <label for="until">Until</label>
          <input id="until" type="datetime-local" defaultValue={until} />
        </span>
        {sourceOptions && (
          <div className="filter-wrapper">
            <span>Source:</span>
            {sourceOptions.map((option) => (
              <button
                className={
                  source?.includes(option.key) ? "filter active" : "filter"
                }
                onClick={() => handleSourceFilterClick(option)}
              >
                {`${option.key} (${option.count})`}
              </button>
            ))}
          </div>
        )}
      </form>
    </div>
  );
};
