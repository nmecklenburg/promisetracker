import React, { useEffect, useState } from "react";
import axios from "axios";
import "./PromiseCard.css";
import StatusLabel from "./HomePage/StatusLabel";
import CategoryLabel from "./HomePage/CategoryLabel";

const PromiseCard = ({ candidateId }) => {
  const [candidate, setCandidate] = useState(null); // Store candidate details
  const [promises, setPromises] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [promiseCounts, setPromiseCounts] = useState({
    progressing: 0,
    completed: 0,
    broken: 0,
    compromised: 0,
  });

  useEffect(() => {
    const fetchCandidateData = async () => {
      try {
        // Fetch candidate details
        const candidateResponse = await axios.get(
          `http://localhost:8000/api/v1/candidates/${candidateId}`
        );
        setCandidate(candidateResponse.data);

        // Fetch all promises for the candidate
        const promisesResponse = await axios.get(
          `http://localhost:8000/api/v1/candidates/${candidateId}/promises`,
          {
            params: {
              after: 0,
              limit: 1000, // Fetch all promises
            },
          }
        );
        const fetchedPromises = promisesResponse.data.data;

        // Count promises by status
        const counts = {
          progressing: 0,
          completed: 0,
          broken: 0,
          compromised: 0,
        };
        fetchedPromises.forEach((promise) => {
          switch (promise.status) {
            case 0:
              counts.progressing++;
              break;
            case 1:
              counts.completed++;
              break;
            case 2:
              counts.broken++;
              break;
            case 3:
              counts.compromised++;
              break;
            default:
              break;
          }
        });

        setPromises(fetchedPromises);
        setPromiseCounts(counts);
        setLoading(false);
      } catch (err) {
        console.error("Error fetching data:", err);
        setError("Failed to fetch data");
        setLoading(false);
      }
    };

    fetchCandidateData();
  }, [candidateId]); // Fetch data whenever candidateId changes

  // Calculate progress percentage
  const totalPromises =
    promiseCounts.progressing +
    promiseCounts.completed +
    promiseCounts.broken +
    promiseCounts.compromised;
  const progressPercentage = totalPromises
    ? Math.round((promiseCounts.completed / totalPromises) * 100)
    : 0;

  if (loading) return <p>Loading...</p>;
  if (error) return <p>{error}</p>;

  return (
    <div className="promise-card">
      {/* Progress Bar */}
      <div className="progress-bar-container">
        <div
          className="progress-bar"
          style={{ width: `${progressPercentage}%` }}
        >
          {progressPercentage}%
        </div>
      </div>
      <p className="progress-text">
        {promiseCounts.completed} / {totalPromises} promises completed
      </p>

      {/* Visualization */}
      <div className="promise-visualization">
        <div
          className="visualization-card"
          style={{ backgroundColor: "#a2f3b6" }}
        >
          <h2>{promiseCounts.completed}</h2>
          <p>
            promises <strong>completed</strong>
          </p>
        </div>
        <div
          className="visualization-card"
          style={{ backgroundColor: "#add8e6" }}
        >
          <h2>{promiseCounts.progressing}</h2>
          <p>
            promises <strong>progressing</strong>
          </p>
        </div>
        <div
          className="visualization-card"
          style={{ backgroundColor: "#fff6a5" }}
        >
          <h2>{promiseCounts.compromised}</h2>
          <p>
            promises <strong>compromised</strong>
          </p>
        </div>
        <div
          className="visualization-card"
          style={{ backgroundColor: "#f8b6b6" }}
        >
          <h2>{promiseCounts.broken}</h2>
          <p>
            promises <strong>broken</strong>
          </p>
        </div>
      </div>

      <h1>Top Promises to Watch</h1>
      {/* List of Promises - Display only the first 4 */}
      {promises.slice(0, 4).map((promise) => {
        const { text: statusText, color: statusColor } = getStatusDetails(
          promise.status
        );

        return (
          <div
            key={promise.id}
            className="card"
            style={{ borderColor: statusColor }}
          >
            <p className="description">{promise.text}</p>
            <div className="status">
              <strong>Status:</strong> <StatusLabel status={statusText} />
            </div>
            <div className="category">
              <strong>Category:</strong>{" "}
              <CategoryLabel key={"Economy"} category={"Economy"} />
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

  function getStatusDetails(status) {
    switch (status) {
      case 0:
        return { text: "Progressing", color: "blue" };
      case 1:
        return { text: "Complete", color: "green" };
      case 2:
        return { text: "Broken", color: "red" };
      case 3:
        return { text: "Compromised", color: "yellow" };
      default:
        return { text: "Unknown", color: "gray" };
    }
  }
};

export default PromiseCard;
