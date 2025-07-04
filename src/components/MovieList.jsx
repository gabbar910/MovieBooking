import { useState, useEffect, useMemo } from 'react';
import movieData from '../data/movieData.json';
import SeatMap from './SeatMap';
import './MovieList.css';

export default function MovieList() {
  const [selectedMovie, setSelectedMovie] = useState(null);
  const [selectedTheatre, setSelectedTheatre] = useState(null);
  const [selectedTime, setSelectedTime] = useState(null);
  const [showSeatMap, setShowSeatMap] = useState(false);
  const [selectedDate, setSelectedDate] = useState(null);

  const today = new Date().toISOString().split('T')[0];

  useEffect(() => {
    setSelectedDate(today);
  }, [today]);

  const handleTimeSlotClick = (movie, theatre, time) => {
    setSelectedMovie(movie);
    setSelectedTheatre(theatre);
    setSelectedTime(time);
    setShowSeatMap(true);
  };

  const handleCloseSeatMap = () => {
    setShowSeatMap(false);
    setSelectedMovie(null);
    setSelectedTheatre(null);
    setSelectedTime(null);
  };

  const uniqueDates = useMemo(() => {
    const allDates = movieData.movies.flatMap((movie) => movie.showDates || []);
    return [...new Set(allDates)].sort();
  }, []);

  const filteredMovies = movieData.movies.filter((movie) =>
    selectedDate ? movie.showDates?.includes(selectedDate) : true,
  );

  const formatDateItem = (dateStr) => {
    const date = new Date(dateStr);
    const options = { weekday: 'short', month: 'short', day: 'numeric' };
    const formatted = new Intl.DateTimeFormat('en-US', options).formatToParts(
      date,
    );
    const parts = Object.fromEntries(formatted.map((p) => [p.type, p.value]));
    return {
      day: parts.weekday,
      date: parts.day,
      month: parts.month,
    };
  };

  return (
    <div className="movie-list">
      {/* Date Selector */}
      <div className="date-selector">
        <div className="date-list">
          {uniqueDates.map((date) => {
            const { day, date: dayNum, month } = formatDateItem(date);
            const isSelected = selectedDate === date;
            const isToday = date === today;
            return (
              <button
                key={date}
                className={`date-item ${isSelected ? 'selected' : ''} ${isToday ? 'today' : ''}`}
                onClick={() => setSelectedDate(date)}
              >
                <div className="day">{day}</div>
                <div className="date">{dayNum}</div>
                <div className="month">{month}</div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Movies List */}
      <div className="movies-container">
        {filteredMovies.length === 0 ? (
          <div className="no-shows">
            <p>No movies found for the selected date.</p>
          </div>
        ) : (
          filteredMovies.map((movie) => (
            <div
              key={movie.id}
              className={`movie-card ${movie.recommended ? 'recommended' : ''}`}
            >
              <div className="movie-header">
                <h3 className="movie-title">{movie.title}</h3>
                {movie.recommended && (
                  <span className="recommended-badge">Recommended</span>
                )}
              </div>
              <div className="movie-info">
                <div className="movie-meta">
                  <span className="movie-language">{movie.language}</span>
                  <span className="movie-format">{movie.format}</span>
                  <span className="movie-duration">{movie.duration}</span>
                </div>
                <div className="movie-genre">{movie.genre.join(' • ')}</div>
              </div>

              <div className="theatres-list">
                {movie.theatres.map((theatre) => (
                  <div key={theatre.id} className="theatre-item">
                    <div className="theatre-info">
                      <div className="theatre-name">{theatre.name}</div>
                      <div className="theatre-location">{theatre.location}</div>
                    </div>
                    <div className="show-timings">
                      {theatre.showTimings.map((time) => (
                        <button
                          key={time}
                          className="time-slot"
                          onClick={() =>
                            handleTimeSlotClick(movie, theatre, time)
                          }
                        >
                          {time}
                        </button>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))
        )}
      </div>

      {showSeatMap &&
        selectedMovie &&
        selectedTheatre &&
        selectedTime &&
        selectedDate && (
          <SeatMap
            movie={selectedMovie}
            theatre={selectedTheatre}
            showTime={selectedTime}
            showDate={selectedDate}
            onClose={handleCloseSeatMap}
          />
        )}
    </div>
  );
}
