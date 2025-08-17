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
}) => {
  const sanitizedId = `tile-content-${title.replace(/\s+/g, '-')}`;

  return (
    <div className={`education-tile${expanded ? ' expanded' : ''}`}>
      <button
        className="education-tile-toggle"
        onClick={onExpand}
        aria-expanded={expanded}
        aria-controls={sanitizedId}
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
          {subtitle}
        </div>
      )}
      <div
        id={sanitizedId}
        className={`education-tile-content${expanded ? ' show' : ''}`}
      >
        {children}
      </div>
    </div>
  );
};

export default EducationTile;