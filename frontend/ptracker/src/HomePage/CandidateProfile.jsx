import React from "react";

const CandidateProfile = ({ candidate }) => {
  if (!candidate) {
    return <p>No candidates found</p>;
  }

  return (
    <div style={styles.card}>
      {/* Blue Background Bar */}
      <div style={styles.blueBar}>
        {/* Circular Image */}
        <div style={styles.imageContainer}>
          <img
            src="https://upload.wikimedia.org/wikipedia/commons/3/3c/Daniel_Lurie_Headshot.jpg"
            alt="Daniel Lurie"
            style={styles.profileImage}
          />
        </div>

        {/* Text Content */}
        <div style={styles.content}>
          <h1 style={styles.title}>{candidate.name}</h1>
          <h2 style={styles.subtitle}>Mayor of San Francisco, CA</h2>
          <p style={styles.date}>January 2025 - Present</p>
          <p style={styles.description}>
            {candidate.description}
          </p>
        </div>
      </div>
    </div>
  );
};

export default CandidateProfile;

const styles = {
  card: {
    marginTop: "50px",
    position: "relative",
    background: "white",
    borderRadius: "10px",
    boxShadow: "0 4px 8px rgba(0, 0, 0, 0.1)",
    fontFamily: "Arial, sans-serif",
    width: "100%",
  },
  blueBar: {
    background: "#7DAFF5",
    display: "flex",
    alignItems: "center",
    padding: "20px",
    height: "180px", // Slightly increased height for better proportions
    position: "relative",
    width: "100%",
  },
  imageContainer: {
    flexShrink: 0,
    width: "300px",
    height: "300px",
    borderRadius: "50%",
    overflow: "hidden",
    boxShadow: "0 4px 6px rgba(0, 0, 0, 0.2)",
    left: "20px",
    top: "0",
    transform: "translateY(-2%)",
    zIndex: 3,
  },
  profileImage: {
    width: "100%",
    height: "100%",
    objectFit: "cover",
  },
  content: {
    flex: 1,
    marginLeft: "10px", // Adjusted to match new image size
    color: "black",
  },
  title: {
    fontSize: "26px",
    fontWeight: "bold",
    margin: "5px 0",
  },
  subtitle: {
    fontSize: "18px",
    fontWeight: "normal",
  },
  date: {
    fontSize: "14px",
    marginBottom: "10px",
  },
  description: {
    fontSize: "14px",
    lineHeight: "1.4",
  },
};
