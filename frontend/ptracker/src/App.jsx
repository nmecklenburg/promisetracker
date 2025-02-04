import { useState, useEffect } from 'react'
import api from './api'
import './App.css'

const App = () => {
  const [data, setData] = useState(null)

  const fetchData = async () => {
    const response = await api.get('/candidates');
    setData(response.data);
  }

  useEffect(() => {
    fetchData();
  }
  , []);

  return (
    <div>
      {data ?? "No data found"}
    </div>
  );
}

export default App
