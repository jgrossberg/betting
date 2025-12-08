# Analytics & Stats Feature Spec

## Overview

BetLab is a laboratory - data and analysis should be core to the experience. Two main analytics areas:

1. **Pre-Bet Insights** - Contextual stats shown before placing a bet
2. **Personal History Analysis** - How am I performing across different slices?

Both reinforce the "learning" aspect and help users make more informed decisions (or at least understand their tendencies).

---

## Pre-Bet Insights (The Lab)

Stats and trends shown on game cards or in the bet modal to inform decisions.

### Team Performance Stats

**Against the Spread (ATS):**
- Season ATS record (e.g., "Lakers: 15-22 ATS")
- Last 10 games ATS
- Home/Away ATS splits
- ATS as favorite vs underdog

**Over/Under (Totals):**
- Season O/U record
- Last 10 games O/U
- Pace trends (are they playing faster/slower lately?)

**Moneyline:**
- Straight up record
- Record as favorite / underdog
- Upset rate

### Situational Stats

**Recency:**
- Last 5/10 game trends
- Current streak (W/L, ATS, O/U)
- Back-to-back performance

**Head-to-Head:**
- Season series record
- H2H ATS history
- Average margin in matchup

**Rest & Schedule:**
- Days rest for each team
- Travel considerations
- Schedule spot (easy/hard stretch)

### Data Model

```
TeamStats (refreshed daily):
  id: UUID
  team_name: string
  season: string

  # Straight up
  wins: int
  losses: int
  home_wins: int
  home_losses: int
  away_wins: int
  away_losses: int

  # ATS
  ats_wins: int
  ats_losses: int
  ats_pushes: int
  ats_wins_home: int
  ats_losses_home: int
  ats_wins_away: int
  ats_losses_away: int
  ats_wins_as_favorite: int
  ats_losses_as_favorite: int
  ats_wins_as_underdog: int
  ats_losses_as_underdog: int

  # Over/Under
  overs: int
  unders: int
  ou_pushes: int

  # Recent form (last 10)
  last10_ats_wins: int
  last10_ats_losses: int
  last10_overs: int
  last10_unders: int
  current_streak: string       # e.g., "W3", "L2", "3-2 ATS"

  updated_at: datetime
```

### UI Placement

**Game Card (subtle):**
- Small badges: "LAL 5-2 ATS L7"
- Trend indicators: 🔥 hot, 🧊 cold

**Bet Modal (detailed):**
- Expandable "Insights" section
- Key stats for selected bet type
- Comparison between teams

---

## Personal History Analysis

Help users understand their own betting patterns and performance.

### Performance Breakdowns

**By Team:**
- Record betting on/against each team
- P/L per team
- "Your best team: Celtics (8-2, +$145)"
- "Your worst team: Lakers (2-9, -$230)"

**By Bet Type:**
- Moneyline vs Spread vs O/U performance
- Which bet type is most profitable for you?

**By Odds Range:**
- Performance on favorites vs underdogs
- Heavy favorites (-300+) vs slight favorites
- P/L by odds bucket

**By Time/Day:**
- Day of week performance
- Early games vs late games
- Weekday vs weekend

**By Stake Size:**
- Performance on small vs large bets
- Are you better with confident (large) bets?

### Trends & Patterns

**Streaks:**
- Current streak
- Longest win/loss streak
- Streak patterns (do you chase after losses?)

**Recency:**
- Last 7 days performance
- Last 30 days vs season
- Trending up or down?

**Behavioral:**
- Average bets per day
- Favorite bet type
- Time of day you usually bet
- Do you bet more after wins or losses?

### Data Model

Most of this can be derived from existing Bet data, but some aggregations are worth caching:

```
UserBettingStats (refreshed on bet settlement):
  id: UUID
  user_id: UUID

  # Overall
  total_bets: int
  total_wins: int
  total_losses: int
  total_pushes: int
  total_staked: decimal
  total_pnl: decimal

  # By bet type
  moneyline_record: json      # {wins: x, losses: y, pnl: z}
  spread_record: json
  over_under_record: json

  # By team (top performers)
  best_teams: json            # [{team, record, pnl}, ...]
  worst_teams: json

  # Streaks
  current_streak: int         # positive = wins, negative = losses
  longest_win_streak: int
  longest_loss_streak: int

  updated_at: datetime

UserTeamStats (per team performance):
  id: UUID
  user_id: UUID
  team_name: string
  bets_for: int               # Betting on this team
  bets_against: int           # Betting against this team
  wins_for: int
  losses_for: int
  wins_against: int
  losses_against: int
  pnl_for: decimal
  pnl_against: decimal
```

### UI Views

**Stats Dashboard:**
- Summary cards: Record, P/L, ROI, Best/Worst teams
- Charts: P/L over time, performance by bet type
- Recent trends

**Team Lookup:**
- Search/select team
- Your history with that team
- Team's current form

**Bet History Filters:**
- Filter by team, bet type, date range, outcome
- Sortable columns
- Export to CSV?

---

## API Endpoints

### Pre-Bet Insights
- `GET /teams/{team}/stats` - Team performance stats
- `GET /games/{game_id}/insights` - Matchup-specific insights
- `GET /teams/{team}/trends` - Recent form and streaks

### Personal Analytics
- `GET /users/{user_id}/stats` - Overall betting stats
- `GET /users/{user_id}/stats/teams` - Per-team breakdown
- `GET /users/{user_id}/stats/trends` - Performance over time
- `GET /users/{user_id}/stats/patterns` - Behavioral patterns

---

## Data Sources

### Team Stats
- **Primary:** Derive from our own completed games data
- **Enhancement:** External API for deeper stats (basketball-reference, etc.)
- **Refresh:** Daily job after games complete

### Personal Stats
- **Source:** Our Bet table
- **Refresh:** On bet settlement or periodic rollup

---

## Future Ideas

1. **Predictions/Picks** - ML model suggesting bets based on trends
2. **Alerts** - "Lakers playing tonight, you're 8-2 on them!"
3. **Comparisons** - How do your stats compare to other users?
4. **Achievements** - Badges for hitting milestones (10 wins on underdogs, etc.)
5. **Betting journal** - Add notes to bets, review reasoning later
6. **Fade yourself** - Show what your record would be if you bet the opposite
