import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';

const PoliticiansPage = () => {
  const [candidates, setCandidates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchCandidates = async () => {
      try {
        const response = await axios.get('http://localhost:8000/api/v1/candidates', {
          params: {
            after: 0,
            limit: 10, // Adjust the limit as needed
          },
        });
        setCandidates(response.data.data);
        setLoading(false);
      } catch (err) {
        console.error('Error fetching candidates:', err);
        setError('Failed to fetch candidates');
        setLoading(false);
      }
    };

    fetchCandidates();
  }, []);

  if (loading) return <p>Loading...</p>;
  if (error) return <p>{error}</p>;

  return (
    <div>
      <h1>Politicians Page</h1>
      <table border="1" style={{ width: '80%', margin: 'auto', textAlign: 'left' }}>
        <thead>
          <tr>
            <th>Name</th>
            <th>Description</th>
            <th>Number of Promises</th>
            <th>View Promises</th>
          </tr>
        </thead>
        <tbody>
          {candidates.map((candidate) => (
            <tr key={candidate.id}>
              <td>{candidate.name}</td>
              <td>{candidate.description}</td>
              <td>{candidate.promises}</td>
              <td>
                <Link to={`/promise-card/${candidate.id}`}>
                  <button>View Promises</button>
                </Link>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default PoliticiansPage;