import React from "react";
import { Routes, Route, BrowserRouter } from "react-router-dom";
import ResultPage from "./components/ResultPage";
import HomePage from "./components/HomePage";

const App = () => {
  return (
    <BrowserRouter basename="/planning-search">
      <Routes>
        <Route path="/results" element={<ResultPage />} />
        <Route path="/" element={<HomePage />} />
      </Routes>
    </BrowserRouter>
  );
};

export default App;
