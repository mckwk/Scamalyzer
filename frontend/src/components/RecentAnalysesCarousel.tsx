import React, { useEffect, useState } from 'react';
import '../styles/carousel.css';
import { EXAMPLES } from '../constants/Examples';

type Analysis = {
  message: string;
  label: string;
  confidence: number;
};

function getRandomAnalyses(): Analysis[] {
  const shuffled = [...EXAMPLES].sort(() => Math.random() - 0.5);
  return shuffled.slice(0, 5).map(ex => ({
    message: ex.text,
    label: ex.isScam ? 'scam' : 'safe',
    confidence: ex.confidence ?? 0.95,
  }));
}

const analyses = getRandomAnalyses();

const RecentAnalysesCarousel: React.FC = () => {
  const [carouselIdx, setCarouselIdx] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setCarouselIdx(idx => (idx + 1) % analyses.length);
    }, 8000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="recent-analyses-carousel">
      <div className="recent-analyses-title">
        Recent Analyses
      </div>
      <div>
        <div
          className={`result-box ${analyses[carouselIdx].label} recent-analyses-box`}
        >
          <div className="result-label recent-analyses-label">
            {analyses[carouselIdx].label.toUpperCase()}
          </div>
          <div className="recent-analyses-message">
            "{analyses[carouselIdx].message}"
          </div>
          <div className="result-confidence recent-analyses-confidence">
            Confidence: <progress value={analyses[carouselIdx].confidence} max={1} style={{ width: '80px', height: '8px' }} /> {(analyses[carouselIdx].confidence * 100).toFixed(1)}%
          </div>
        </div>
      </div>
    </div>
  );
};

export default RecentAnalysesCarousel;