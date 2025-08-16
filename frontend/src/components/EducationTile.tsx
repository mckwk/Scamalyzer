import React from 'react';
import '../styles/education.css';

interface EducationTileProps {
  title: string;
  subtitle?: string;
  children: React.ReactNode;
  expanded: boolean;
  onExpand: () => void;
}

const EducationTile: React.FC<EducationTileProps> = ({
  title,
  subtitle,
  children,
  expanded,
  onExpand
}) => (
  <div className={`education-tile${expanded ? ' expanded' : ''}`}>
    <button
      className="education-tile-toggle"
      onClick={onExpand}
      aria-expanded={expanded}
      aria-controls={`tile-content-${title}`}
      tabIndex={0}
      type="button"
    >
      <span className="education-tile-title">{title}</span>
      <span className="education-tile-arrow" aria-hidden="true">
        {expanded ? '▲' : '▼'}
      </span>
      <span className="education-tile-toggle-label">
        {expanded ? 'Hide details' : 'Show details'}
      </span>
    </button>
    {subtitle && (
      <div className="education-tile-subtitle">
        {subtitle.split('\n').map((line, idx, arr) => (
          <React.Fragment key={idx}>
            {line}
            {idx < arr.length - 1 && <br />}
          </React.Fragment>
        ))}
      </div>
    )}
    <div
      id={`tile-content-${title}`}
      className={`education-tile-content${expanded ? ' show' : ''}`}
    >
      {children}
    </div>
  </div>
);

export default EducationTile;