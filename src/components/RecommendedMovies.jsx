import { useRef } from 'react';
import movieData from '../data/movieData.json';
import './RecommendedMovies.css';

export default function RecommendedMovies() {
  const carouselRef = useRef(null);
  const recommendedMovies = movieData.movies.filter(
    (movie) => movie.recommended,
  );

  const scroll = (direction) => {
    const container = carouselRef.current;
    const scrollAmount = direction === 'left' ? -300 : 300;
    container.scrollBy({ left: scrollAmount, behavior: 'smooth' });
  };

  return (
    <div className="recommended-movies">
      <h2 className="section-title">Recommended Movies</h2>
      <div className="carousel">
        <button
          className="carousel-arrow left"
          onClick={() => scroll('left')}
          aria-label="Scroll left"
        >
          <svg
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M15 19L8 12L15 5"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </button>

        <div className="carousel-track" ref={carouselRef}>
          {recommendedMovies.map((movie) => (
            <div key={movie.id} className="carousel-item">
              <div className="movie-card">
                <div className="movie-info">
                  <h3 className="movie-title">{movie.title}</h3>
                  <div className="movie-meta">
                    <span className="movie-language">{movie.language}</span>
                    <div className="movie-genre">{movie.genre.join(' • ')}</div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        <button
          className="carousel-arrow right"
          onClick={() => scroll('right')}
          aria-label="Scroll right"
        >
          <svg
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M9 5L16 12L9 19"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </button>
      </div>
    </div>
  );
}
