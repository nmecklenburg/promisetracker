import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import './App.css';
import PromiseCard from './PromiseCard';

const Home = () => {
  return (
    <div>
      <h1>Home Page</h1>
      <Link to="/promise-card">
        <button>View Promise Card</button>
      </Link>
    </div>
  );
};

const App = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/promise-card" element={<PromiseCard />} />
      </Routes>
    </Router>
  );
};

export default App;
