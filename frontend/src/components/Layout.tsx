import { useState } from 'react';
import { NavLink, Outlet } from 'react-router-dom';
import './Layout.css';

interface LayoutProps {
  balance: string | null;
  username: string;
  onLogout: () => void;
}

export function Layout({ balance, username, onLogout }: LayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="layout">
      <button
        className="hamburger"
        onClick={() => setSidebarOpen(!sidebarOpen)}
        aria-label="Toggle menu"
      >
        <span></span>
        <span></span>
        <span></span>
      </button>

      <aside className={`sidebar ${sidebarOpen ? 'open' : ''}`}>
        <div className="sidebar-header">
          <h1>BetLab</h1>
        </div>

        <nav className="sidebar-nav">
          <NavLink to="/" onClick={() => setSidebarOpen(false)}>Games</NavLink>
          <NavLink to="/bets" onClick={() => setSidebarOpen(false)}>Open Bets</NavLink>
          <NavLink to="/history" onClick={() => setSidebarOpen(false)}>History</NavLink>
        </nav>

        <div className="sidebar-footer">
          <div className="user-info">
            <span className="username">{username}</span>
          </div>
          <div className="balance">
            <span className="balance-label">Balance</span>
            <span className="balance-amount">${balance || '...'}</span>
          </div>
          <button className="logout-button" onClick={onLogout}>
            Log out
          </button>
        </div>
      </aside>

      {sidebarOpen && (
        <div className="sidebar-overlay" onClick={() => setSidebarOpen(false)} />
      )}

      <main className="main-content">
        <Outlet />
      </main>
    </div>
  );
}
