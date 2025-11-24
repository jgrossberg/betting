# NBA Betting CLI

A Python-based command-line application for simulating NBA betting. Fetches real-time odds and scores from The Odds API, manages bets, and settles winnings.

## Features

- Fetch live NBA odds (moneyline, spread, over/under)
- Interactive CLI for placing bets
- Automatic bet settlement based on game results
- Track user balance and betting history
- Dry-run mode to preview settlements before committing

## Prerequisites

- Python 3.10+
- The Odds API key (free tier available at https://the-odds-api.com/)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd betting
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:

Create a `.env` file in the project root:
```
ODDS_API_KEY=your_api_key_here
ODDS_API_BASE_URL=https://api.the-odds-api.com/v4
ODDS_API_SPORT=basketball_nba
DATABASE_URL=sqlite:///betting.db
```

4. Initialize the database:
```bash
python init_db.py
```

This creates the SQLite database and sets up a default user with $1000 balance.

## Usage

### 1. Fetch Games

Fetch upcoming NBA games with odds from The Odds API:

```bash
python fetch_games.py
```

This populates the database with games, odds, and betting lines.

### 2. Place Bets

Launch the interactive betting CLI:

```bash
python place_bets.py
```

The CLI will:
- Display each upcoming game with available odds
- Prompt you to select bet type (moneyline, spread, over/under)
- Let you choose your selection and stake amount
- Deduct your stake from your balance immediately

### 3. Settle Bets

After games complete, settle your pending bets:

**Preview settlements (dry-run):**
```bash
python settle_bets.py --dry-run
```

This shows you which bets will win/lose/push without making any changes.

**Actually settle bets:**
```bash
python settle_bets.py
```

This will:
- Check for games that are IN_PROGRESS
- Fetch final scores from The Odds API
- Mark games as COMPLETED
- Settle all pending bets and update user balances

## Development

Run tests:
```bash
pytest
```

