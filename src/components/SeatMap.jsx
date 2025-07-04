import { useEffect, useState } from 'react';
import './SeatMap.css';
import seatAvailability from '../data/seatmap.json'; // adjust path as needed

export default function SeatMap({
  movie,
  theatre,
  showTime,
  showDate,
  onClose,
}) {
  const [selectedSeats, setSelectedSeats] = useState([]);
  const [occupiedSeats, setOccupiedSeats] = useState([]);

  const rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'];
  const seatsPerRow = 20;

  useEffect(() => {
    const showData = seatAvailability.seats.find(
      (entry) =>
        entry.movieId === movie.id &&
        entry.date === showDate &&
        entry.showTime === showTime,
    );

    setOccupiedSeats(showData?.occupiedSeats || []);
  }, [movie.id, showTime, showDate]);

  const handleSeatClick = (seatId) => {
    if (occupiedSeats.includes(seatId)) return;

    setSelectedSeats((prev) =>
      prev.includes(seatId)
        ? prev.filter((id) => id !== seatId)
        : [...prev, seatId],
    );
  };

  return (
    <div className="seat-map-overlay">
      <div className="seat-map-container">
        <div className="seat-map-header">
          <div className="movie-details">
            <h2>{movie.title}</h2>
            <p>
              {theatre.name} • {showTime}
            </p>
          </div>
          <button
            className="close-button"
            onClick={onClose}
            aria-label="Close seat map"
          >
            <svg
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                d="M18 6L6 18M6 6L18 18"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </button>
        </div>

        <div className="screen">Screen</div>

        <div className="seats-container">
          {rows.map((row) => (
            <div key={row} className="seat-row">
              <div className="row-label">{row}</div>
              {Array.from({ length: seatsPerRow }, (_, i) => {
                const seatNumber = i + 1;
                const seatId = `${row}${seatNumber}`;
                const isSelected = selectedSeats.includes(seatId);
                const isOccupied = occupiedSeats.includes(seatId);

                return (
                  <button
                    key={seatId}
                    className={`seat ${isSelected ? 'selected' : ''} ${isOccupied ? 'occupied' : ''}`}
                    onClick={() => handleSeatClick(seatId)}
                    aria-label={`Seat ${seatId}`}
                    aria-pressed={isSelected}
                    disabled={isOccupied}
                  >
                    {seatNumber}
                  </button>
                );
              })}
            </div>
          ))}
        </div>

        <div className="seat-map-footer">
          <div className="seat-info">
            <div className="seat-type">
              <div className="seat-example available"></div>
              <span>Available</span>
            </div>
            <div className="seat-type">
              <div className="seat-example selected"></div>
              <span>Selected</span>
            </div>
            <div className="seat-type">
              <div className="seat-example occupied"></div>
              <span>Occupied</span>
            </div>
          </div>

          <div className="booking-info">
            <div className="selected-seats">
              Selected Seats: {selectedSeats.join(', ') || 'None'}
            </div>
            <button
              className="book-button"
              disabled={selectedSeats.length === 0}
            >
              Book Tickets
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
