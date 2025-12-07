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

export function BetsPage({ bets, games }: BetsPageProps) {
  const pendingBets = bets.filter(b => b.status === 'pending');
  const settledBets = bets.filter(b => b.status !== 'pending');

  return (
    <div className="page">
      <h2 className="page-title">My Bets</h2>

      {pendingBets.length > 0 && (
        <section className="bets-section">
          <h3 className="section-title">Pending ({pendingBets.length})</h3>
          <div className="bets-list">
            {pendingBets.map(bet => (
              <BetCard key={bet.id} bet={bet} games={games} />
            ))}
          </div>
        </section>
      )}

      {settledBets.length > 0 && (
        <section className="bets-section">
          <h3 className="section-title">Settled ({settledBets.length})</h3>
          <div className="bets-list">
            {settledBets.map(bet => (
              <BetCard key={bet.id} bet={bet} games={games} />
            ))}
          </div>
        </section>
      )}

      {bets.length === 0 && (
        <p className="empty-state">No bets yet. Go place some!</p>
      )}
    </div>
  );
}
