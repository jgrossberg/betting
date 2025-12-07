import { useEffect, useState } from 'react';
import type { Game, Bet } from './api';
import { api } from './api';
import './App.css';

// Hardcode user ID for now - replace with auth later
const USER_ID = localStorage.getItem('userId') || '';

function formatOdds(odds: string | null): string {
  if (!odds) return '-';
  const num = parseFloat(odds);
  return num > 0 ? `+${num}` : `${num}`;
}

function formatDate(dateStr: string): string {
  const date = new Date(dateStr);
  return date.toLocaleDateString('en-US', {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  });
}

function GameCard({ game, onPlaceBet }: { game: Game; onPlaceBet: (game: Game) => void }) {
  return (
    <div className="game-card">
      <div className="game-header">
        <span className="game-time">{formatDate(game.commence_time)}</span>
        <span className={`game-status ${game.status}`}>{game.status}</span>
      </div>
      <div className="game-teams">
        <div className="team">
          <span className="team-name">{game.away_team}</span>
          {game.away_score !== null && <span className="score">{game.away_score}</span>}
        </div>
        <div className="team">
          <span className="team-name">{game.home_team}</span>
          {game.home_score !== null && <span className="score">{game.home_score}</span>}
        </div>
      </div>
      <div className="game-odds">
        <div className="odds-row">
          <span className="odds-label">Moneyline</span>
          <span className="odds-value">{formatOdds(game.away_moneyline)}</span>
          <span className="odds-value">{formatOdds(game.home_moneyline)}</span>
        </div>
        <div className="odds-row">
          <span className="odds-label">Spread</span>
          <span className="odds-value">{game.away_spread} ({formatOdds(game.away_spread_odds)})</span>
          <span className="odds-value">{game.home_spread} ({formatOdds(game.home_spread_odds)})</span>
        </div>
        <div className="odds-row">
          <span className="odds-label">O/U {game.total_points}</span>
          <span className="odds-value">O {formatOdds(game.over_odds)}</span>
          <span className="odds-value">U {formatOdds(game.under_odds)}</span>
        </div>
      </div>
      {game.status === 'upcoming' && (
        <button className="bet-button" onClick={() => onPlaceBet(game)}>
          Place Bet
        </button>
      )}
    </div>
  );
}

function BetCard({ bet, games }: { bet: Bet; games: Game[] }) {
  const game = games.find(g => g.id === bet.game_id);
  return (
    <div className={`bet-card ${bet.status}`}>
      <div className="bet-header">
        <span className="bet-type">{bet.bet_type.replace('_', '/')}</span>
        <span className={`bet-status ${bet.status}`}>{bet.status}</span>
      </div>
      <div className="bet-details">
        <div>{game ? `${game.away_team} @ ${game.home_team}` : 'Unknown game'}</div>
        <div>Selection: {bet.selection}</div>
        <div>Odds: {formatOdds(bet.odds)}</div>
      </div>
      <div className="bet-amounts">
        <span>Stake: ${bet.stake}</span>
        <span>To win: ${bet.potential_payout}</span>
      </div>
    </div>
  );
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
            setBetType(e.target.value as any);
            setSelection(e.target.value === 'over_under' ? 'over' : 'home');
          }}>
            <option value="moneyline">Moneyline</option>
            <option value="spread">Spread</option>
            <option value="over_under">Over/Under</option>
          </select>
        </div>

        <div className="form-group">
          <label>Selection</label>
          <select value={selection} onChange={e => setSelection(e.target.value as any)}>
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

function App() {
  const [games, setGames] = useState<Game[]>([]);
  const [bets, setBets] = useState<Bet[]>([]);
  const [balance, setBalance] = useState<string | null>(null);
  const [userId, setUserId] = useState(USER_ID);
  const [selectedGame, setSelectedGame] = useState<Game | null>(null);
  const [tab, setTab] = useState<'games' | 'bets'>('games');
  const [error, setError] = useState<string | null>(null);
  const [usernameInput, setUsernameInput] = useState('');

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
      await api.placeBet(userId, selectedGame.id, betType as any, selection as any, stake);
      setSelectedGame(null);
      // Refresh data
      const [newBalance, newBets] = await Promise.all([
        api.getUserBalance(userId),
        api.getUserBets(userId),
      ]);
      setBalance(newBalance.balance);
      setBets(newBets);
    } catch (err: any) {
      setError(err.message);
    }
  };

  const handleCreateUser = async () => {
    if (!usernameInput.trim()) return;
    try {
      const user = await api.createUser(usernameInput);
      setUserId(user.id);
      setUsernameInput('');
    } catch (err: any) {
      setError(err.message);
    }
  };

  if (!userId) {
    return (
      <div className="app">
        <h1>NBA Betting</h1>
        <div className="login-form">
          <input
            type="text"
            placeholder="Enter username"
            value={usernameInput}
            onChange={e => setUsernameInput(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleCreateUser()}
          />
          <button onClick={handleCreateUser}>Start Betting</button>
        </div>
        {error && <div className="error">{error}</div>}
      </div>
    );
  }

  return (
    <div className="app">
      <header>
        <h1>NBA Betting</h1>
        <div className="user-info">
          <span>Balance: ${balance || '...'}</span>
        </div>
      </header>

      <nav className="tabs">
        <button className={tab === 'games' ? 'active' : ''} onClick={() => setTab('games')}>
          Games
        </button>
        <button className={tab === 'bets' ? 'active' : ''} onClick={() => setTab('bets')}>
          My Bets ({bets.length})
        </button>
      </nav>

      {error && <div className="error">{error}</div>}

      <main>
        {tab === 'games' && (
          <div className="games-list">
            {games.length === 0 ? (
              <p>No upcoming games</p>
            ) : (
              games.map(game => (
                <GameCard key={game.id} game={game} onPlaceBet={setSelectedGame} />
              ))
            )}
          </div>
        )}

        {tab === 'bets' && (
          <div className="bets-list">
            {bets.length === 0 ? (
              <p>No bets yet</p>
            ) : (
              bets.map(bet => (
                <BetCard key={bet.id} bet={bet} games={games} />
              ))
            )}
          </div>
        )}
      </main>

      {selectedGame && (
        <BetModal
          game={selectedGame}
          onClose={() => setSelectedGame(null)}
          onSubmit={handlePlaceBet}
        />
      )}
    </div>
  );
}

export default App;
