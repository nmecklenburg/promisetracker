import React, { useEffect, useState } from "react";
import axios from "axios";
import "./PromiseCard.css";
import StatusLabel from "./HomePage/StatusLabel";
import CategoryLabel from "./HomePage/CategoryLabel";

const PromiseCard = ({ candidateId }) => {
  const [promises, setPromises] = useState([]);
  const [error, setError] = useState(null);
  const [citationsByPromise, setCitationsByPromise] = useState({});
  const [currentCitationIndex, setCurrentCitationIndex] = useState({});
  const [promiseCounts, setPromiseCounts] = useState({
    progressing: 0,
    completed: 0,
    broken: 0,
    compromised: 0,
  });

  useEffect(() => {
    const fetchCandidateData = async () => {
      try {
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
              counts.compromised++;
              break;
            case 2:
              counts.completed++;
              break;
            case 3:
              counts.broken++;
              break;
            default:
              break;
          }
        });

        setPromises(fetchedPromises);
        setPromiseCounts(counts);

        const citationsPromises = fetchedPromises.map(async (promise) => {
          const response = await axios.get(
            `http://localhost:8000/api/v1/candidates/${candidateId}/promises/${promise.id}/citations`
          );
          return { promiseId: promise.id, citations: response.data.data };
        });

        const citationsData = await Promise.all(citationsPromises);
        const citationsMap = {};
        const citationIndices = {};

        citationsData.forEach(({ promiseId, citations }) => {
          citationsMap[promiseId] = citations;
          citationIndices[promiseId] = 0;
        });

        setCitationsByPromise(citationsMap);
        setCurrentCitationIndex(citationIndices);
      } catch (err) {
        console.error("Error fetching data:", err);
        setError("Failed to fetch data");
      }
    };

    fetchCandidateData();
  }, [candidateId]); // Fetch data whenever candidateId changes

  const handleNextCitation = (promiseId) => {
    setCurrentCitationIndex((prev) => ({
      ...prev,
      [promiseId]:
        (prev[promiseId] + 1) % (citationsByPromise[promiseId]?.length || 1),
    }));
  };

  const handlePrevCitation = (promiseId) => {
    setCurrentCitationIndex((prev) => ({
      ...prev,
      [promiseId]:
        prev[promiseId] === 0
          ? (citationsByPromise[promiseId]?.length || 1) - 1
          : prev[promiseId] - 1,
    }));
  };

  // Calculate progress percentage
  const totalPromises =
    promiseCounts.progressing +
    promiseCounts.completed +
    promiseCounts.broken +
    promiseCounts.compromised;
  const progressPercentage = totalPromises
    ? Math.round((promiseCounts.completed / totalPromises) * 100)
    : 0;

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

      <h1 style={styles.topPromisesTitle}>Top Promises to Watch</h1>
      <div style={styles.promiseGrid}>
        {promises.slice(0, 4).map((promise) => {
          const { text: statusText, color: statusColor } = getStatusDetails(
            promise.status
          );
          const citations = citationsByPromise[promise.id] || [];
          const currentCitation =
            citations[currentCitationIndex[promise.id]] || {};

          return (
            <div
              key={promise.id}
              style={{
                ...styles.card,
                border: `4px solid ${statusColor}`, // Explicitly set the border width, style, and color
              }}
            >
              <p style={styles.description}>{promise.text}</p>
              <div style={styles.status}>
                <strong>Status:</strong> <StatusLabel status={statusText} />
              </div>
              <div style={styles.category}>
                <strong>Category:</strong>{" "}
                <CategoryLabel category={"Economy"} />
              </div>

              {/* Related Articles with Navigation */}
              {citations.length > 0 && (
                <div style={styles.relatedArticlesSection}>
                  <strong>Related Articles:</strong>
                  <div style={styles.articleSwipeContainer}>
                    <button
                      style={styles.navButton}
                      onClick={() => handlePrevCitation(promise.id)}
                    >
                      ◀
                    </button>
                    <div style={styles.articleCard}>
                      <a
                        href={currentCitation.url}
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        {`"${currentCitation.extract}"` || "Read more"}
                      </a>
                    </div>
                    <button
                      style={styles.navButton}
                      onClick={() => handleNextCitation(promise.id)}
                    >
                      ▶
                    </button>
                  </div>
                  <div style={styles.citationIndex}>
                    {`${currentCitationIndex[promise.id] + 1} / ${
                      citations.length
                    }`}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );

  function getStatusDetails(status) {
    switch (status) {
      case 0:
        return { text: "Progressing", color: "#99C3FF" };
      case 1:
        return { text: "Delivered", color: "#59E000" };
      case 2:
        return { text: "Broken", color: "#DF0404" };
      case 3:
        return { text: "Compromised", color: "#AB9629" };
      default:
        return { text: "Unknown", color: "gray" };
    }
  }
};

const styles = {
  topPromisesTitle: {
    marginTop: "60px"
  },
  promiseGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(2, 1fr)",
    gap: "40px",
    marginTop: "20px",
    marginLeft: "100px",
    marginRight: "100px",
  },
  card: {
    padding: "15px",
    borderRadius: "20px",
    backgroundColor: "white",
    boxShadow: "0px 4px 6px rgba(0, 0, 0, 0.1)",
    transition: "transform 0.2s ease-in-out",
  },
  description: {
    fontSize: "16px",
    fontWeight: "bold",
    marginBottom: "20px",
  },
  status: {
    marginBottom: "20px",
  },
  category: {
    marginBottom: "20px",
  },
  relatedArticlesSection: {
    marginTop: "20px",
  },
  articleSwipeContainer: {
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    gap: "10px",
    marginTop: "10px",
  },
  articleCard: {
    width: "250px",
    height: "70px",
    backgroundColor: "#ddd",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    fontSize: "12px",
    borderRadius: "8px",
    padding: "10px",
    cursor: "pointer",
    textAlign: "center",
    transition: "color 0.3s ease",
  },
  navButton: {
    background: "none",
    border: "none",
    fontSize: "20px",
    cursor: "pointer",
  },
  citationIndex: {
    textAlign: "center",
    marginTop: "10px",
  },
};

export default PromiseCard;
