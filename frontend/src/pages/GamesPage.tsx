import type { Game } from '../api';

interface GamesPageProps {
  games: Game[];
  onPlaceBet: (game: Game) => void;
}

function formatOdds(odds: string | null): string {
  if (!odds) return '-';
  const num = parseFloat(odds);
  return num > 0 ? `+${num}` : `${num}`;
}

function formatDate(dateStr: string): string {
  const date = new Date(dateStr);
  return date.toLocaleString('en-US', {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
    timeZoneName: 'short',
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

export function GamesPage({ games, onPlaceBet }: GamesPageProps) {
  const sortedGames = [...games].sort(
    (a, b) => new Date(a.commence_time).getTime() - new Date(b.commence_time).getTime()
  );

  return (
    <div className="page">
      <h2 className="page-title">Upcoming Games</h2>
      <div className="games-list">
        {sortedGames.length === 0 ? (
          <p className="empty-state">No upcoming games</p>
        ) : (
          sortedGames.map(game => (
            <GameCard key={game.id} game={game} onPlaceBet={onPlaceBet} />
          ))
        )}
      </div>
    </div>
  );
}
