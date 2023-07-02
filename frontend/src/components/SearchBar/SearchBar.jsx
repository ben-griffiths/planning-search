import React, { useRef } from "react";
import "./SearchBar.css";
import { useNavigate } from "react-router-dom";

export const SearchBar = ({ searchTerm }) => {
  const ref = useRef();
  const navigate = useNavigate();

  const handleSubmit = (e) => {
    e.preventDefault();
    navigate(`/results?search=${e.target[0].value}`);
  };

  return (
    <form className="search-bar" onSubmit={handleSubmit}>
      <input
        ref={ref}
        type="text"
        placeholder="Search..."
        defaultValue={searchTerm}
      />
      <button type="submit">Search</button>
    </form>
  );
};
