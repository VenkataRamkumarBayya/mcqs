import React, { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import './App.css';

function QnaResults() {
  const location = useLocation();
  const navigate = useNavigate();
  const { qnaPairs: initialQnaPairs, rawText, numQuestions } = location.state || { qnaPairs: [], rawText: '', numQuestions: 0 };
  const [quizQnaPairs, setQuizQnaPairs] = useState([]);
  const [selectedAnswers, setSelectedAnswers] = useState({});
  const [quizStarted, setQuizStarted] = useState(false);
  const [loadingQuiz, setLoadingQuiz] = useState(false);

  const handleStartQuiz = async () => {
    setLoadingQuiz(true);
    try {
      console.log('Attempting to fetch quiz MCQs...');
      console.log('Raw text length:', rawText.length);
      console.log('Number of questions requested:', numQuestions);
      console.log('Excluded questions count:', initialQnaPairs.length);

      const response = await fetch('http://localhost:5000/generate_quiz_mcqs', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          raw_text: rawText,
          num_questions: parseInt(numQuestions), // Ensure it's an integer
          excluded_questions: initialQnaPairs.map(q => q.question) // Pass existing questions
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setQuizQnaPairs(data);
        setQuizStarted(true);
      } else {
        const errorData = await response.json();
        console.error('Backend Error:', errorData);
        alert(`Error generating new questions: ${errorData.error || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Error fetching new questions:', error);
      alert('An error occurred while fetching new questions.');
    } finally {
      setLoadingQuiz(false);
    }
  };

  const handleOptionClick = (questionIndex, selectedOption) => {
    // Only allow selection if quiz has started
    if (!quizStarted) return;

    setSelectedAnswers({
      ...selectedAnswers,
      [questionIndex]: selectedOption,
    });
  };

  const handleBack = () => {
    navigate('/');
  };

  const currentQnaPairs = quizStarted ? quizQnaPairs : initialQnaPairs;

  return (
    <div className="App">
      <header className="App-header">
        <h2>Generated Questions & Answers</h2>
        {currentQnaPairs.length > 0 ? (
          <div className="results-section">
            <div className="qna-container">
              {currentQnaPairs.map((item, index) => {
                const isCorrect = item.answer === selectedAnswers[index];
                const selectionMade = !!selectedAnswers[index];

                return (
                  <div key={index} className="qna-pair">
                    <p><strong>Question {item.question_number}:</strong> {item.question}</p>
                    {Object.entries(item.options).map(([key, value]) => {
                      let className = "option";

                      // Pre-highlight the correct answer only when quiz has not started
                      if (!quizStarted && item.answer === key) {
                        className += " pre-highlight";
                      }

                      // Apply highlighting based on selection when quiz has started
                      if (quizStarted && selectionMade) {
                        if (item.answer === key) {
                          className += " correct";
                        } else if (selectedAnswers[index] === key) {
                          className += " incorrect";
                        }
                      }

                      return (
                        <p
                          key={key}
                          className={className}
                          onClick={() => quizStarted && !selectionMade && handleOptionClick(index, key)}
                        >
                          {key}. {value}
                        </p>
                      );
                    })}
                    {quizStarted && selectionMade && selectedAnswers[index] !== item.answer && (
                      <p className="correct-answer-display">
                        Correct Answer: {item.answer}. {item.options[item.answer]}
                      </p>
                    )}
                  </div>
                );
              })}
            </div>
            {!quizStarted && !loadingQuiz && (
              <button onClick={handleStartQuiz} className="start-quiz-button">Start Quiz</button>
            )}
            {loadingQuiz && <div className="loader"></div>}
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
