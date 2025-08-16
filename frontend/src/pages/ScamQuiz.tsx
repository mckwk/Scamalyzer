import React, { useState } from 'react';
import '../styles/scamquiz.css';
import { EXAMPLES, QuizExample } from '../constants/Examples';

function getRandomExamples(): QuizExample[] {
  const shuffled = [...EXAMPLES].sort(() => Math.random() - 0.5);
  return shuffled.slice(0, 5);
}

const ScamQuiz: React.FC = () => {
  const [examples, setExamples] = useState<QuizExample[]>(getRandomExamples());
  const [current, setCurrent] = useState(0);
  const [answers, setAnswers] = useState<(boolean | null)[]>([]);
  const [score, setScore] = useState(0);
  const [showAnswer, setShowAnswer] = useState(false);
  const [finished, setFinished] = useState(false);

  const handleAnswer = (answer: boolean) => {
    if (showAnswer || finished) return;
    const correct = examples[current].isScam === answer;
    setAnswers([...answers, answer]);
    if (correct) setScore(score + 1);
    setShowAnswer(true);
  };

  const handleNext = () => {
    if (current < examples.length - 1 && answers.length < 5) {
      setCurrent(current + 1);
      setShowAnswer(false);
    } else {
      setFinished(true);
    }
  };

  const handleRestart = () => {
    setExamples(getRandomExamples());
    setCurrent(0);
    setAnswers([]);
    setScore(0);
    setShowAnswer(false);
    setFinished(false);
  };

  return (
    <div className="scamquiz-container container">
      <h1 className="scamquiz-title">Scam Spotting Quiz</h1>
      <p className="scamquiz-desc">
        Can you spot the scam? For each message, choose whether you think it's a scam or safe.
      </p>
      {!finished ? (
        <>
          <div className="scamquiz-tile">
            <strong>Round {current + 1} of 5:</strong>
            <div className="scamquiz-example">{examples[current].text}</div>
          </div>
          <div className="scamquiz-btn-row">
            <button
              className="analyze-btn scamquiz-btn"
              style={{
                background: answers[current] === true ? '#630875' : 'var(--accent-color)',
                opacity: showAnswer ? 0.7 : 1,
              }}
              disabled={showAnswer}
              onClick={() => handleAnswer(true)}
            >
              Scam
            </button>
            <button
              className="analyze-btn scamquiz-btn"
              style={{
                background: answers[current] === false ? '#2522ac' : 'var(--accent-color)',
                opacity: showAnswer ? 0.7 : 1,
              }}
              disabled={showAnswer}
              onClick={() => handleAnswer(false)}
            >
              Safe
            </button>
          </div>
          {showAnswer && (
            <div className="scamquiz-answer">
              Correct answer:{" "}
              <span style={{ color: examples[current].isScam ? '#ff3b3b' : '#3bff7a' }}>
                {examples[current].isScam ? 'Scam' : 'Safe'}
              </span>
              <br />
              {answers[current] === examples[current].isScam ? (
                <span style={{ color: '#3bff7a' }}>You got it right!</span>
              ) : (
                <span style={{ color: '#ff3b3b' }}>You got it wrong.</span>
              )}
            </div>
          )}
          <button
            className="analyze-btn scamquiz-next-btn"
            disabled={!showAnswer}
            onClick={handleNext}
          >
            {current === 4 ? "Finish Quiz" : "Next"}
          </button>
          <div className="scamquiz-score">
            Score: {score} / {answers.length}
          </div>
        </>
      ) : (
        <div className="scamquiz-final">
          <h2
            className="scamquiz-final-title"
            style={{ color: score >= 4 ? '#3bff7a' : score >= 2 ? '#ffe13b' : '#ff3b3b' }}
          >
            Final Score: {score} / 5
          </h2>
          <ol className="scamquiz-final-list">
            {examples.map((ex, idx) => (
              <li key={idx} className="scamquiz-final-item">
                <div>
                  <strong>{ex.text}</strong>
                  <br />
                  <span>
                    Correct: <span style={{ color: ex.isScam ? '#ff3b3b' : '#3bff7a' }}>
                      {ex.isScam ? 'Scam' : 'Safe'}
                    </span>
                  </span>
                  <br />
                  <span>
                    Your answer: <span style={{ color: answers[idx] === ex.isScam ? '#3bff7a' : '#ff3b3b' }}>
                      {answers[idx] === undefined ? 'No answer' : answers[idx] ? 'Scam' : 'Safe'}
                    </span>
                  </span>
                </div>
              </li>
            ))}
          </ol>
          <button
            className="analyze-btn scamquiz-playagain-btn"
            onClick={handleRestart}
          >
            Play Again
          </button>
        </div>
      )}
    </div>
  );
};

export default ScamQuiz;