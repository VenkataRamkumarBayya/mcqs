import React, { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import './App.css';

function QnaResults() {
  const location = useLocation();
  const navigate = useNavigate();
  const { qnaPairs } = location.state || { qnaPairs: [] };
  const [selectedAnswers, setSelectedAnswers] = useState({});

  const handleOptionClick = (questionIndex, selectedOption) => {
    setSelectedAnswers({
      ...selectedAnswers,
      [questionIndex]: selectedOption,
    });
  };

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
                  {Object.entries(item.options).map(([key, value]) => {
                    const selection = selectedAnswers[index];
                    const isCorrect = item.answer === key;
                    let className = "option";

                    if (selection === key) { // If this option has been selected
                      className += isCorrect ? " correct" : " incorrect";
                    }

                    return (
                      <p
                        key={key}
                        className={className}
                        onClick={() => !selection && handleOptionClick(index, key)} // Allow selection only once
                      >
                        {key}. {value}
                      </p>
                    );
                  })}
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
