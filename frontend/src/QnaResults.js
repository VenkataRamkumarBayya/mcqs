import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import './App.css';

function QnaResults() {
  const location = useLocation();
  const navigate = useNavigate();
  const { qnaPairs } = location.state || { qnaPairs: [] };

  const handleBack = () => {
    navigate('/');
  };

  return (
    <div className="App">
      <header className="App-header">
        <h2>Generated Questions & Answers</h2>
        {qnaPairs.length > 0 ? (
          <div className="results-section">
            <div className="qna-container">
              {qnaPairs.map((item, index) => (
                <div key={index} className="qna-pair">
                  <p><strong>Question {item.question_number}:</strong> {item.question}</p>
                  {Object.entries(item.options).map(([key, value]) => (
                    <p
                      key={key}
                      style={{
                      fontWeight: key === item.answer ? 'bold' : 'normal',
                      color: key === item.answer ? 'lightgreen' : 'white',
                      backgroundColor: key === item.answer ? '#1e3d2f' : 'black',
                      padding: '6px 12px',
                      borderRadius: '4px',
                      marginBottom: '4px',
                      }}
                    >
                      {key}. {value}
                    </p>
                  ))}
                  <p><strong>Correct Answer:</strong> {item.answer} — {item.options[item.answer]}</p>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <p>No Q&A pairs generated yet. Please go back and upload a file.</p>
        )}
        <button onClick={handleBack} className="back-button">Go Back</button>
      </header>
    </div>
  );
}

export default QnaResults;
