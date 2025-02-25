import React, { useState, useEffect } from "react";
import CategoryLabel from "./CategoryLabel";
import api from "../api";
import StatusLabel from "./StatusLabel";

const PromisePopup = ({ promise, candidateId, onClose }) => {
  if (!promise) return null;

  const [actions, setActions] = useState([]);
  const [expandedActions, setExpandedActions] = useState({}); // Track expanded citations per action
  const [citationsByAction, setCitationsByAction] = useState({}); // Store citations per action
  const [citations, setCitations] = useState([]);
  const [currentCitationIndex, setCurrentCitationIndex] = useState(0);
  const [isHovered, setIsHovered] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const actionsResponse = await api.get(
          `/api/v1/candidates/${candidateId}/promises/${promise.id}/actions`
        );
        const citationsResponse = await api.get(
          `/api/v1/candidates/${candidateId}/promises/${promise.id}/citations`
        );

        setActions(actionsResponse.data.data);
        setCitations(citationsResponse.data.data);
      } catch (error) {
        console.error("Error fetching actions:", error);
      }
    };

    fetchData();
  }, [candidateId, promise.id]);

  const formatDate = (isoString) => {
    const date = new Date(isoString);
    return date.toLocaleDateString("en-US", {
      month: "long",
      day: "numeric",
      year: "numeric",
    });
  };

  const nextCitation = () => {
    setCurrentCitationIndex((prevIndex) => (prevIndex + 1) % citations.length);
  };

  const prevCitation = () => {
    setCurrentCitationIndex((prevIndex) =>
      prevIndex === 0 ? citations.length - 1 : prevIndex - 1
    );
  };

  const toggleActionCitations = async (actionId) => {
    setExpandedActions((prevState) => ({
      ...prevState,
      [actionId]: !prevState[actionId],
    }));

    if (!citationsByAction[actionId]) {
      try {
        const response = await api.get(
          `/api/v1/candidates/${candidateId}/actions/${actionId}/citations/`
        );
        setCitationsByAction((prevCitations) => ({
          ...prevCitations,
          [actionId]: response.data.data,
        }));
      } catch (error) {
        console.error(
          `Error fetching citations for action ${actionId}:`,
          error
        );
      }
    }
  };

  return (
    <div style={styles.overlay}>
      <div style={styles[getStatusLabel(promise.status)]}>
        <button style={styles.closeButton} onClick={onClose}>
          &times;
        </button>
        <h2 style={styles.title}>{promise.text}</h2>

        {/* Status Section */}
        <div style={styles.statusContainer}>
          <span style={styles.statusLabel}>Status:</span>
          <StatusLabel status={getStatusLabel(promise.status)} />
        </div>

        {/* Actions Taken (Scrollable) */}
        <div style={styles.section}>
          <strong>Progress Updates:</strong>
          <div style={styles.actionContainer}>
            <ul style={styles.actionList}>
              {actions.length > 0 ? (
                actions.map((action) => (
                  <li key={action.id} style={styles.actionItem}>
                    {formatDate(action.date)}: {action.text}
                    <div
                      style={styles.toggleButton}
                      onClick={() => toggleActionCitations(action.id)}
                    >
                      {expandedActions[action.id]
                        ? "Hide Sources"
                        : "View Sources"}
                    </div>
                    {expandedActions[action.id] && (
                      <ul style={styles.citationList}>
                        {citationsByAction[action.id]?.length > 0 ? (
                          citationsByAction[action.id].map((citation) => (
                            <li key={citation.url} style={styles.citationItem}>
                              <a
                                href={citation.url}
                                target="_blank"
                                rel="noopener noreferrer"
                              >
                                {`"${citation.extract}"`}
                              </a>
                            </li>
                          ))
                        ) : (
                          <li style={styles.noCitation}>
                            No sources available
                          </li>
                        )}
                      </ul>
                    )}
                  </li>
                ))
              ) : (
                <li>No recorded actions</li>
              )}
            </ul>
          </div>
        </div>

        {/* Category */}
        <div style={styles.statusContainer}>
          <span style={styles.statusLabel}>Categories:</span>
          <CategoryLabel category="Economy" />
        </div>
        {/* Related Articles (Swipeable) */}
        {citations.length > 0 && (
          <div style={styles.section}>
            <strong>Related Articles:</strong>
            <div style={styles.articleSwipeContainer}>
              <button
                style={styles.navButton}
                onClick={prevCitation}
                disabled={citations.length <= 1}
              >
                ◀
              </button>
              <div
                style={{
                  ...styles.articleCard,
                }}
              >
                <a
                  href={citations[currentCitationIndex].url}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  {`"${citations[currentCitationIndex].extract}"`}
                </a>
              </div>
              <button
                style={styles.navButton}
                onClick={nextCitation}
                disabled={citations.length <= 1}
              >
                ▶
              </button>
            </div>
            <div style={styles.citationIndex}>
              {`${currentCitationIndex + 1} / ${citations.length}`}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

// Helper function to map status values to labels
const getStatusLabel = (status) => {
  const statusMap = {
    0: "Progressing",
    1: "Compromised",
    2: "Delivered",
    3: "Broken",
  };
  return statusMap[status] || "Unknown";
};
const styles = {
  overlay: {
    position: "fixed",
    top: 0,
    left: 0,
    width: "100%",
    height: "100%",
    backgroundColor: "rgba(0,0,0,0.5)",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    zIndex: 1000,
  },
  Progressing: {
    backgroundColor: "#fff",
    padding: "20px",
    borderRadius: "12px",
    boxShadow: "0 4px 8px rgba(0,0,0,0.2)",
    width: "420px",
    maxWidth: "90%",
    border: "3px solid #99C3FF",
    position: "relative",
  },
  closeButton: {
    position: "absolute",
    top: "10px",
    right: "10px",
    background: "none",
    border: "none",
    fontSize: "20px",
    cursor: "pointer",
  },
  title: {
    fontSize: "20px",
    fontWeight: "bold",
    textAlign: "center",
    marginBottom: "15px",
    textDecoration: "underline",
  },
  statusContainer: {
    display: "flex",
    alignItems: "center",
    gap: "10px",
    marginBottom: "10px",
  },
  statusLabel: {
    fontWeight: "bold",
  },
  section: {
    marginBottom: "15px",
  },
  actionContainer: {
    maxHeight: "120px",
    overflowY: "auto",
    border: "1px solid #ddd",
    borderRadius: "6px",
    padding: "10px",
    backgroundColor: "#f9f9f9",
  },
  actionList: {
    paddingLeft: "15px",
    fontSize: "14px",
    margin: 0,
  },
  actionItem: {
    marginBottom: "8px",
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
    height: "80px",
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
    justifyContent: "center",
    textAlign: "center",
    marginTop: "5px",
  },
  toggleButton: {
    display: "block",
    backgroundColor: "#f9f9f9",
    border: "none",
    borderRadius: "5px",
    fontSize: "14px",
    textDecoration: "underline",
    marginTop: "2px",
    fontWeight: "bold",
  },
  citationList: {
    marginTop: "5px",
    paddingLeft: "20px",
    fontSize: "12px",
  },
  citationItem: {
    marginBottom: "4px",
  },
  citationLink: {
    color: "black",
    textDecoration: "none",
  },
  noCitation: {
    fontSize: "12px",
    fontStyle: "italic",
    color: "gray",
  },
};
export default PromisePopup;
