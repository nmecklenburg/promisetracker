import React from "react";
import CandidateProfile from "./CandidateProfile";
import PromisesList from "./PromisesList";
import api from '../api'
import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';

const HomePage = () => {
  const { candidateId } = useParams();

  const [data, setData] = useState(null);

  const fetchData = async () => {
    try {
      const response = await api.get(`/api/v1/candidates/${candidateId}`); // have daniel lurie as default for now
      console.log(response.data);
      setData(response.data);
    } catch (error) {
      console.error("Error fetching data:", error);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  return (
    <>
      <CandidateProfile candidate={data} />
      <PromisesList candidate={data} />
    </>
  );
};

export default HomePage;
