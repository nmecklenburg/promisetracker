import React from "react";
import PromisesTable from "./PromisesTable";

const PromisesList = ({ candidate, isJournalist }) => {

  return (
    <div>
        <h1 style={styles.title}>Explore All Promises</h1>
        <PromisesTable candidate={candidate} isJournalist={isJournalist} />
    </div>
  );
};

export default PromisesList;

const styles = {
    title: {
      fontSize: "32px",
      fontWeight: "500",
      fontFamily: "Arial, sans-serif",
      textAlign: "center",
      paddingTop: "30px"
    },
  };
  