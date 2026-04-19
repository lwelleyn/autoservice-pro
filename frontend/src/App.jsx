import { BrowserRouter, Routes, Route, Link, useLocation } from 'react-router-dom';
import './App.css';
import ClientsPage from './pages/ClientsPage';
import CarsPage from './pages/CarsPage';
import WorkOrdersPage from './pages/WorkOrdersPage';

function NavLink({ to, children }) {
  const location = useLocation();
  const isActive = location.pathname === to;
  return (
    <Link to={to} className={`nav-link ${isActive ? 'active' : ''}`}>
      {children}
    </Link>
  );
}

function App() {
  return (
    <BrowserRouter>
      <div className="app">
        <header className="header">
          <h1>AutoService Pro</h1>
          <nav className="nav">
            <NavLink to="/clients">Clients</NavLink>
            <NavLink to="/cars">Cars</NavLink>
            <NavLink to="/work-orders">Work Orders</NavLink>
          </nav>
        </header>
        <main className="main">
          <Routes>
            <Route path="/clients" element={<ClientsPage />} />
            <Route path="/cars" element={<CarsPage />} />
            <Route path="/work-orders" element={<WorkOrdersPage />} />
            <Route path="*" element={<ClientsPage />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;