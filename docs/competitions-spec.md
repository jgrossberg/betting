# Competitions Feature Spec

## Overview

Competitions allow groups of friends to compete against each other in betting performance over a defined period. Since all bets carry negative EV (house edge), the accumulated "rake" is pooled and redistributed as prizes.

---

## Core Problems to Solve

### 1. Everyone Eventually Goes Broke
With negative EV on every bet, all users will eventually lose their entire balance. Need mechanisms to keep the game going:

**Options:**
- **Daily/Weekly credits** - Auto-replenish X credits on a schedule
- **Minimum balance refill** - When balance drops below threshold (e.g., $10), auto-refill to starting amount
- **Season reset** - Everyone starts fresh at beginning of each season/competition
- **Earn through engagement** - Bonus credits for daily logins, placing bets, streaks
- **Request refill** - Manual "rebuy" button (maybe limited per week)

**Recommendation:** Combine minimum balance refill (keeps people playing) with season resets (clean slate for competitions).

### 💡 XP System - "Win or Learn"
Lost bets convert to XP based on stake amount. You either win money or gain experience.

**How it works:**
- **Win:** Receive payout as normal
- **Lose:** Stake converts to XP (e.g., $50 stake → 50 XP)
- **Push:** Stake returned, no XP

**XP Redemption:**
- Convert XP back to credits at some rate (e.g., 100 XP = $10)
- Creates a floor - you can never truly go broke
- Rewards volume/engagement even during losing streaks

**XP Multipliers (optional):**
- Underdog wins: 1.5x XP bonus
- Streak bonuses: Consecutive bets = multiplier
- Competition participation: Bonus XP for being in active competition

**Data Model:**
```
User (add fields):
+ xp_balance: int            # Current XP
+ xp_lifetime: int           # All-time XP earned

XPTransaction:
  id: UUID
  user_id: UUID
  amount: int
  type: enum (BET_LOSS, REDEMPTION, BONUS, MULTIPLIER)
  source_bet_id: UUID        # nullable - links to bet if from loss
  created_at: datetime
```

This elegantly solves the "everyone goes broke" problem while reinforcing the learning aspect of the platform.

**XP Uses:**
1. **Redeem for credits** - 100 XP → $10 playable balance
2. **Sabotage bets** - Place bets on opponent's behalf (see below)
3. **Power-ups** - Unlock boosts, streak shields, etc. (future)

### 🎯 Sabotage Bets (Competition Feature)
In H2H competitions, spend XP to place bets using your opponent's money.

**How it works:**
- Costs XP to place (e.g., 50 XP → force a $5 bet)
- Bet uses opponent's balance, not yours
- Opponent sees the bet tagged as "Sabotage" + who did it
- Win/loss affects opponent's P/L normally

**Strategy implications:**
- Force opponent onto heavy favorites (low upside)
- Make them take the other side of a game you like
- Drain their balance on -EV longshots
- Timing matters - use before game locks

**Limits & Balance:**
- Max sabotage bets per opponent per week (e.g., 2-3)
- Minimum opponent balance required (can't bankrupt someone with sabotage)
- Maybe opponent can "block" with their own XP spend?

**Data Model:**
```
SabotageBet:
  id: UUID
  competition_id: UUID
  placed_by_user_id: UUID    # Who spent the XP
  target_user_id: UUID       # Whose money is on the line
  bet_id: UUID               # The actual bet created
  xp_cost: int
  created_at: datetime
```

This adds a whole psychological warfare layer to H2H competitions.

### 2. House Money Not Tracked
Currently we don't track the rake/vig the house collects. Need this for:
- Prize pool accumulation
- Analytics (how much edge are we simulating?)
- Leaderboards that account for volume

**Implementation:**
- Calculate rake on each bet at placement time
- Store `house_rake` field on Bet model
- Accumulate into Competition prize_pool (or global pool)
- Track per-user rake contributed for volume-based rewards

---

## Competition Types

### Season League
- Runs for an entire NBA season (or custom date range)
- Leaderboard ranked by net P/L
- Winner takes the prize pool or tiered payouts (1st/2nd/3rd)

### Weekly H2H
- Head-to-head matchups each week
- Bracket or round-robin format
- Winner determined by weekly P/L
- Playoffs at end of season

## Data Models

### Bet (existing - add fields)
```
+ house_rake: decimal        # Calculated vig on this bet
+ competition_id: UUID       # Optional - if bet is part of a competition
```

### HouseAccount (global tracking)
```
id: UUID
total_rake: decimal          # All-time accumulated rake
period_rake: decimal         # Current period (reset weekly/monthly)
last_reset_at: datetime
```

### Competition
```
id: UUID
name: string
type: enum (SEASON_LEAGUE, WEEKLY_H2H)
created_by: UUID (user_id)
start_date: datetime
end_date: datetime
status: enum (PENDING, ACTIVE, COMPLETED)
prize_pool: decimal (accumulated house rake)
created_at: datetime
updated_at: datetime
```

### CompetitionMember
```
id: UUID
competition_id: UUID
user_id: UUID
joined_at: datetime
starting_balance: decimal (snapshot at join)
```

### CompetitionWeek
For H2H format - defines weekly matchups
```
id: UUID
competition_id: UUID
week_number: int
start_date: datetime
end_date: datetime
```

### WeeklyMatchup
```
id: UUID
competition_week_id: UUID
user_1_id: UUID
user_2_id: UUID
winner_id: UUID (nullable, set when week ends)
user_1_pl: decimal
user_2_pl: decimal
```

### CompetitionSnapshot
Weekly/periodic snapshots of member standings
```
id: UUID
competition_id: UUID
user_id: UUID
snapshot_date: datetime
balance: decimal
net_pl: decimal
total_staked: decimal
total_bets: int
win_count: int
loss_count: int
```

## House Rake & Prize Pool

### How It Works
1. Every bet placed has built-in vig (e.g., -110 odds on both sides)
2. Calculate theoretical house edge on each bet
3. Accumulate rake into competition's prize_pool
4. Redistribute at competition end (or weekly)

### Rake Calculation
For standard -110/-110 lines:
- True probability: 50% each side
- Implied probability at -110: 52.4%
- House edge: ~4.5% per bet
- Rake per bet = stake × 0.045 (approximately)

### Prize Distribution Options
1. **Winner takes all** - 100% to first place
2. **Tiered** - 60/30/10 to top 3
3. **Volume bonus** - Percentage to highest volume staker
4. **Weekly prizes** - Distribute rake each week

## API Endpoints

### Competitions
- `POST /competitions` - Create competition
- `GET /competitions` - List user's competitions
- `GET /competitions/{id}` - Competition details + leaderboard
- `POST /competitions/{id}/join` - Join a competition
- `POST /competitions/{id}/invite` - Invite users (generates invite code)
- `GET /competitions/{id}/standings` - Current standings
- `GET /competitions/{id}/weeks` - Weekly breakdown (H2H)

### Admin
- `POST /admin/competitions/{id}/advance-week` - Process weekly H2H matchups
- `POST /admin/competitions/{id}/finalize` - End competition, distribute prizes

## Frontend Views

### Competition Lobby
- List of active competitions
- Create new competition
- Join via invite code

### Competition Dashboard
- Leaderboard with P/L, record, volume
- Prize pool tracker
- Weekly matchup bracket (H2H mode)
- Member activity feed

### My Competition Stats
- Personal performance vs group
- Week-over-week trends
- Head-to-head record

## Future Considerations

1. **Entry fees** - Members contribute to prize pool on join
2. **Private/Public** - Public competitions anyone can join
3. **Achievements** - Badges for streaks, upsets, etc.
4. **Chat/Trash talk** - Social features within competition
5. **Pick visibility** - Option to hide/reveal picks in real-time or after lock
6. **Survivor pools** - Eliminate lowest performer each week
7. **Best bet contests** - One pick per day/week, highest confidence
