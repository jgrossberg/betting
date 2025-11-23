# NBA Betting CLI Application

A command-line betting application for NBA games with balance tracking.

## Project Structure

```
betting/
├── src/
│   ├── models/          # Database models
│   │   ├── user.py      # User model with balance
│   │   ├── game.py      # Game model with odds
│   │   └── bet.py       # Bet model with status tracking
│   ├── services/        # Business logic (to be implemented)
│   ├── cli/             # CLI interface (to be implemented)
│   ├── database.py      # Database connection and session management
│   └── config.py        # Application configuration
├── init_db.py           # Database initialization script
├── requirements.txt     # Python dependencies
└── .env.example         # Example environment variables
```

## Database Schema

### Users Table
- `id`: Primary key
- `username`: Unique username
- `balance`: Current balance (default: $1000.00)
- `created_at`, `updated_at`: Timestamps

### Games Table
- `id`: Primary key
- `external_id`: Unique ID from odds API
- `home_team`, `away_team`: Team names
- `commence_time`: When the game starts
- `home_moneyline`, `away_moneyline`: Moneyline odds
- `home_spread`, `home_spread_odds`: Home spread and odds
- `away_spread`, `away_spread_odds`: Away spread and odds
- `total_points`, `over_odds`, `under_odds`: Totals betting
- `home_score`, `away_score`: Final scores (null until complete)
- `status`: UPCOMING, IN_PROGRESS, or COMPLETED
- `created_at`, `updated_at`: Timestamps

### Bets Table
- `id`: Primary key
- `user_id`: Foreign key to users
- `game_id`: Foreign key to games
- `bet_type`: MONEYLINE, SPREAD, or OVER_UNDER
- `selection`: "home", "away", "over", or "under"
- `odds`: American odds at time of bet
- `stake`: Amount wagered
- `potential_payout`: Total return if bet wins
- `status`: PENDING, WON, LOST, or PUSH
- `settled_at`: When bet was settled (null if pending)
- `created_at`, `updated_at`: Timestamps

## Setup (Not Yet Ready to Run)

This is the initial schema setup. Before running:

1. Review the database models in `src/models/`
2. Confirm the schema meets requirements
3. Next steps will include implementing betting logic and CLI

## Notes

- Using SQLAlchemy ORM with SQLite
- American odds format (e.g., +150, -110)
- Push handling for ties (stake returned)
- The Odds API for live NBA odds
