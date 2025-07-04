import Header from './components/Header.jsx';
import MovieList from './components/MovieList.jsx';
import RecommendedMovies from './components/RecommendedMovies.jsx';
import './styles/App.css';

function App() {
  return (
    <div className="app">
      <Header />
      <div className="main-wrapper">
        <main className="main-content">
          <RecommendedMovies />
          <MovieList />
        </main>
      </div>
    </div>
  );
}

export default App;
