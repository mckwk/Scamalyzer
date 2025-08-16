import React, { useState, useEffect } from 'react';
import '../styles/main.css';
import '../styles/scamalyzer.css';
import Header from '../components/Header';
import FAQSection from '../components/FAQSection';
import RecentAnalysesCarousel from '../components/RecentAnalysesCarousel';
import { EXAMPLES as QUIZ_EXAMPLES, QuizExample } from '../constants/Examples';

type ResultType = {
  label: string;
  confidence: number;
};

function getRandomScamExamples(): string[] {
  const scamExamples = QUIZ_EXAMPLES.filter(ex => ex.isScam).map(ex => ex.text);
  const shuffled = [...scamExamples].sort(() => Math.random() - 0.5);
  return shuffled.slice(0, 5);
}

const EXAMPLES = getRandomScamExamples();

const FAQS = [
  {
    question: "Is Scamalyzer free to use?",
    answer: "Yes, Scamalyzer is completely free for personal use. It is, in fact, a part  of a Master thesis :)"
  },
  {
    question: "How accurate is Scamalyzer?",
    answer: "Scamalyzer uses AI to detect scams, but no tool is 100% accurate. Always use your best judgment."
  },
  {
    question: "Can Scamalyzer detect all types of scams?",
    answer: "Scamalyzer is designed to spot common scam patterns, but new scams appear all the time. If in doubt, seek advice from trusted sources."
  },
  {
    question: "Where can I learn more about staying safe online?",
    answer: 'Visit our "How to stay safe?" page for tips and resources.'
  }
];

const RECENT_ANALYSES = [
  { message: "Your account will be suspended unless you verify your info.", label: "scam", confidence: 0.97 },
  { message: "Reminder: Your subscription renews tomorrow.", label: "safe", confidence: 0.92 },
  { message: "Hi, can you send me your phone number?", label: "suspicious", confidence: 0.65 },
  { message: "You've won a free iPhone! Click here.", label: "scam", confidence: 0.99 },
  { message: "Your package is out for delivery.", label: "safe", confidence: 0.88 },
];

const ScamalyzerMain: React.FC = () => {
  const [message, setMessage] = useState('');
  const [result, setResult] = useState<ResultType | null>(null);
  const [loading, setLoading] = useState(false);
  const [carouselIdx, setCarouselIdx] = useState(0);

  // Auto-advance carousel every 4 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      setCarouselIdx(idx => (idx + 1) % RECENT_ANALYSES.length);
    }, 4000);
    return () => clearInterval(interval);
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setResult(null);
    try {
      const res = await fetch('/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message }),
      });
      const data = await res.json();
      setResult(data);
    } catch {
      setResult({ label: 'error', confidence: 0 });
    }
    setLoading(false);
  };

  const getAdvice = (label: string) => {
    switch (label) {
      case 'scam':
        return (
          <div>
            <div className="result-icon">🚨</div>
            <div className="result-advice">
              This message appears to be a <b>scam</b>. Do not click any links or share personal information.
              <br />
              <a href="/education" className="result-link">Learn how to spot scams</a>
            </div>
          </div>
        );
      case 'safe':
        return (
          <div>
            <div className="result-icon">🛡️</div>
            <div className="result-advice">
              This message appears <b>safe</b>.
              <br />
              <a href="/education" className="result-link">See tips for staying safe online</a>
            </div>
          </div>
        );
      case 'suspicious':
        return (
          <div>
            <div className="result-icon">⚠️</div>
            <div className="result-advice">
              This message is <b>suspicious</b>. Proceed with caution.
              <br />
              <a href="/education" className="result-link">How to handle suspicious messages</a>
            </div>
          </div>
        );
      default:
        return (
          <div className="result-advice">
            Sorry, something went wrong. Please try again.
          </div>
        );
    }
  };

  return (
    <div className="main-bg page-flex">
      <div className="container">
        <Header
          title="Scamalyzer"
          description="AI-powered detection of scam, phishing, and deceptive messages. Paste your message below and get instant analysis."
        />
        <div className="examples-section">
          <div className="examples-title">Try these examples:</div>
          <ul className="examples-list">
            {EXAMPLES.map((ex, idx) => (
              <li key={idx}>
                <button
                  className="example-btn"
                  type="button"
                  onClick={() => setMessage(ex)}
                >
                  {ex}
                </button>
              </li>
            ))}
          </ul>
        </div>
        <form className="analyze-form" onSubmit={handleSubmit} aria-busy={loading}>
          <textarea
            className="analyze-textarea"
            placeholder="Paste your message here..."
            value={message}
            onChange={e => setMessage(e.target.value)}
            required
          />
          <button
            className="analyze-btn"
            type="submit"
            disabled={loading}
          >
            {loading ? (
              <span className="loading-spinner" aria-label="Analyzing"></span>
            ) : (
              'Analyze'
            )}
          </button>
        </form>
        {result && (
          <div className={`result-box ${result.label}`}>
            <span className={`result-label ${result.label}`}>
              {result.label.toUpperCase()}
            </span>
            <div className="result-confidence">
              Confidence: <progress value={result.confidence} max={1} /> {(result.confidence * 100).toFixed(1)}%
            </div>
            {getAdvice(result.label)}
            <div className="result-disclaimer">
              * Scamalyzer is an AI tool and may not be 100% accurate. Always use your best judgment.
            </div>
          </div>
        )}
        {/* FAQ and Recent Analyses Carousel */}
        <div style={{ display: 'flex', gap: '2rem', marginTop: '2.5rem', alignItems: 'flex-start' }}>
          <div style={{ flex: 2 }}>
            <FAQSection faqs={FAQS} />
          </div>
          <div style={{ flex: 1, minWidth: 220 }}>
            <RecentAnalysesCarousel analyses={RECENT_ANALYSES} />
          </div>
        </div>
      </div>
    </div>
  );
};

export default ScamalyzerMain;