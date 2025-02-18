import React from "react";

const statusStyles = {
  Progressing: { padding: "6px 12px", color: "black", borderRadius: "4px", backgroundColor: "#99C3FF", border: "1px solid #355581" },
  Compromised: { padding: "6px 12px", color: "black", borderRadius: "4px", backgroundColor: "#FFF0A2", border: "1px solid #AB9629" },
  Delivered: { padding: "6px 12px", color: "black", borderRadius: "4px", backgroundColor: "#B7FFB5", border: "1px solid #59E000" },
  Broken: { padding: "6px 12px", color: "black", borderRadius: "4px", backgroundColor: "#FF9C9C", border: "1px solid #DF0404" },
};

const StatusLabel = ({ status }) => {
  return <span style={statusStyles[status] || {}}>{status}</span>;
};

export default StatusLabel;
