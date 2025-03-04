import React, { useState, useEffect } from "react";
import CategoryLabel from "./CategoryLabel";
import api from "../api";
import StatusLabel from "./StatusLabel";

const PromisePopup = ({ promise, candidateId, onClose, editMode, updatePromiseStatus }) => {
  if (!promise) return null;

  const [actions, setActions] = useState([]);
  const [expandedActions, setExpandedActions] = useState({});
  const [citationsByAction, setCitationsByAction] = useState({});
  const [citations, setCitations] = useState([]);
  const [currentCitationIndex, setCurrentCitationIndex] = useState(0);
  const [selectedStatus, setSelectedStatus] = useState(promise.status);
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [newCitationUrl, setNewCitationUrl] = useState("");
  const [newCitationExtract, setNewCitationExtract] = useState("");
  const [isAddingCitation, setIsAddingCitation] = useState(false);
  const [newActionText, setNewActionText] = useState("");
  const [isAddingAction, setIsAddingAction] = useState(false);

  useEffect(() => {
    console.log(promise.id)
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
        console.error("Error fetching data:", error);
      }
    };

    fetchData();
  }, [candidateId, promise.id]);

  const statusMap = {
    0: "Progressing",
    1: "Compromised",
    2: "Delivered",
    3: "Broken",
  };

  // Save status change
  const handleSaveStatus = async (status) => {
    if (editMode) {
      try {
        const response = await api.patch(`/api/v1/candidates/${candidateId}/promises/${promise.id}`, {
          status: status
        });

        console.log("Status updated:", response.data);
        updatePromiseStatus(promise.id, status);
      } catch (error) {
        console.error("Error saving status:", error);
      }
    }
  };

  const handleAddAction = async () => {
    if (!newActionText.trim() || !newCitationUrl.trim() || !newCitationExtract.trim()) {
      alert("Please enter an action description and a valid citation.");
      return;
    }

    try {
      const currentDate = new Date().toISOString();

      // Create the new action with the citation
      const response = await api.post(
        `/api/v1/candidates/${candidateId}/actions/`,
        {
          date: currentDate,
          text: newActionText,
          citations: [
            {
              date: currentDate,
              extract: newCitationExtract,
              url: newCitationUrl
            }
          ],
          promises: [promise.id]
        }
      );
      console.log(response.data)
      console.log("created action: ", currentDate, newActionText, promise.id)

      setActions([...actions, response.data]); // Update UI with new action
      setNewActionText("");
      setNewCitationUrl("");
      setNewCitationExtract("");
      setIsAddingAction(false);
    } catch (error) {
      console.error("Error adding action:", error);
    }
  };

  // Add new citation
  const handleAddCitation = async () => {
    if (!newCitationUrl.trim()) return;

    try {
      const currentDate = new Date().toISOString();
      const response = await api.post(
        `/api/v1/candidates/${candidateId}/promises/${promise.id}/citations`,
        {
          date: currentDate,
          url: newCitationUrl,
          extract: newCitationExtract
        }
      );
      console.log("action created: ", response.data);

      setCitations([...citations, response.data]);
      setNewCitationUrl("");
      setNewCitationExtract("");
      setIsAddingCitation(false);
    } catch (error) {
      console.error("Error adding citation:", error);
    }
  };

  // Fetch citations for a specific action
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
        console.error(`Error fetching citations for action ${actionId}:`, error);
      }
    }
  };

  const nextCitation = () => {
    setCurrentCitationIndex((prevIndex) => (prevIndex + 1) % citations.length);
  };

  const prevCitation = () => {
    setCurrentCitationIndex((prevIndex) =>
      prevIndex === 0 ? citations.length - 1 : prevIndex - 1
    );
  };

  const getStatusLabel = (status) => {
    return statusMap[status] || "Unknown";
  };

  return (
    <div style={styles.overlay}>
      <div style={styles[getStatusLabel(selectedStatus)]}>
        <button style={styles.closeButton} onClick={onClose}>&times;</button>
        {editMode && <div style={styles.editModeBanner}>You are editing this promise. Changes are saved automatically.</div>}

        <h2 style={styles.title}>{promise.text}</h2>

        {/* Status Section */}
        <div style={styles.statusContainer}>
          <span style={styles.statusLabel}>Status:</span>
          {editMode ? (
            <div style={styles.dropdownContainer}>
              <div
                style={{
                  ...statusStyles[getStatusLabel(selectedStatus)],
                  ...styles.dropdownButton,
                }}
                onClick={() => setDropdownOpen(!dropdownOpen)}
              >
                {`${statusMap[selectedStatus]} ▼`}
              </div>
              {dropdownOpen && (
                <div style={styles.dropdownMenu}>
                  {Object.entries(statusMap).map(([key, label]) => (
                    <div
                      key={key}
                      style={{ ...statusStyles[label], ...styles.dropdownItem }}
                      onClick={() => {
                        setSelectedStatus(Number(key));
                        handleSaveStatus(Number(key));
                        setDropdownOpen(false);
                      }}
                    >
                      {label}
                    </div>
                  ))}
                </div>
              )}
            </div>
          ) : (
            <StatusLabel status={statusMap[selectedStatus]} />
          )}
        </div>

        {/* Actions and Citations */}
        <div style={styles.section}>
          <strong>Progress Updates:</strong>
          <div style={styles.actionContainer}>
            <ul style={styles.actionList}>
              {actions.map((action) => (
                <li key={action.id} style={styles.actionItem}>
                  {action.text}
                  <div
                    style={styles.toggleButton}
                    onClick={() => toggleActionCitations(action.id)}
                  >
                    {expandedActions[action.id] ? "Hide Sources" : "View Sources"}
                  </div>
                  {expandedActions[action.id] && (
                    <ul style={styles.citationList}>
                      {citationsByAction[action.id]?.length > 0 ? (
                        citationsByAction[action.id].map((citation) => (
                          <li key={citation.url} style={styles.citationItem}>
                            <a href={citation.url} target="_blank" rel="noopener noreferrer">
                              {`"${citation.extract}"`}
                            </a>
                          </li>
                        ))
                      ) : (
                        <li style={styles.noCitation}>No sources available</li>
                      )}
                    </ul>
                  )}
                </li>
              ))}
            </ul>
          </div>

          {editMode && (
            <div style={styles.addActionContainer}>
              {isAddingAction ? (
                <>
                  <input
                    placeholder="Describe the new action..."
                    value={newActionText}
                    onChange={(e) => setNewActionText(e.target.value)}
                    style={styles.inputField}
                  />
                  <input
                    type="text"
                    placeholder="Citation URL"
                    value={newCitationUrl}
                    onChange={(e) => setNewCitationUrl(e.target.value)}
                    style={styles.inputField}
                  />
                  <input
                    type="text"
                    placeholder="Quote from the source"
                    value={newCitationExtract}
                    onChange={(e) => setNewCitationExtract(e.target.value)}
                    style={styles.inputField}
                  />
                  <div style={styles.buttonGroup}>
                    <button style={styles.addButton} onClick={handleAddAction}>Add Action</button>
                    <button style={styles.cancelButton} onClick={() => setIsAddingAction(false)}>Cancel</button>
                  </div>
                </>
              ) : (
                <button style={styles.addActionButton} onClick={() => setIsAddingAction(true)}>+ Add Action</button>
              )}
            </div>
          )}
        </div>

        {/* Related Articles Section */}
        <div style={styles.section}>
          <strong>Related Articles:</strong>

          {citations.length > 0 && (
            <div style={styles.articleSwipeContainer}>
              <button style={styles.navButton} onClick={prevCitation} disabled={citations.length <= 1}>◀</button>
              <div style={styles.articleCard}>
                <a href={citations[currentCitationIndex].url} target="_blank" rel="noopener noreferrer">
                  {`"${citations[currentCitationIndex].extract}"`}
                </a>
              </div>
              <button style={styles.navButton} onClick={nextCitation} disabled={citations.length <= 1}>▶</button>
            </div>
          )}
          <div style={styles.citationIndex}>{`${currentCitationIndex + 1} / ${citations.length}`}</div>

          {editMode && (
            <div style={styles.addCitationContainer}>
              {isAddingCitation ? (
                <>
                  <input type="text" placeholder="Citation URL" value={newCitationUrl} onChange={(e) => setNewCitationUrl(e.target.value)} style={styles.inputField} />
                  <input type="text" placeholder="Quote (Optional)" value={newCitationExtract} onChange={(e) => setNewCitationExtract(e.target.value)} style={styles.inputField} />
                  <div style={styles.buttonGroup}>
                  <button style={styles.addButton} onClick={handleAddCitation}>Add Citation</button>
                    <button style={styles.cancelButton} onClick={() => setIsAddingCitation(false)}>Cancel</button>
                  </div>
                </>
              ) : (
                    <button style={styles.addCitationButton} onClick={() => setIsAddingCitation(true)}>+ Add Related Article</button>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

const statusStyles = {
  Progressing: {
    padding: "6px 12px",
    color: "black",
    borderRadius: "6px",
    backgroundColor: "#99C3FF",
    border: "1px solid #355581",
  },
  Compromised: {
    padding: "6px 12px",
    color: "black",
    borderRadius: "6px",
    backgroundColor: "#FFF0A2",
    border: "1px solid #AB9629",
  },
  Delivered: {
    padding: "6px 12px",
    color: "black",
    borderRadius: "6px",
    backgroundColor: "#B7FFB5",
    border: "1px solid #59E000",
  },
  Broken: {
    padding: "6px 12px",
    color: "black",
    borderRadius: "6px",
    backgroundColor: "#FF9C9C",
    border: "1px solid #DF0404",
  },
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
    padding: "12px",
    borderRadius: "12px",
    boxShadow: "0 4px 8px rgba(0,0,0,0.2)",
    width: "420px",
    maxWidth: "90%",
    border: "3px solid #99C3FF",
    position: "relative",
  },
  Compromised: {
    backgroundColor: "#fff",
    padding: "12px",
    borderRadius: "12px",
    boxShadow: "0 4px 8px rgba(0,0,0,0.2)",
    width: "420px",
    maxWidth: "90%",
    border: "3px solid #AB9629",
    position: "relative",
  },
  Delivered: {
    backgroundColor: "#fff",
    padding: "12px",
    borderRadius: "12px",
    boxShadow: "0 4px 8px rgba(0,0,0,0.2)",
    width: "420px",
    maxWidth: "90%",
    border: "3px solid #59E000",
    position: "relative",
  },
  Broken: {
    backgroundColor: "#fff",
    padding: "12px",
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
  editModeBanner: {
    backgroundColor: "#ffeb3b",
    color: "#000",
    textAlign: "center",
    padding: "8px",
    fontWeight: "bold",
    borderRadius: "5px",
    marginBottom: "10px",
  },
  dropdownContainer: {
    position: "relative",
    display: "inline-block",
    cursor: "pointer",
  },
  dropdownButton: {
    display: "inline-block",
    padding: "6px 12px",
    borderRadius: "6px",
    border: "1px solid #ccc",
  },
  dropdownMenu: {
    position: "absolute",
    top: "100%",
    left: 0,
    backgroundColor: "#fff",
    borderRadius: "6px",
    boxShadow: "0 4px 6px rgba(0, 0, 0, 0.1)",
    minWidth: "150px",
    zIndex: 1000,
  },
  dropdownItem: {
    padding: "6px 12px",
    cursor: "pointer",
    borderBottom: "1px solid #ddd",
    textAlign: "center",
  },
  saveButton: {
    width: "100%",
    padding: "10px",
    fontSize: "16px",
    fontWeight: "bold",
    color: "#fff",
    backgroundColor: "#b51d1d",
    border: "none",
    borderRadius: "6px",
    cursor: "pointer",
    marginTop: "15px",
    transition: "background-color 0.3s",
  },
  addCitationContainer: {
    marginTop: "5px",
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
  },
  buttonGroup: {
    display: "flex",
    justifyContent: "center",
    gap: "10px",
  },
  addButton: {
    padding: "6px 12px",
    backgroundColor: "#4CAF50",
    color: "white",
    border: "none",
    borderRadius: "5px",
    cursor: "pointer",
  },
  cancelButton: {
    padding: "6px 12px",
    backgroundColor: "#ccc",
    border: "none",
    borderRadius: "5px",
    cursor: "pointer",
  },
  addCitationButton: {
    marginTop: "5px",
    padding: "8px",
    backgroundColor: "#007BFF",
    color: "white",
    border: "none",
    borderRadius: "5px",
    cursor: "pointer",
  },
  addActionContainer: {
    marginTop: "10px",
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
  },
  inputField: {
    width: "100%",
    padding: "5px",
    margin: "5px 0",
    borderRadius: "5px",
    border: "1px solid #ccc",
    fontSize: "14px",
  },
  addActionButton: {
    marginTop: "10px",
    padding: "8px",
    backgroundColor: "#007BFF",
    color: "white",
    border: "none",
    borderRadius: "5px",
    cursor: "pointer",
  },
};
export default PromisePopup;
