import React, { useEffect, useState } from 'react';
import '../styles/carousel.css';

type Analysis = {
  message: string;
  label: string;
  confidence: number;
};

interface RecentAnalysesCarouselProps {
  analyses: Analysis[];
}

const RecentAnalysesCarousel: React.FC<RecentAnalysesCarouselProps> = ({ analyses }) => {
  const [carouselIdx, setCarouselIdx] = useState(0);

  // Auto-advance carousel every 4 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      setCarouselIdx(idx => (idx + 1) % analyses.length);
    }, 4000);
    return () => clearInterval(interval);
  }, [analyses.length]);

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