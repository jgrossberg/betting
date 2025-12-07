const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:9000';

export interface Game {
  id: string;
  external_id: string;
  home_team: string;
  away_team: string;
  commence_time: string;
  status: 'upcoming' | 'in_progress' | 'completed';
  home_moneyline: string | null;
  away_moneyline: string | null;
  home_spread: string | null;
  home_spread_odds: string | null;
  away_spread: string | null;
  away_spread_odds: string | null;
  total_points: string | null;
  over_odds: string | null;
  under_odds: string | null;
  home_score: number | null;
  away_score: number | null;
}

export interface Bet {
  id: string;
  user_id: string;
  game_id: string;
  bet_type: 'moneyline' | 'spread' | 'over_under';
  selection: 'home' | 'away' | 'over' | 'under';
  odds: string;
  stake: string;
  potential_payout: string;
  status: 'pending' | 'won' | 'lost' | 'push';
  settled_at: string | null;
}

export interface User {
  id: string;
  username: string;
  balance: string;
}

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const res = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Request failed' }));
      throw new Error(err.detail || `Request failed: ${res.status}`);
    }

    return res.json();
  }

  async getGames(status?: string): Promise<Game[]> {
    const query = status ? `?status=${status}` : '';
    return this.request<Game[]>(`/games${query}`);
  }

  async getUserBets(userId: string): Promise<Bet[]> {
    return this.request<Bet[]>(`/users/${userId}/bets`);
  }

  async getUserBalance(userId: string): Promise<{ user_id: string; balance: string }> {
    return this.request(`/users/${userId}/balance`);
  }

  async createUser(username: string, balance?: string): Promise<User> {
    return this.request<User>('/users', {
      method: 'POST',
      body: JSON.stringify({ username, balance }),
    });
  }

  async placeBet(
    userId: string,
    gameId: string,
    betType: 'moneyline' | 'spread' | 'over_under',
    selection: 'home' | 'away' | 'over' | 'under',
    stake: string
  ): Promise<Bet> {
    return this.request<Bet>(`/bets?user_id=${userId}`, {
      method: 'POST',
      body: JSON.stringify({
        game_id: gameId,
        bet_type: betType,
        selection,
        stake,
      }),
    });
  }
}

export const api = new ApiClient(API_BASE);
