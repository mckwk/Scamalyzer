import React from 'react';

interface HeaderProps {
  title: string;
  description?: string;
}

const Header: React.FC<HeaderProps> = ({ title, description }) => (
  <header>
    <h1 className="project-title">{title}</h1>
    {description && <p className="project-desc">{description}</p>}
  </header>
);

export default Header;