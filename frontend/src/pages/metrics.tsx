import React, { useEffect, useState } from "react";

const MetricsPage: React.FC = () => {
  const [metrics, setMetrics] = useState<{
    secure: number[];
    non_secure: number[];
  }>({
    secure: [],
    non_secure: [],
  });

  useEffect(() => {
    // Fetch metrics from the backend
    fetch("http://127.0.0.1:5000/metrics")
      .then((response) => response.json())
      .then((data) => {
        setMetrics(data);
      })
      .catch((error) => {
        console.error("Error fetching metrics:", error);
      });
  }, []);

  return (
    <div style={styles.container}>
      <h1 style={styles.heading}>Performance Metrics</h1>
      <div style={styles.section}>
        <h2>Secure Email Metrics</h2>
        <ul>
          {metrics.secure.map((time, index) => (
            <li key={index}>
              Run {index + 1}: {time.toFixed(2)} seconds
            </li>
          ))}
        </ul>
      </div>
      <div style={styles.section}>
        <h2>Non-Secure Email Metrics</h2>
        <ul>
          {metrics.non_secure.map((time, index) => (
            <li key={index}>
              Run {index + 1}: {time.toFixed(2)} seconds
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};

const styles: { [key: string]: React.CSSProperties } = {
  container: {
    padding: "20px",
    fontFamily: "Arial, sans-serif",
  },
  heading: {
    textAlign: "center",
    fontSize: "32px",
    marginBottom: "20px",
  },
  section: {
    marginBottom: "20px",
  },
};

export default MetricsPage;
