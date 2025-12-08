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
  const isLocked = new Date(game.commence_time) < new Date();
  const displayStatus = isLocked && game.status === 'upcoming' ? 'locked' : game.status;

  return (
    <div className="game-card">
      <div className="game-header">
        <span className="game-time">{formatDate(game.commence_time)}</span>
        <span className={`game-status ${displayStatus}`}>{displayStatus}</span>
      </div>
      <table className="game-table">
        <thead>
          <tr>
            <th className="col-team">Team</th>
            <th>Spread</th>
            <th>Money</th>
            <th>O/U {game.total_points}</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td className="team-cell">
              <span className="team-name">{game.away_team}</span>
              {game.away_score !== null && <span className="score">{game.away_score}</span>}
            </td>
            <td className="odds-cell">{game.away_spread} ({formatOdds(game.away_spread_odds)})</td>
            <td className="odds-cell">{formatOdds(game.away_moneyline)}</td>
            <td className="odds-cell">O {formatOdds(game.over_odds)}</td>
          </tr>
          <tr>
            <td className="team-cell">
              <span className="team-name">{game.home_team}</span>
              {game.home_score !== null && <span className="score">{game.home_score}</span>}
            </td>
            <td className="odds-cell">{game.home_spread} ({formatOdds(game.home_spread_odds)})</td>
            <td className="odds-cell">{formatOdds(game.home_moneyline)}</td>
            <td className="odds-cell">U {formatOdds(game.under_odds)}</td>
          </tr>
        </tbody>
      </table>
      {game.status === 'upcoming' && (
        <button
          className={`bet-button ${isLocked ? 'disabled' : ''}`}
          onClick={() => !isLocked && onPlaceBet(game)}
          disabled={isLocked}
        >
          {isLocked ? 'Locked' : 'Place Bet'}
        </button>
      )}
    </div>
  );
}

export function GamesPage({ games, onPlaceBet }: GamesPageProps) {
  const upcomingGames = games.filter(g => g.status === 'upcoming');
  const sortedGames = [...upcomingGames].sort(
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
