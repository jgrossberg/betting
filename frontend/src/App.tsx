import { useEffect, useState } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import type { Game, Bet } from './api';
import { api } from './api';
import { Layout } from './components/Layout';
import { GamesPage } from './pages/GamesPage';
import { BetsPage } from './pages/BetsPage';
import './App.css';

const USER_ID = localStorage.getItem('userId') || '';

function formatOdds(odds: string | null): string {
  if (!odds) return '-';
  const num = parseFloat(odds);
  return num > 0 ? `+${num}` : `${num}`;
}

function BetModal({
  game,
  onClose,
  onSubmit
}: {
  game: Game;
  onClose: () => void;
  onSubmit: (betType: string, selection: string, stake: string) => void;
}) {
  const [betType, setBetType] = useState<'moneyline' | 'spread' | 'over_under'>('moneyline');
  const [selection, setSelection] = useState<'home' | 'away' | 'over' | 'under'>('home');
  const [stake, setStake] = useState('10');

  const getOddsForSelection = () => {
    if (betType === 'moneyline') {
      return selection === 'home' ? game.home_moneyline : game.away_moneyline;
    } else if (betType === 'spread') {
      return selection === 'home' ? game.home_spread_odds : game.away_spread_odds;
    } else {
      return selection === 'over' ? game.over_odds : game.under_odds;
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={e => e.stopPropagation()}>
        <h2>Place Bet</h2>
        <p>{game.away_team} @ {game.home_team}</p>

        <div className="form-group">
          <label>Bet Type</label>
          <select value={betType} onChange={e => {
            setBetType(e.target.value as typeof betType);
            setSelection(e.target.value === 'over_under' ? 'over' : 'home');
          }}>
            <option value="moneyline">Moneyline</option>
            <option value="spread">Spread</option>
            <option value="over_under">Over/Under</option>
          </select>
        </div>

        <div className="form-group">
          <label>Selection</label>
          <select value={selection} onChange={e => setSelection(e.target.value as typeof selection)}>
            {betType === 'over_under' ? (
              <>
                <option value="over">Over {game.total_points}</option>
                <option value="under">Under {game.total_points}</option>
              </>
            ) : (
              <>
                <option value="away">{game.away_team} {betType === 'spread' ? game.away_spread : ''}</option>
                <option value="home">{game.home_team} {betType === 'spread' ? game.home_spread : ''}</option>
              </>
            )}
          </select>
        </div>

        <div className="form-group">
          <label>Stake ($)</label>
          <input
            type="number"
            value={stake}
            onChange={e => setStake(e.target.value)}
            min="1"
          />
        </div>

        <div className="bet-summary">
          <p>Odds: {formatOdds(getOddsForSelection())}</p>
        </div>

        <div className="modal-buttons">
          <button className="cancel-button" onClick={onClose}>Cancel</button>
          <button className="submit-button" onClick={() => onSubmit(betType, selection, stake)}>
            Place Bet
          </button>
        </div>
      </div>
    </div>
  );
}

function LoginPage({ onLogin, error }: { onLogin: (username: string) => void; error: string | null }) {
  const [usernameInput, setUsernameInput] = useState('');

  const handleSubmit = () => {
    if (usernameInput.trim()) {
      onLogin(usernameInput);
    }
  };

  return (
    <div className="login-page">
      <div className="login-card">
        <h1>BetLab</h1>
        <p className="login-subtitle">Test your betting strategies with real odds</p>
        <div className="login-form">
          <input
            type="text"
            placeholder="Enter username"
            value={usernameInput}
            onChange={e => setUsernameInput(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleSubmit()}
          />
          <button onClick={handleSubmit}>Start Betting</button>
        </div>
        {error && <div className="error">{error}</div>}
      </div>
    </div>
  );
}

function App() {
  const [games, setGames] = useState<Game[]>([]);
  const [bets, setBets] = useState<Bet[]>([]);
  const [balance, setBalance] = useState<string | null>(null);
  const [userId, setUserId] = useState(USER_ID);
  const [selectedGame, setSelectedGame] = useState<Game | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.getGames().then(setGames).catch(console.error);
  }, []);

  useEffect(() => {
    if (userId) {
      localStorage.setItem('userId', userId);
      api.getUserBalance(userId).then(data => setBalance(data.balance)).catch(console.error);
      api.getUserBets(userId).then(setBets).catch(console.error);
    }
  }, [userId]);

  const handlePlaceBet = async (betType: string, selection: string, stake: string) => {
    if (!selectedGame || !userId) return;
    try {
      setError(null);
      await api.placeBet(userId, selectedGame.id, betType as Parameters<typeof api.placeBet>[2], selection as Parameters<typeof api.placeBet>[3], stake);
      setSelectedGame(null);
      const [newBalance, newBets] = await Promise.all([
        api.getUserBalance(userId),
        api.getUserBets(userId),
      ]);
      setBalance(newBalance.balance);
      setBets(newBets);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      }
    }
  };

  const handleLogin = async (username: string) => {
    try {
      const user = await api.createUser(username);
      setUserId(user.id);
      setError(null);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      }
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('userId');
    setUserId('');
    setBalance(null);
    setBets([]);
  };

  if (!userId) {
    return <LoginPage onLogin={handleLogin} error={error} />;
  }

  return (
    <BrowserRouter>
      {error && <div className="global-error">{error}</div>}

      <Routes>
        <Route element={<Layout balance={balance} onLogout={handleLogout} />}>
          <Route path="/" element={<GamesPage games={games} onPlaceBet={setSelectedGame} />} />
          <Route path="/bets" element={<BetsPage bets={bets} games={games} />} />
        </Route>
      </Routes>

      {selectedGame && (
        <BetModal
          game={selectedGame}
          onClose={() => setSelectedGame(null)}
          onSubmit={handlePlaceBet}
        />
      )}
    </BrowserRouter>
  );
}

export default App;
