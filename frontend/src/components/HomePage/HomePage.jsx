import "./HomePage.css";
import SearchBar from "../SearchBar";

export const Homepage = () => {
  return (
    <div className="homepage">
      <header className="header">
        <h1>Planning Application Search</h1>
        <p>Find and track planning applications in your area</p>
      </header>
      <div className="main">
        <SearchBar />
      </div>
      <footer className="footer">
        <p>&copy; {new Date().getFullYear()} Planning Application Search</p>
      </footer>
    </div>
  );
};
