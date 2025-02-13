import React from "react";
import CandidateProfile from "./CandidateProfile";
import PromisesList from "./PromisesList";

const HomePage = ({ candidate }) => {
  return (
    <>
      <CandidateProfile candidate={candidate} />
      <PromisesList candidate={candidate} />
    </>
  );
};

export default HomePage;
