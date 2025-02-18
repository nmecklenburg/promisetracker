import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import axios from "axios";

const PoliticiansPage = () => {
  const [candidates, setCandidates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchCandidates = async () => {
      try {
        const response = await axios.get("http://localhost:8000/api/v1/candidates", {
          params: { after: 0, limit: 10 },
        });
        setCandidates(response.data.data);
        setLoading(false);
      } catch (err) {
        console.error("Error fetching candidates:", err);
        setError("Failed to fetch candidates");
        setLoading(false);
      }
    };

    fetchCandidates();
  }, []);

  if (loading) return <p style={styles.loading}>Loading...</p>;
  if (error) return <p style={styles.error}>{error}</p>;

  return (
    <div style={styles.container}>
      <h1 style={styles.title}>Politicians Page</h1>
      <table style={styles.table}>
        <thead>
          <tr style={styles.headerRow}>
            <th style={styles.th}>Name</th>
            <th style={styles.th}>Description</th>
            <th style={styles.th}>Number of Promises</th>
            <th style={styles.th}>View Promises</th>
          </tr>
        </thead>
        <tbody>
          {candidates.map((candidate) => (
            <tr key={candidate.id} style={styles.row}>
              <td style={styles.td}>{candidate.name}</td>
              <td style={styles.td}>{candidate.description}</td>
              <td style={styles.td}>{candidate.promises}</td>
              <td style={styles.td}>
                <Link to={`/${candidate.id}`}>
                  <button style={styles.button}>View Promises</button>
                </Link>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

// Styles
const styles = {
  container: {
    width: "80%",
    margin: "40px auto",
    textAlign: "center",
  },
  title: {
    fontSize: "28px",
    fontWeight: "bold",
    marginBottom: "20px",
  },
  table: {
    width: "100%",
    borderCollapse: "collapse",
    boxShadow: "0px 4px 6px rgba(0, 0, 0, 0.1)",
  },
  headerRow: {
    backgroundColor: "#f4f4f4",
  },
  th: {
    padding: "12px",
    fontWeight: "bold",
    borderBottom: "2px solid #ddd",
    textAlign: "left",
  },
  row: {
    borderBottom: "1px solid #ddd",
  },
  td: {
    padding: "12px",
    textAlign: "left",
  },
  button: {
    padding: "8px 12px",
    backgroundColor: "#007bff",
    color: "white",
    border: "none",
    borderRadius: "5px",
    cursor: "pointer",
    transition: "0.3s",
  },
  buttonHover: {
    backgroundColor: "#0056b3",
  },
  loading: {
    fontSize: "18px",
    fontWeight: "bold",
    textAlign: "center",
    marginTop: "20px",
  },
  error: {
    color: "red",
    fontSize: "16px",
    textAlign: "center",
    marginTop: "20px",
  },
};

export default PoliticiansPage;
