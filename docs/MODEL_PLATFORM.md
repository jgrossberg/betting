# BetLab Model Testing Platform

A platform for testing AI/ML sports betting models against real odds without financial risk.

## Vision

Enable quants, ML engineers, and hobbyists to:
- Test betting strategies against real, live odds
- Track performance with professional-grade analytics
- Iterate quickly without risking real money
- Benchmark against other models (opt-in leaderboard)

## Target Users

1. **ML practitioners** - Training models on sports data, want realistic paper trading
2. **Agentic AI builders** - Building autonomous betting agents (Claude, GPT, custom)
3. **Quants** - Testing strategies before deploying capital
4. **Hobbyists** - Sports fans who want to test their intuition systematically

---

## API Design

### Authentication

Replace `?user_id=` with proper API keys:

```
POST /api-keys
Authorization: Bearer <user_token>

Response: { "api_key": "fb_live_abc123...", "created_at": "..." }
```

All model endpoints use header auth:
```
GET /games
X-API-Key: fb_live_abc123...
```

### Core Endpoints (Updated)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/games` | Current games with odds |
| GET | `/games/history` | Historical games with results |
| GET | `/odds/snapshots?game_id=X` | Line movement history |
| POST | `/bets` | Place single bet |
| POST | `/bets/bulk` | Place multiple bets |
| GET | `/portfolios` | List user's portfolios |
| POST | `/portfolios` | Create new portfolio |
| GET | `/portfolios/{id}/performance` | Analytics for portfolio |
| GET | `/portfolios/{id}/bets` | Bet history for portfolio |

### Portfolios

Users can create multiple portfolios to test different strategies:

```
POST /portfolios
{
  "name": "Conservative ML v2",
  "starting_balance": "10000.00"
}
```

Each portfolio has isolated balance and bet history. Compare strategies side-by-side.

### Historical Data

For backtesting, expose completed games with their odds at different points:

```
GET /games/history?sport=basketball_nba&from=2024-01-01&to=2024-06-01

Response: [
  {
    "id": "...",
    "home_team": "Lakers",
    "away_team": "Celtics",
    "commence_time": "2024-01-15T19:00:00Z",
    "home_score": 112,
    "away_score": 108,
    "odds_snapshots": [
      { "captured_at": "2024-01-14T12:00:00Z", "home_moneyline": -150, ... },
      { "captured_at": "2024-01-15T10:00:00Z", "home_moneyline": -145, ... }
    ]
  }
]
```

### Odds Snapshots

Track line movements. Smart models exploit stale lines.

New table: `odds_snapshots`
- game_id, captured_at, home_moneyline, away_moneyline, spread, total, bookmaker

Capture odds every time `fetch-games` runs, not just latest.

### Bulk Betting

For models that analyze many games at once:

```
POST /bets/bulk
{
  "portfolio_id": "...",
  "bets": [
    { "game_id": "...", "bet_type": "moneyline", "selection": "home", "stake": "100" },
    { "game_id": "...", "bet_type": "spread", "selection": "away", "stake": "50" }
  ]
}
```

Returns array of created bets (or errors for invalid ones).

### Webhooks

Let models react to settlements without polling:

```
POST /webhooks
{
  "url": "https://my-model.example.com/settlement",
  "events": ["bet.settled", "game.completed"]
}
```

Payload:
```
{
  "event": "bet.settled",
  "data": {
    "bet_id": "...",
    "status": "won",
    "payout": "250.00",
    "portfolio_id": "..."
  }
}
```

---

## Analytics

### Portfolio Performance Endpoint

```
GET /portfolios/{id}/performance

Response: {
  "total_bets": 247,
  "record": { "won": 134, "lost": 108, "push": 5 },
  "win_rate": 0.553,
  "roi": 0.087,
  "total_staked": "24700.00",
  "total_returned": "26848.00",
  "net_profit": "2148.00",
  "sharpe_ratio": 1.42,
  "max_drawdown": 0.12,
  "breakdown": {
    "by_bet_type": {
      "moneyline": { "count": 100, "roi": 0.05 },
      "spread": { "count": 97, "roi": 0.12 },
      "total": { "count": 50, "roi": 0.08 }
    },
    "by_sport": {
      "basketball_nba": { "count": 200, "roi": 0.09 },
      "football_nfl": { "count": 47, "roi": 0.06 }
    },
    "by_month": [
      { "month": "2024-01", "bets": 45, "roi": 0.11 },
      { "month": "2024-02", "bets": 52, "roi": 0.03 }
    ]
  }
}
```

### Metrics to Track

- **ROI** - (returns - stakes) / stakes
- **Win Rate** - wins / (wins + losses)
- **Sharpe Ratio** - risk-adjusted returns
- **Max Drawdown** - largest peak-to-trough decline
- **CLV (Closing Line Value)** - did you beat the closing line?
- **Bet Size Efficiency** - Kelly criterion analysis

---

## Rate Limiting

Per API key limits:

| Tier | Requests/min | Bulk bets/request |
|------|--------------|-------------------|
| Free | 60 | 10 |
| Pro | 300 | 100 |

Headers on every response:
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1699574400
```

---

## Optional: MCP Server

For Claude-based agents, offer an MCP server:

```json
{
  "mcpServers": {
    "betlab": {
      "command": "npx",
      "args": ["@betlab/mcp-server"],
      "env": { "BETLAB_API_KEY": "fb_live_..." }
    }
  }
}
```

Tools exposed:
- `get_games` - Fetch current games with odds
- `place_bet` - Place a bet
- `get_portfolio_performance` - Check how the model is doing
- `get_bet_history` - Review past bets

This lets Claude agents bet conversationally while using the same backend API.

---

## Database Changes

### New Tables

```sql
-- API keys
CREATE TABLE api_keys (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  key_hash VARCHAR(64) NOT NULL,  -- store hashed, not plaintext
  name VARCHAR(100),
  created_at TIMESTAMP DEFAULT NOW(),
  last_used_at TIMESTAMP,
  revoked_at TIMESTAMP
);

-- Portfolios
CREATE TABLE portfolios (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  name VARCHAR(100) NOT NULL,
  balance DECIMAL(12,2) DEFAULT 10000.00,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Update bets table
ALTER TABLE bets ADD COLUMN portfolio_id UUID REFERENCES portfolios(id);

-- Odds snapshots
CREATE TABLE odds_snapshots (
  id UUID PRIMARY KEY,
  game_id UUID REFERENCES games(id),
  captured_at TIMESTAMP NOT NULL,
  bookmaker VARCHAR(50),
  home_moneyline INTEGER,
  away_moneyline INTEGER,
  home_spread DECIMAL(4,1),
  away_spread DECIMAL(4,1),
  spread_home_price INTEGER,
  spread_away_price INTEGER,
  total_points DECIMAL(5,1),
  over_price INTEGER,
  under_price INTEGER
);

-- Webhooks
CREATE TABLE webhooks (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  url VARCHAR(500) NOT NULL,
  events VARCHAR(50)[] NOT NULL,
  secret VARCHAR(64),  -- for signature verification
  created_at TIMESTAMP DEFAULT NOW(),
  active BOOLEAN DEFAULT TRUE
);
```

---

## Implementation Phases

### Phase 1: Foundation
- [ ] API key authentication
- [ ] Portfolios (multi-strategy support)
- [ ] Update bet placement to use portfolios

### Phase 2: Data
- [ ] Odds snapshots (capture on every fetch)
- [ ] Historical games endpoint
- [ ] Basic performance analytics

### Phase 3: Scale
- [ ] Bulk betting endpoint
- [ ] Rate limiting
- [ ] Webhooks

### Phase 4: Polish
- [ ] Advanced analytics (Sharpe, drawdown, CLV)
- [ ] OpenAPI spec + SDK generation
- [ ] MCP server for Claude agents
- [ ] Leaderboard (opt-in)

---

## Competitive Positioning

| Platform | Real Odds | Free | API-First | Model Analytics |
|----------|-----------|------|-----------|-----------------|
| BetLab | Yes | Yes | Yes | Yes |
| Paper trading apps | Some | Yes | No | No |
| Real sportsbooks | Yes | No | Limited | No |
| Backtesting tools | Historical only | Varies | Yes | Some |

BetLab's niche: **Real-time paper trading with an API built for AI agents.**
