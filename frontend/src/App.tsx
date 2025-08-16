import React from 'react';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
import ScamalyzerMain from './pages/ScamalyzerMain';
import EducationPage from './pages/EducationPage';
import NavBar from './components/NavBar';
import Footer from './components/Footer';
import './styles/navigation.css';


const App: React.FC = () => {
  return (
    <Router>
      <NavBar />
      <div className="main-bg page-flex">
        <Switch>
          <Route path="/" exact component={ScamalyzerMain} />
          <Route path="/education" component={EducationPage} />
        </Switch>
        <Footer />
      </div>
    </Router>
  );
};

export default App;