import React from "react";
import { useNavigate } from "react-router-dom";

const LoginPage = ({ setIsJournalist }) => {
  const navigate = useNavigate();

  const handleLoginSignup = () => {
    setIsJournalist(true);
    navigate("/"); // Redirect to the home page
  };

  return (
    <div style={styles.container}>
      <h2>I'm a journalist and I want to contribute to the promise tracker!</h2>
      <button style={styles.button} onClick={handleLoginSignup}>
        Log In
      </button>
      <button style={styles.button} onClick={handleLoginSignup}>
        Sign Up
      </button>
    </div>
  );
};

const styles = {
  container: {
    textAlign: "center",
    padding: "50px",
    fontFamily: "Arial, sans-serif",
  },
  button: {
    margin: "10px",
    padding: "10px 20px",
    fontSize: "16px",
    cursor: "pointer",
    backgroundColor: "#007BFF",
    color: "white",
    border: "none",
    borderRadius: "5px",
  },
};

export default LoginPage;
