import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import './App.css';
import PromiseCard from './PromiseCard';
import PoliticiansPage from './PoliticiansPage';

const Home = () => {
  return (
    <div>
      <h1>Home Page</h1>
      <Link to="/politicians">
        <button>Go to Politicians Page</button>
      </Link>
    </div>
  );
};

const App = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/politicians" element={<PoliticiansPage />} />
        <Route path="/promise-card/:candidateId" element={<PromiseCard />} />
      </Routes>
    </Router>
  );
};

export default App;
