# Competitions Feature Spec

## Overview

Competitions let friends compete on betting performance. The core loop: create a challenge, place bets within the challenge window, whoever profits most wins. Losing bets generate XP, which can be redeemed for strategic advantages.

---

## MVP: Challenges

### How It Works

1. **Create a Challenge** - Pick a duration (1 day or 1 week)
2. **Eligible Games** - Any game with `commence_time` within the challenge window
3. **Place Bets** - Tag bets to the challenge (untagged bets = season grind)
4. **Winner** - Highest net profit when challenge ends
5. **Tiebreaker** - Longest odds winning bet

### Challenge Rules

- **Open join** - Anyone can join at any time during the challenge
- **No buy-in** - Pure competition on skill/picks
- **Multi-player** - Not limited to 1v1, can be H2H2H2H...
- **Winner takes all** - Bragging rights to #1

### Data Model

```
Challenge:
  id: UUID
  name: string
  created_by: UUID (user_id)
  duration_type: enum (DAY, WEEK)
  start_date: datetime
  end_date: datetime
  status: enum (OPEN, ACTIVE, COMPLETED)
  winner_id: UUID (nullable, set when challenge ends)
  created_at: datetime
  updated_at: datetime
```

```
ChallengeParticipant:
  id: UUID
  challenge_id: UUID
  user_id: UUID
  joined_at: datetime
  net_profit: decimal (calculated/cached)
  total_bets: int
  wins: int
  losses: int
```

```
Bet (add field):
  + challenge_id: UUID (nullable - if part of a challenge)
```

---

## XP System - "Win or Learn"

You either win money or gain experience. Never both.

### How It Works

- **Win** - Receive payout as normal, no XP
- **Lose** - Stake converts to XP (e.g., $100 stake → 100 XP)
- **Push** - Stake returned, no XP

### Why This Matters

- Creates comeback opportunities without rewarding losing
- Strategic depth in choosing chip conversion vs betting advantages
- 75% conversion rate maintains competitiveness
- Losing still stings, but you're building toward something

### Data Model

```
User (add fields):
  + xp_balance: int           # Current spendable XP
  + xp_lifetime: int          # All-time XP earned
```

```
XPTransaction:
  id: UUID
  user_id: UUID
  amount: int                 # Positive = earned, negative = spent
  type: enum (BET_LOSS, CHIP_CONVERSION, ADVANTAGE_PURCHASE)
  source_bet_id: UUID         # Nullable - links to bet if from loss
  description: string         # Human-readable note
  created_at: datetime
```

---

## XP Advantages

Spend XP on strategic advantages instead of converting to chips.

| Advantage | Description | XP Cost (TBD) |
|-----------|-------------|---------------|
| **Chip Conversion** | Convert XP to playable dollars at 75% rate | N/A (rate-based) |
| **Buy Points** | Adjust spread/total by 0.5-2 points on a bet | TBD |
| **Reduced Vig** | Get -105 instead of -110 on a bet | TBD |
| **Bad Beat Insurance** | Partial refund if you lose by < 1 point | TBD |
| **Teasers** | Move lines on 2+ legs (reduced payout) | TBD |
| **Line Lock** | Lock current line, place bet later | TBD |

### Chip Conversion

```
Convert XP → Playable Dollars at 75% rate
Example: 100 XP → $75 added to balance
```

### Advantage Details (Future Implementation)

**Buy Points:**
- Move spread or total by 0.5 to 2 points
- Cost scales with points bought
- Must be applied at bet placement

**Reduced Vig:**
- Single bet gets -105 odds instead of -110
- One-time use per bet

**Bad Beat Insurance:**
- If bet loses by margin < 1 point (covers the hook)
- Refund 50% of stake as XP or credits

**Teasers:**
- Combine 2+ bets with adjusted lines
- Each leg moves 6 points (NFL) or 4 points (NBA)
- All legs must hit

**Line Lock:**
- Snapshot current line for a game
- Place bet later using locked line
- Expires at game start

---

## API Endpoints

### Challenges

```
POST   /challenges              # Create a challenge
GET    /challenges              # List challenges (filter: mine, open, completed)
GET    /challenges/:id          # Challenge details + leaderboard
POST   /challenges/:id/join     # Join a challenge
GET    /challenges/:id/bets     # All bets in this challenge
```

### XP

```
GET    /users/:id/xp            # XP balance and history
POST   /xp/convert              # Convert XP to chips (75% rate)
POST   /xp/purchase-advantage   # Buy an advantage (future)
```

### Bets (modify existing)

```
POST   /bets                    # Add optional challenge_id field
```

---

## Frontend Views

### Challenge Lobby
- List of open challenges to join
- Create new challenge button
- Filter: My Challenges, Open, Completed

### Challenge Detail
- Leaderboard (profit, bets, win rate)
- Time remaining
- Eligible games list
- Quick bet placement

### XP Dashboard
- Current balance
- Transaction history
- Conversion calculator
- Available advantages (future)

---

## Future: Leagues

Structured season-long competition with weekly H2H matchups.

### How It Works (Stubbed)

- Season runs for defined period (e.g., NFL season)
- Each week, participants are matched H2H
- Weekly winner gets a "win" in standings
- End of season: playoffs or best record wins

### Data Model (Stubbed)

```
League:
  id: UUID
  name: string
  season_start: datetime
  season_end: datetime
  status: enum (PENDING, ACTIVE, COMPLETED)
```

```
LeagueMember:
  id: UUID
  league_id: UUID
  user_id: UUID
  wins: int
  losses: int
```

```
LeagueWeek:
  id: UUID
  league_id: UUID
  week_number: int
  start_date: datetime
  end_date: datetime
```

```
LeagueMatchup:
  id: UUID
  league_week_id: UUID
  user_1_id: UUID
  user_2_id: UUID
  user_1_profit: decimal
  user_2_profit: decimal
  winner_id: UUID (nullable)
```

### Future Features
- Podium recognition (1st/2nd/3rd)
- H2H matrix (everyone plays everyone)
- Playoff brackets
- Division/conference structure

---

## Implementation Order

1. **Challenge CRUD** - Create, join, list challenges
2. **Bet tagging** - Add challenge_id to bets
3. **Leaderboard** - Calculate standings from tagged bets
4. **Challenge completion** - Auto-determine winner at end_date
5. **XP generation** - Award XP on losing bets
6. **XP conversion** - Convert to chips at 75%
7. **XP advantages** - Individual advantage implementations
8. **Leagues** - Season structure with weekly matchups
