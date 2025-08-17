import React, { useState } from 'react';
import '../styles/faq.css';

type FAQ = {
  question: string;
  answer: string;
};

interface FAQSectionProps {
  faqs: FAQ[];
}

const FAQSection: React.FC<FAQSectionProps> = ({ faqs }) => {
  const [faqOpen, setFaqOpen] = useState<number | null>(null);

  return (
    <div className="faq-section">
      <h3 className="faq-title">Frequently Asked Questions</h3>
      <ul className="faq-list">
        {faqs.map((faq, idx) => {
          const answerId = `faq-answer-${idx}`;
          return (
            <li key={idx} className="faq-list-item">
              <button
                type="button"
                className="faq-question"
                aria-expanded={faqOpen === idx}
                aria-controls={answerId}
                aria-label={`Toggle answer for: ${faq.question}`}
                onClick={() => setFaqOpen(faqOpen === idx ? null : idx)}
              >
                {faq.question}
                <span className="faq-arrow">
                  {faqOpen === idx ? '▲' : '▼'}
                </span>
              </button>
              {faqOpen === idx && (
                <div className="faq-answer" id={answerId}>
                  {faq.answer}
                </div>
              )}
            </li>
          );
        })}
      </ul>
    </div>
  );
};

export default FAQSection;