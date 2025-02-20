import React, { useState, useEffect } from "react";
import CategoryLabel from "./CategoryLabel";
import api from "../api";
import StatusLabel from "./StatusLabel";

const PromisePopup = ({ promise, candidateId, onClose }) => {
  if (!promise) return null;

  const [actions, setActions] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await api.get(
          `/api/v1/candidates/${candidateId}/promises/${promise.id}/actions`
        );
        setActions(response.data.data);
      } catch (error) {
        console.error("Error fetching data:", error);
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
          <strong>Actions Taken:</strong>
          <div style={styles.actionContainer}>
            <ul style={styles.actionList}>
              {actions.length > 0 ? (
                actions.map((action) => (
                  <li key={action.id}>
                    {formatDate(action.date)}: {action.text}
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

        {/* Related Articles */}
        <div style={styles.section}>
          <strong>Related Articles:</strong>
          <div style={styles.articleContainer}>
            <div style={styles.articleCard}>{"Article Title"}</div>
          </div>
        </div>
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
  Compromised: {
    backgroundColor: "#fff",
    padding: "20px",
    borderRadius: "12px",
    boxShadow: "0 4px 8px rgba(0,0,0,0.2)",
    width: "420px",
    maxWidth: "90%",
    border: "3px solid #FFF0A2",
    position: "relative",
  },
  Delivered: {
    backgroundColor: "#fff",
    padding: "20px",
    borderRadius: "12px",
    boxShadow: "0 4px 8px rgba(0,0,0,0.2)",
    width: "420px",
    maxWidth: "90%",
    border: "3px solid #7ED957",
    position: "relative",
  },
  Broken: {
    backgroundColor: "#fff",
    padding: "20px",
    borderRadius: "12px",
    boxShadow: "0 4px 8px rgba(0,0,0,0.2)",
    width: "420px",
    maxWidth: "90%",
    border: "3px solid #DF0404",
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
  statusBadge: {
    padding: "6px 12px",
    borderRadius: "8px",
    backgroundColor: "#C8F7C5",
    fontSize: "14px",
  },
  section: {
    marginBottom: "15px",
  },
  actionContainer: {
    maxHeight: "120px", // Show only first 5 actions (approximate height)
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
  articleContainer: {
    display: "flex",
    gap: "10px",
    justifyContent: "center",
  },
  articleCard: {
    width: "120px",
    height: "80px",
    backgroundColor: "#ddd",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    fontSize: "12px",
    borderRadius: "8px",
  },
};

export default PromisePopup;
