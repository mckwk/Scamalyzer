import React, { useState } from 'react';
import '../styles/main.css';
import '../styles/education.css';
import Header from '../components/Header';
import EducationTile from '../components/EducationTile';
import tileData from '../constants/TileData';

const EducationPage: React.FC = () => {
  const [expandedIdx, setExpandedIdx] = useState<number | null>(null);

  return (
    <div className="main-bg page-flex">
      <div className="container wide">
        <Header
          title="How to stay safe online?"
          description="Scamalyzer helps you spot and avoid online scams, phishing, and deceptive messages. These tips are written for everyone, no matter your experience with computers or the internet."
        />
      </div>
      <section className="education-tiles">
        {tileData.map((tile, idx) => (
          <EducationTile
            key={tile.title}
            title={tile.title}
            subtitle={tile.subtitle}
            expanded={expandedIdx === idx}
            onExpand={() => setExpandedIdx(expandedIdx === idx ? null : idx)}
          >
            {tile.content}
          </EducationTile>
        ))}
      </section>
    </div>
  );
};

export default EducationPage;