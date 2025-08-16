import React, { useState } from 'react';
import '../styles/main.css';
import '../styles/education.css';
import Header from '../components/Header';
import EducationTile from '../components/EducationTile';

type TileData = {
  title: string;
  subtitle?: string;
  content: React.ReactNode;
};

const tileData: TileData[] = [
  {
    title: "How to recognize a scam",
    subtitle: "Learn the warning signs of scams in messages, emails, calls, and online posts.",
    content: (
      <ul>
        <li>
          <strong>Urgency and threats:</strong> Scammers often say you must act quickly or something bad will happen.
          <span className="example">Example: “Your account will be closed in 24 hours unless you act now.”</span>
        </li>
        <li>
          <strong>Strange links:</strong> Be careful with links you don’t recognize. If you’re unsure, don’t click.
          <span className="example">Example: Links like “secure-bank-login.com” instead of your real bank.</span>
        </li>
        <li>
          <strong>Unusual requests:</strong> If someone asks for money, gift cards, or personal information, be cautious.
          <span className="example">Example: “Please buy gift cards and send me the codes.”</span>
        </li>
        <li>
          <strong>Spelling and grammar mistakes:</strong> Many scam messages have errors or sound odd.
          <span className="example">Example: “Congratulation! You has win.”</span>
        </li>
        <li>
          <strong>Too good to be true:</strong> If an offer seems unbelievable, it probably isn’t real.
          <span className="example">Example: “You’ve won a $1,000 gift card!”</span>
        </li>
        <li>
          <strong>Phone call scams:</strong> Watch out for robocalls, fake tech support, or government calls.
          <span className="example">Example: “This is the IRS. You owe money and must pay now.”</span>
        </li>
        <li>
          <strong>Verify requests:</strong> If you’re unsure, contact the company directly using their official website or phone number.
        </li>
      </ul>
    )
  },
  {
    title: "How to handle suspicious messages",
    subtitle: "Know what to do if you get a message that seems off or makes you uncomfortable.",
    content: (
      <ul>
        <li>
          <strong>Don’t reply:</strong> Ignore messages that seem suspicious. Take a screenshot if you want to report it.
          <span className="example">Tip: Save evidence before deleting.</span>
        </li>
        <li>
          <strong>Don’t click links or open attachments:</strong> These can be dangerous.
        </li>
        <li>
          <strong>Block the sender:</strong> Stop further messages by blocking the sender.
        </li>
        <li>
          <strong>Report the message:</strong> Use the “Report spam” or “Report phishing” option in your email or messaging app.
        </li>
        <li>
          <strong>Check with the official organization:</strong> If a message claims to be from your bank or another company, contact them using their official website or phone number before deleting.
        </li>
        <li>
          <strong>Real companies won’t ask for sensitive info:</strong> Legitimate businesses will never ask for your password or bank details by email or text.
        </li>
        <li>
          <strong>Ask someone you trust:</strong> If you’re unsure, talk to a friend or family member.
        </li>
      </ul>
    )
  },
  {
    title: "Smart online habits",
    subtitle: "Protect yourself every day with these simple habits.",
    content: (
      <ul>
        <li>
          <strong>Be careful with personal information:</strong> Don’t share your passwords, bank details, or address unless you’re sure it’s safe.
        </li>
        <li>
          <strong>Use strong passwords:</strong> Make your passwords hard to guess and don’t use the same one everywhere.
          <span className="example">Example: Use “Turtle!Rainbow!2025” instead of “password123”.</span>
        </li>
        <li>
          <strong>Use a password manager:</strong> These tools help you create and remember strong, unique passwords for every site.
        </li>
        <li>
          <strong>Keep your devices updated:</strong> Updates help protect you from new threats.
        </li>
        <li>
          <strong>Turn on two-step verification:</strong> This adds extra security to your accounts.
        </li>
        <li>
          <strong>Be careful on public Wi-Fi:</strong> Avoid logging into important accounts on free public Wi-Fi unless you use a VPN.
        </li>
        <li>
          <strong>Watch out on social media:</strong> Be cautious of fake giveaways, job offers, or online stores.
          <span className="example">Example: “You’ve won a free iPhone! Click here.”</span>
        </li>
      </ul>
    )
  },
  {
    title: "If you think you’ve been scammed",
    subtitle: "Don’t panic—anyone can fall for a scam. Here’s what to do next.",
    content: (
      <ul>
        <li>
          <strong>Don’t be embarrassed:</strong> Scams can happen to anyone.
        </li>
        <li>
          <strong>Stop all contact:</strong> Don’t reply to the scammer anymore.
        </li>
        <li>
          <strong>Change your passwords:</strong> If you shared any, change them right away.
        </li>
        <li>
          <strong>Contact your bank:</strong> If you sent money or shared bank details, call your bank as soon as possible.
        </li>
        <li>
          <strong>Check your credit report / freeze credit:</strong> If you shared ID details, consider checking your credit or freezing it (especially in the US).
        </li>
        <li>
          <strong>Report the scam:</strong> Tell your local authorities or use official websites (see resources below).
        </li>
        <li>
          <strong>Ask for help:</strong> Talk to someone you trust or get support from organizations that help scam victims.
          <span className="example">Examples: <a href="https://cybercrimesupport.org/" target="_blank" rel="noopener noreferrer">Cybercrime Support Network</a> (US), <a href="https://www.victimsupport.org.uk/" target="_blank" rel="noopener noreferrer">Victim Support UK</a></span>
        </li>
        <li>
          <strong>Take care of your mental health:</strong> Scams can be upsetting. It’s okay to seek emotional support.
        </li>
      </ul>
    )
  },
  {
    title: "Helpful resources",
    subtitle: "Find more tips, guides, and support from trusted organizations.",
    content: (
      <>
        <div>
          <strong>Practical guides:</strong>
          <ul>
            <li>
              <a href="https://staysafeonline.org/" target="_blank" rel="noopener noreferrer">
                StaySafeOnline.org: Simple advice for everyone
              </a>
            </li>
            <li>
              <a href="https://www.consumer.ftc.gov/articles/how-recognize-and-avoid-phishing-scams" target="_blank" rel="noopener noreferrer">
                FTC: How to recognize and avoid phishing scams
              </a>
            </li>
            <li>
              <a href="https://www.ncsc.gov.uk/collection/phishing-scams" target="_blank" rel="noopener noreferrer">
                UK National Cyber Security Centre: Phishing Scams
              </a>
            </li>
            <li>
              <a href="https://www.getsafeonline.org/" target="_blank" rel="noopener noreferrer">
                Get Safe Online: Internet safety advice
              </a>
            </li>
          </ul>
        </div>
        <div>
          <strong>Support and recovery:</strong>
          <ul>
            <li>
              <a href="https://cybercrimesupport.org/" target="_blank" rel="noopener noreferrer">
                Cybercrime Support Network (US)
              </a>
            </li>
            <li>
              <a href="https://fraudadvisorypanel.org/" target="_blank" rel="noopener noreferrer">
                Fraud Advisory Panel (UK)
              </a>
            </li>
            <li>
              <a href="https://www.victimsupport.org.uk/" target="_blank" rel="noopener noreferrer">
                Victim Support UK
              </a>
            </li>
          </ul>
        </div>
        <div>
          <strong>For older adults:</strong>
          <ul>
            <li>
              <a href="https://www.aarp.org/money/scams-fraud/" target="_blank" rel="noopener noreferrer">
                AARP Fraud Watch Network
              </a>
            </li>
          </ul>
        </div>
        <div>
          <strong>For students/young people:</strong>
          <ul>
            <li>
              <a href="https://www.foolprooffoundation.org/" target="_blank" rel="noopener noreferrer">
                FoolProof Foundation: Scam-Smart Education
              </a>
            </li>
            <li>
              <a href="https://information-services.ed.ac.uk/help-consultancy/is-skills/digital-safety-wellbeing-and-citizenship/fraud-awareness-resources" target="_blank" rel="noopener noreferrer">
                University of Edinburgh: Student Fraud Awareness
              </a>
            </li>
          </ul>
        </div>
        <em>Outside the US/UK? Check your local government website for scam reporting and advice.</em>
      </>
    )
  }
];

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