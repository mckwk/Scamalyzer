import React from 'react';

interface FooterProps {
  showFtcLink?: boolean;
}

const Footer: React.FC<FooterProps> = ({ showFtcLink }) => (
  <footer className="footer" style={{ marginTop: '2rem' }}>
    <p>
      Scamalyzer &copy; {new Date().getFullYear()} &mdash; Protecting you from digital deception.<br />
    </p>
  </footer>
);

export default Footer;