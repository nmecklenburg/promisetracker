import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import './PromiseCard.css';

const PromiseCard = () => {
  const { candidateId } = useParams(); // Get candidateId from the URL
  const [candidate, setCandidate] = useState(null); // Store candidate details
  const [promises, setPromises] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchCandidateData = async () => {
      try {
        // Fetch candidate details
        const candidateResponse = await axios.get(
          `http://localhost:8000/api/v1/candidates/${candidateId}`
        );
        setCandidate(candidateResponse.data);

        // Fetch promises for the candidate
        const promisesResponse = await axios.get(
          `http://localhost:8000/api/v1/candidates/${candidateId}/promises`,
          {
            params: {
              after: 0,
              limit: 4
            },
          }
        );
        setPromises(promisesResponse.data.data);
        setLoading(false);
      } catch (err) {
        console.error('Error fetching data:', err);
        setError('Failed to fetch data');
        setLoading(false);
      }
    };

    fetchCandidateData();
  }, [candidateId]); // Fetch data whenever candidateId changes

  // Determine status text and colors
  const getStatusDetails = (status) => {
    switch (status) {
      case 0:
        return { text: 'Progressing', color: 'blue' };
      case 1:
        return { text: 'Complete', color: 'green' };
      case 2:
        return { text: 'Broken', color: 'red' };
      case 3:
        return { text: 'Compromised', color: 'yellow' };
      default:
        return { text: 'Unknown', color: 'gray' };
    }
  };

  if (loading) return <p>Loading...</p>;
  if (error) return <p>{error}</p>;

  return (
    <div className="promise-card">
      <h1>Top Promises for {candidate?.name}</h1>
      {promises.map((promise) => {
        const { text: statusText, color: statusColor } = getStatusDetails(promise.status);

        return (
          <div
            key={promise.id}
            className="card"
            style={{ borderColor: statusColor }}
          >
            <p className="description">{promise.text}</p>
            <div className="status">
              <strong>Status:</strong>{' '}
              <span
                className="status-badge"
                style={{ backgroundColor: statusColor }}
              >
                {statusText}
              </span>
            </div>
            <div className="category">
              <strong>Category:</strong> <span className="category-economy">Economy</span>
            </div>
            <div className="related-articles">
              <strong>Related Articles:</strong>
              <div className="articles">
                {/* Placeholder for related articles */}
                <div className="article">
                  <div className="article-thumbnail"></div>
                  <p>"Article Title"</p>
                </div>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default PromiseCard;
