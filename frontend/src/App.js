import React, { useState } from 'react';
import { BrowserRouter as Router, Route, Routes, useNavigate } from 'react-router-dom';
import './App.css';
import QnaResults from './QnaResults'; // New component for displaying results

function Home() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [numQuestions, setNumQuestions] = useState(20); // Default to 20 questions
  const navigate = useNavigate();

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
  };

  const handleNumQuestionsChange = (event) => {
    setNumQuestions(parseInt(event.target.value));
  };

  const handleUpload = async () => {
    if (!file) {
      alert('Please select a file first!');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);
    formData.append('num_questions', numQuestions); // Append the selected number of questions

    setLoading(true);

    try {
      const response = await fetch('http://localhost:5000/generate', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        // Read file content to pass to results page for subsequent quiz generation
        const reader = new FileReader();
        reader.onload = (e) => {
          const rawText = e.target.result;
          navigate('/results', { state: { qnaPairs: data, rawText: rawText, numQuestions: numQuestions } });
        };
        reader.readAsText(file);

      } else {
        const errorData = await response.json();
        console.error('Backend Error:', errorData);
        alert(`Error: ${errorData.error || 'Unknown error from backend'}`);
      }
    } catch (error) {
      console.error('Error uploading file:', error);
      alert('An error occurred while uploading the file.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Question & Answer Generation</h1>
        <div className="upload-section">
          <input type="file" onChange={handleFileChange} accept=".txt,.pdf" />
          <div className="question-count-selection">
            <label htmlFor="numQuestions">Number of Questions:</label>
            <select id="numQuestions" value={numQuestions} onChange={handleNumQuestionsChange}>
              <option value={20}>20</option>
              <option value={30}>30</option>
              <option value={40}>40</option>
              <option value={50}>50</option>
            </select>
          </div>
          <button onClick={handleUpload} disabled={loading}>
            {loading ? 'Generating...' : 'Generate Q&A'}
          </button>
        </div>
        {loading && <div className="loader"></div>}
      </header>
    </div>
  );
}

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/results" element={<QnaResults />} />
      </Routes>
    </Router>
  );
}

export default App;