import type { Game, Bet } from '../api';

interface BetsPageProps {
  bets: Bet[];
  games: Game[];
}

function formatOdds(odds: string | null): string {
  if (!odds) return '-';
  const num = parseFloat(odds);
  return num > 0 ? `+${num}` : `${num}`;
}

function formatGameTime(commence_time: string): { relative: string; absolute: string } {
  const gameDate = new Date(commence_time);
  const now = new Date();
  const diffMs = gameDate.getTime() - now.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMins / 60);
  const diffDays = Math.floor(diffHours / 24);

  const timeStr = gameDate.toLocaleTimeString('en-US', {
    hour: 'numeric',
    minute: '2-digit',
    hour12: true
  });

  let relative: string;
  if (diffMs < 0) {
    relative = 'In Progress';
  } else if (diffMins < 60) {
    relative = `${diffMins}m`;
  } else if (diffHours < 24) {
    relative = `${diffHours}h ${diffMins % 60}m`;
  } else if (diffDays === 1) {
    relative = 'Tomorrow';
  } else {
    relative = `${diffDays} days`;
  }

  const isToday = gameDate.toDateString() === now.toDateString();
  const isTomorrow = diffDays === 1;
  const dayStr = isToday ? 'Today' : isTomorrow ? 'Tomorrow' : gameDate.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });

  return { relative, absolute: `${dayStr} @ ${timeStr}` };
}

function getSelectionDisplay(bet: Bet, game: Game | undefined): string {
  if (!game) return bet.selection;

  if (bet.bet_type === 'moneyline') {
    return bet.selection === 'home' ? game.home_team : game.away_team;
  } else if (bet.bet_type === 'spread') {
    const team = bet.selection === 'home' ? game.home_team : game.away_team;
    const spread = bet.selection === 'home' ? game.home_spread : game.away_spread;
    return `${team} ${spread && parseFloat(spread) > 0 ? '+' : ''}${spread}`;
  } else if (bet.bet_type === 'over_under') {
    return `${bet.selection.charAt(0).toUpperCase() + bet.selection.slice(1)} ${game.total_points}`;
  }
  return bet.selection;
}

function getBetTypeLabel(betType: string): string {
  switch (betType) {
    case 'moneyline': return 'ML';
    case 'spread': return 'Spread';
    case 'over_under': return 'O/U';
    default: return betType;
  }
}

function OpenBetCard({ bets, game }: { bets: Bet[]; game: Game | undefined }) {
  const time = game ? formatGameTime(game.commence_time) : null;
  const isStartingSoon = time && (time.relative.includes('m') || time.relative === 'In Progress');

  const totalStake = bets.reduce((sum, b) => sum + parseFloat(b.stake), 0);
  const totalPayout = bets.reduce((sum, b) => sum + parseFloat(b.potential_payout), 0);

  return (
    <div className={`open-bet-card ${isStartingSoon ? 'starting-soon' : ''}`}>
      <div className="open-bet-time">
        {time ? (
          <>
            <span className="time-relative">{time.relative}</span>
            <span className="time-absolute">{time.absolute}</span>
          </>
        ) : (
          <span className="time-absolute">Time unknown</span>
        )}
      </div>

      <div className="open-bet-matchup">
        {game ? `${game.away_team} @ ${game.home_team}` : 'Unknown game'}
      </div>

      <div className="open-bet-picks">
        <div className="picks-header">Your Picks</div>
        <table className="picks-table">
          <thead>
            <tr>
              <th className="col-type">Type</th>
              <th className="col-selection">Selection</th>
              <th className="col-odds">Odds</th>
              <th className="col-stake">Stake</th>
              <th className="col-payout">To Win</th>
            </tr>
          </thead>
          <tbody>
            {bets.map(bet => (
              <tr key={bet.id}>
                <td className="col-type">{getBetTypeLabel(bet.bet_type)}</td>
                <td className="col-selection">{getSelectionDisplay(bet, game)}</td>
                <td className="col-odds">{formatOdds(bet.odds)}</td>
                <td className="col-stake">${bet.stake}</td>
                <td className="col-payout">${bet.potential_payout}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="open-bet-totals">
        <div className="totals-stake">
          <span className="totals-label">Total Risking</span>
          <span className="totals-value">${totalStake.toFixed(2)}</span>
        </div>
        <div className="totals-arrow">→</div>
        <div className="totals-win">
          <span className="totals-label">Total To Win</span>
          <span className="totals-value highlight">${totalPayout.toFixed(2)}</span>
        </div>
      </div>
    </div>
  );
}


export function BetsPage({ bets, games }: BetsPageProps) {
  const pendingBets = bets.filter(b => b.status === 'pending');

  // Group bets by game
  const betsByGame = pendingBets.reduce((acc, bet) => {
    if (!acc[bet.game_id]) {
      acc[bet.game_id] = [];
    }
    acc[bet.game_id].push(bet);
    return acc;
  }, {} as Record<string, Bet[]>);

  // Sort games by commence time (soonest first)
  const sortedGameIds = Object.keys(betsByGame).sort((a, b) => {
    const gameA = games.find(g => g.id === a);
    const gameB = games.find(g => g.id === b);
    if (!gameA || !gameB) return 0;
    return new Date(gameA.commence_time).getTime() - new Date(gameB.commence_time).getTime();
  });

  return (
    <div className="page">
      <h2 className="page-title">Open Bets</h2>
      <div className="open-bets-list">
        {sortedGameIds.length === 0 ? (
          <p className="empty-state">No open bets</p>
        ) : (
          sortedGameIds.map(gameId => (
            <OpenBetCard
              key={gameId}
              bets={betsByGame[gameId]}
              game={games.find(g => g.id === gameId)}
            />
          ))
        )}
      </div>
    </div>
  );
}
