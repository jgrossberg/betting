# FreeBet

A free sports betting platform for testing strategies and models against real odds. No money, no risk.

**Live at:** https://betting-bice.vercel.app

## Features

- Real betting lines from The Odds API (moneyline, spread, over/under)
- Place bets and track your balance
- Automatic bet settlement when games complete
- REST API for programmatic betting (build your own models!)

## Architecture

- **Frontend:** React + Vite, deployed on Vercel
- **Backend:** FastAPI on Google Cloud Run
- **Database:** PostgreSQL on Supabase
- **Scheduled Jobs:** Cloud Scheduler triggers game fetching and scoring

## Local Development

### Backend

```bash
# Install dependencies
pip install -r requirements.txt

# Set up .env
cp .env.example .env
# Add your ODDS_API_KEY, DATABASE_URL, ADMIN_API_KEY

# Run migrations
alembic upgrade head

# Start the API
uvicorn betting.api.http_api:app --reload --port 9000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### CLI Scripts

```bash
# Fetch games from The Odds API
python -m betting.scripts.fetch_games

# Place bets interactively
python -m betting.scripts.place_bets <username>

# Score completed games
python -m betting.scripts.score_games

# Settle bets
python -m betting.scripts.settle_bets
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/games` | List games with odds |
| POST | `/users` | Create a user |
| GET | `/users/{id}/balance` | Get user balance |
| GET | `/users/{id}/bets` | Get user's bets |
| POST | `/bets?user_id={id}` | Place a bet |

Admin endpoints (require `X-Admin-Key` header):
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/admin/fetch-games` | Fetch games from Odds API |
| POST | `/admin/score-games` | Update scores for completed games |
| POST | `/admin/settle-bets` | Settle pending bets |

## Deployment

```bash
# Deploy backend to Cloud Run
./scripts/deploy.sh

# Frontend auto-deploys on push via Vercel
```

## Tests

```bash
pytest
```
