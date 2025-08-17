import React from 'react';
import { useHistory } from 'react-router-dom';
import ghIcon from '../images/gh.png';
import scamalyzerIcon from '../images/logo-c.png';

const NavBar: React.FC = () => {
  const history = useHistory();
  return (
    <nav className="nav-bar-pro nav-bar-transparent">
      <div className="nav-content nav-content-space">
        <button
          className="nav-logo"
          onClick={() => history.push('/')}
          type="button"
          aria-label="Go to home"
        >
          <img src={scamalyzerIcon} alt="Scamalyzer Icon" className="nav-logo-img" />
        </button>
        <div className="nav-links nav-links-right">
          <button
            className="nav-btn-pro nav-btn-transparent"
            type="button"
            onClick={() => history.push('/education')}
          >
            How to stay safe?
          </button>
          <button
            className="nav-btn-pro nav-btn-transparent"
            type="button"
            onClick={() => history.push('/quiz')}
          >
            Quiz: Can you spot the scam?
          </button>
          <a
            href="https://github.com/mckwk/scamalyzer"
            target="_blank"
            rel="noopener noreferrer"
            className="nav-gh-link"
            aria-label="GitHub"
          >
            <img
              src={ghIcon}
              alt="GitHub"
              className="nav-gh-img"
            />
          </a>
        </div>
      </div>
    </nav>
  );
};

export default NavBar;