import React from "react";
import CandidateProfile from './CandidateProfile';


const HomePage = ({ candidate }) => {

  return (
    candidate ? <CandidateProfile candidate={candidate} /> : "No data found"
  );
};

export default HomePage;