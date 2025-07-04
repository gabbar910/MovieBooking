import './Header.css';

export default function Header() {
  return (
    <header className="header">
      <div className="header-content">
        <a href="/" className="logo">
          MovieTime
        </a>

        <div className="search-box">
          <input
            type="search"
            placeholder="Search for movies..."
            className="search-input"
            aria-label="Search for movies"
          />
          <button className="search-button" aria-label="Search">
            <svg
              width="20"
              height="20"
              viewBox="0 0 20 20"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                d="M9 17C13.4183 17 17 13.4183 17 9C17 4.58172 13.4183 1 9 1C4.58172 1 1 4.58172 1 9C1 13.4183 4.58172 17 9 17Z"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
              <path
                d="M19 19L14.65 14.65"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </button>
        </div>

        <nav className="nav-links">
          <a href="/" className="nav-link">
            Movies
          </a>
          <a href="/cinemas" className="nav-link">
            Cinemas
          </a>
          <a href="/upcoming" className="nav-link">
            Upcoming
          </a>
        </nav>
      </div>
    </header>
  );
}
