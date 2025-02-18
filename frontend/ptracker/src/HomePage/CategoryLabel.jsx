import React from "react";

const styles = {
  category: {
    display: "inline-block",
    backgroundColor: "#e0e0e0",
    padding: "4px 10px",
    borderRadius: "10px",
    marginRight: "8px",
  },
};

const CategoryLabel = ({ category }) => {
  return <span style={styles.category}>{category}</span>;
};

export default CategoryLabel;
