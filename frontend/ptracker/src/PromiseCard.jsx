import React, { useEffect, useState } from 'react';
import axios from 'axios';
import './PromiseCard.css';

const PromiseCard = () => {
  const [promises, setPromises] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchPromises = async () => {
      try {
        const response = await axios.get(
          'http://localhost:8000/api/v1/candidates/3/promises',
          {
            params: {
              after: 1,
              limit: 2, // Adjust based on your needs
            },
          }
        );
        setPromises(response.data.data);
        setLoading(false);
      } catch (err) {
        console.error('Error fetching promises:', err);
        setError('Failed to fetch promises');
        setLoading(false);
      }
    };

    fetchPromises();
  }, []);

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
      <h1>Top Promises</h1>
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
