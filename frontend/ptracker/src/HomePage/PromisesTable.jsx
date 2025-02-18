import React, { useState, useEffect } from "react";
import api from "../api";
import { FaPen } from "react-icons/fa";
import StatusLabel from "./StatusLabel";
import CategoryLabel from "./CategoryLabel";

const styles = {
  table: {
    fontFamily: "Arial, sans-serif",
    fontSize: "14px",
    width: "95%",
    borderCollapse: "collapse",
    alignContent: "center",
    margin: "auto",
  },
  th: {
    borderBottom: "1px solid #EEEEEE",
    padding: "12px",
    textAlign: "left",
  },
  td: {
    borderBottom: "1px solid #EEEEEE",
    padding: "12px",
  },
  editButton: {
    padding: "6px",
    borderRadius: "4px",
    backgroundColor: "#e0e0e0",
    border: "none",
    cursor: "pointer",
  },
  centeredText: {
    textAlign: "center",
  },
  paginationWrapper: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    margin: "16px auto",
    width: "95%",
    marginBottom: "20px",
  },
  paginationText: {
    fontFamily: "Arial, sans-serif",
    fontSize: "14px",
    color: "#777777",
  },
  paginationContainer: {
    display: "flex",
    alignItems: "center",
  },
  paginationButton: {
    border: "1px solid #ddd",
    padding: "8px 12px",
    margin: "0 4px",
    cursor: "pointer",
    backgroundColor: "#f8f8f8",
    borderRadius: "4px",
  },
  activePage: {
    backgroundColor: "#6699FF",
    color: "white",
  },
  disabledButton: {
    opacity: 0.5,
    cursor: "not-allowed",
  },
};

const statusLabels = ["Progressing", "Compromised", "Delivered", "Broken"];

const PromisesTable = ({ candidate }) => {
  if (!candidate) {
    return <p>No candidates found</p>;
  }

  const [promises, setPromises] = useState([]);
  const [currentPage, setCurrentPage] = useState(1);
  const promisesPerPage = 10;

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await api.get(
          `/api/v1/candidates/${candidate.id}/promises`
        );
        setPromises(response.data.data);
      } catch (error) {
        console.error("Error fetching data:", error);
      }
    };

    fetchData();
  }, [candidate.id]);

  // Pagination logic
  const indexOfLastPromise = currentPage * promisesPerPage;
  const indexOfFirstPromise = indexOfLastPromise - promisesPerPage;
  const currentPromises = promises.slice(
    indexOfFirstPromise,
    indexOfLastPromise
  );
  const totalPages = Math.ceil(promises.length / promisesPerPage);

  const handlePageChange = (pageNumber) => {
    if (pageNumber >= 1 && pageNumber <= totalPages) {
      setCurrentPage(pageNumber);
    }
  };

  return (
    <div style={{ overflowX: "auto" }}>
      <table style={styles.table}>
        <thead>
          <tr>
            <th style={styles.th}>Promise</th>
            <th style={styles.th}>Categories</th>
            <th style={styles.th}>Citations</th>
            <th style={styles.th}>Status</th>
            <th style={styles.th}></th>
          </tr>
        </thead>
        <tbody>
          {currentPromises.map((promise) => (
            <tr key={promise.id}>
              <td style={styles.td}>{promise.text}</td>
              <td style={styles.td}>
                <CategoryLabel key="Economy" category="Economy" />
                <CategoryLabel key="Health" category="Health" />
              </td>
              <td style={{ ...styles.td, ...styles.centeredText }}>
                {promise.citations ? (
                  <a
                    href="#"
                    style={{ color: "#3498db", textDecoration: "underline" }}
                  >
                    {promise.citations}
                  </a>
                ) : (
                  "N/A"
                )}
              </td>
              <td style={styles.td}>
                <StatusLabel status={statusLabels[promise.status]} />
              </td>
              <td style={styles.td}>
                <button style={styles.editButton}>
                  <FaPen />
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {/* Pagination UI (Showing Text + Pagination Buttons) */}
      {promises.length > promisesPerPage && (
        <div style={styles.paginationWrapper}>
          {/* Left-aligned text */}
          <p style={styles.paginationText}>
            Showing {indexOfFirstPromise + 1}-
            {Math.min(indexOfLastPromise, promises.length)} promises of{" "}
            {promises.length}
          </p>

          {/* Right-aligned pagination buttons */}
          <div style={styles.paginationContainer}>
            {/* Previous Button */}
            <button
              style={{
                ...styles.paginationButton,
                ...(currentPage === 1 ? styles.disabledButton : {}),
              }}
              onClick={() => handlePageChange(currentPage - 1)}
              disabled={currentPage === 1}
            >
              {"<"}
            </button>

            {/* Page Numbers */}
            {Array.from({ length: totalPages }, (_, i) => i + 1)
              .slice(0, 3)
              .map((page) => (
                <button
                  key={page}
                  style={{
                    ...styles.paginationButton,
                    ...(currentPage === page ? styles.activePage : {}),
                  }}
                  onClick={() => handlePageChange(page)}
                >
                  {page}
                </button>
              ))}

            {/* Ellipsis if there are more than 3 pages */}
            {totalPages > 4 && <span style={{ margin: "0 6px" }}>...</span>}

            {/* Last Page */}
            {totalPages > 3 && (
              <button
                style={{
                  ...styles.paginationButton,
                  ...(currentPage === totalPages ? styles.activePage : {}),
                }}
                onClick={() => handlePageChange(totalPages)}
              >
                {totalPages}
              </button>
            )}

            {/* Next Button */}
            <button
              style={{
                ...styles.paginationButton,
                ...(currentPage === totalPages ? styles.disabledButton : {}),
              }}
              onClick={() => handlePageChange(currentPage + 1)}
              disabled={currentPage === totalPages}
            >
              {">"}
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default PromisesTable;
