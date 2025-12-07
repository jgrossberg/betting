import type { Game, Bet } from '../api';
import './HistoryPage.css';

interface HistoryPageProps {
  bets: Bet[];
  games: Game[];
}

function formatOdds(odds: string | null): string {
  if (!odds) return '-';
  const num = parseFloat(odds);
  return num > 0 ? `+${num}` : `${num}`;
}

function formatDate(dateStr: string): string {
  const date = new Date(dateStr);
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
  });
}

export function HistoryPage({ bets, games }: HistoryPageProps) {
  const settledBets = bets
    .filter(b => b.status !== 'pending')
    .sort((a, b) => {
      // Sort by settled_at descending (most recent first)
      if (!a.settled_at || !b.settled_at) return 0;
      return new Date(b.settled_at).getTime() - new Date(a.settled_at).getTime();
    });

  const getGame = (gameId: string) => games.find(g => g.id === gameId);

  const totalStaked = settledBets.reduce((sum, b) => sum + parseFloat(b.stake), 0);
  const totalReturns = settledBets.reduce((sum, b) => {
    if (b.status === 'won') return sum + parseFloat(b.potential_payout);
    if (b.status === 'push') return sum + parseFloat(b.stake);
    return sum;
  }, 0);
  const netProfit = totalReturns - totalStaked;
  const winCount = settledBets.filter(b => b.status === 'won').length;
  const lossCount = settledBets.filter(b => b.status === 'lost').length;

  return (
    <div className="page history-page">
      <h2 className="page-title">Bet History</h2>

      <div className="stats-bar">
        <div className="stat">
          <span className="stat-label">Record</span>
          <span className="stat-value">{winCount}W - {lossCount}L</span>
        </div>
        <div className="stat">
          <span className="stat-label">Staked</span>
          <span className="stat-value">${totalStaked.toFixed(2)}</span>
        </div>
        <div className="stat">
          <span className="stat-label">Net P/L</span>
          <span className={`stat-value ${netProfit >= 0 ? 'positive' : 'negative'}`}>
            {netProfit >= 0 ? '+' : ''}${netProfit.toFixed(2)}
          </span>
        </div>
      </div>

      {settledBets.length === 0 ? (
        <p className="empty-state">No settled bets yet</p>
      ) : (
        <div className="history-table-wrapper">
          <table className="history-table">
            <thead>
              <tr>
                <th>Date</th>
                <th>Game</th>
                <th>Type</th>
                <th>Pick</th>
                <th>Odds</th>
                <th>Stake</th>
                <th>To Win</th>
                <th>Result</th>
              </tr>
            </thead>
            <tbody>
              {settledBets.map(bet => {
                const game = getGame(bet.game_id);
                return (
                  <tr key={bet.id} className={bet.status}>
                    <td className="date-cell">
                      {bet.settled_at ? formatDate(bet.settled_at) : '-'}
                    </td>
                    <td className="game-cell">
                      {game ? `${game.away_team} @ ${game.home_team}` : 'Unknown'}
                    </td>
                    <td className="type-cell">{bet.bet_type.replace('_', '/')}</td>
                    <td className="pick-cell">{bet.selection}</td>
                    <td className="odds-cell">{formatOdds(bet.odds)}</td>
                    <td className="stake-cell">${bet.stake}</td>
                    <td className="payout-cell">${bet.potential_payout}</td>
                    <td className={`result-cell ${bet.status}`}>
                      {bet.status.toUpperCase()}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
