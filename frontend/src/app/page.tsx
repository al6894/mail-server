"use client";
import React, { useState } from "react";
import Link from "next/link";

const App: React.FC = () => {
  const [formData, setFormData] = useState({
    senderEmail: "",
    recipientEmail: "",
    subject: "",
    body: "",
  });

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    console.log("Form Data Submitted:", formData);

    fetch("http://127.0.0.1:5000/send-secure-email", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(formData),
    })
      .then((response) => response.json())
      .then((data) => {
        console.log("Response from secure API:", data);
        alert(data.message || data.error);
      })
      .catch((error) => {
        console.error("Error in secure API:", error);
      });
  };

  return (
    <>
      <header style={styles.header}>
        <div style={styles.logoContainer}>
          <img src="/mail.svg" alt="Mail Icon" style={styles.icon} />
          <h1 style={styles.title}>SecureMail</h1>
        </div>
      </header>
      <main style={styles.main}>
        {/* Navigation Button to Metrics Page */}
        <Link href="/metrics">
          <button style={styles.metricsButton}>View Metrics</button>
        </Link>
        <form style={styles.form} onSubmit={handleSubmit}>
          <label style={styles.label}>
            Sender Email:
            <input
              type="email"
              name="senderEmail"
              value={formData.senderEmail}
              onChange={handleChange}
              style={styles.input}
              placeholder="Enter sender email"
            />
          </label>
          <label style={styles.label}>
            Recipient Email:
            <input
              type="email"
              name="recipientEmail"
              value={formData.recipientEmail}
              onChange={handleChange}
              style={styles.input}
              placeholder="Enter recipient email"
            />
          </label>
          <label style={styles.label}>
            Subject:
            <input
              type="text"
              name="subject"
              value={formData.subject}
              onChange={handleChange}
              style={styles.input}
              placeholder="Enter subject"
            />
          </label>
          <label style={styles.label}>
            Email Body:
            <textarea
              name="body"
              value={formData.body}
              onChange={handleChange}
              style={styles.textarea}
              placeholder="Write your email here"
            />
          </label>
          <button type="submit" style={styles.button}>
            Submit
          </button>
        </form>
      </main>
    </>
  );
};

const styles: { [key: string]: React.CSSProperties } = {
  header: {
    display: "flex",
    alignItems: "center",
    padding: "10px 20px",
    backgroundColor: "#f5f5f5",
    borderBottom: "1px solid #ccc",
  },
  logoContainer: {
    display: "flex",
    alignItems: "center",
  },
  icon: {
    width: 75,
    height: 75,
    marginRight: "10px",
  },
  title: {
    margin: 0,
    fontSize: "48px",
    fontWeight: "bold",
    color: "#333",
  },
  main: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
    height: "calc(100vh - 100px)",
    padding: "20px",
    backgroundColor: "#f9f9f9",
  },
  form: {
    display: "flex",
    flexDirection: "column",
    width: "400px",
    gap: "15px",
    padding: "20px",
    border: "1px solid #ccc",
    borderRadius: "8px",
    backgroundColor: "#fff",
    boxShadow: "0 4px 8px rgba(0, 0, 0, 0.1)",
  },
  label: {
    display: "flex",
    flexDirection: "column",
    fontWeight: "bold",
    marginBottom: "5px",
  },
  input: {
    padding: "10px",
    border: "1px solid #ccc",
    borderRadius: "4px",
    fontSize: "16px",
  },
  textarea: {
    padding: "10px",
    border: "1px solid #ccc",
    borderRadius: "4px",
    fontSize: "16px",
    height: "100px",
    resize: "none",
  },
  button: {
    padding: "10px 20px",
    fontSize: "16px",
    fontWeight: "bold",
    color: "#fff",
    backgroundColor: "#007BFF",
    border: "none",
    borderRadius: "4px",
    cursor: "pointer",
    textAlign: "center",
    alignSelf: "center",
  },
  metricsButton: {
    marginBottom: "20px",
    padding: "10px 20px",
    fontSize: "16px",
    fontWeight: "bold",
    color: "#fff",
    backgroundColor: "#28A745",
    border: "none",
    borderRadius: "4px",
    cursor: "pointer",
  },
};

export default App;
