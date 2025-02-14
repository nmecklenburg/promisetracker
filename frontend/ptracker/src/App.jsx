import HomePage from './HomePage/HomePage';
import AboutPage from './AboutPage/AboutPage';
import ContactPage from './ContactPage/ContactPage';
import LoginPage from './LoginPage/LoginPage';
import PoliticiansPage from './PoliticiansPage/PoliticiansPage';
import PromiseCard from './PromiseCard'
import { BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom';

const Navbar = () => {
  return (
    <nav style={styles.navbar}>
      <div style={styles.logo}>
        <span style={styles.logoP}>P</span>
        <span style={styles.logoT}>T</span>
      </div>
      <ul style={styles.navLinks}>
        <li style={styles.navItem}><Link to="/" style={styles.navLink}>Home</Link></li>
        <li style={styles.navItem}><Link to="/about" style={styles.navLink}>About Us</Link></li>
        <li style={styles.navItem}><Link to="/politicians" style={styles.navLink}>Politicians</Link></li>
        <li style={styles.navItem}><Link to="/contact" style={styles.navLink}>Contact Us</Link></li>
        <li style={styles.navItem}><Link to="/login" style={styles.navLink}>Login/Signup</Link></li>
      </ul>
    </nav>
  );
};

const App = () => {

  return (
    <Router>
      <Navbar />
      <div>
        <Routes>
          <Route path="/:candidateId?" element={<HomePage />} />
          <Route path="/about" element={<AboutPage />} />
          <Route path="/politicians" element={<PoliticiansPage />} />
          <Route path="/contact" element={<ContactPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/promise-card/:candidateId" element={<PromiseCard />} />
        </Routes>
      </div>
    </Router>
  );
};

const styles = {
  navbar: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '15px 30px',
    fontFamily: "Arial, sans-serif",
  },
  logo: {
    fontSize: '24px',
    fontWeight: 'bold',
  },
  logoP: {
    color: 'blue',
    fontWeight: 'bold',
  },
  logoT: {
    color: 'brown',
    fontWeight: 'bold',
  },
  navLinks: {
    listStyle: 'none',
    display: 'flex',
    gap: '20px',
    padding: 0,
    margin: 0,
  },
  navItem: {
    display: 'inline',
  },
  navLink: {
    textDecoration: 'none',
    color: 'black',
    fontWeight: 'bold',
  },
  navLinkHover: {
    color: 'gray',
  },
  content: {
    padding: '20px',
  },
};

export default App;