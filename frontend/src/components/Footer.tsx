import React from 'react';

const Footer: React.FC = () => (
  <footer className="footer" style={{ marginTop: '2rem' }}>
    <p>
      Scamalyzer &copy; {new Date().getFullYear()} &mdash; Protecting you from digital deception.<br />
    </p>
  </footer>
);

export default Footer;