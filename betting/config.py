import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration settings."""

    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///betting.db")

    ODDS_API_KEY = os.getenv("ODDS_API_KEY", "")
    ODDS_API_BASE_URL = "https://api.the-odds-api.com/v4"
    ODDS_API_SPORT = "basketball_nba"

    ADMIN_API_KEY = os.getenv("ADMIN_API_KEY", "")

    DEFAULT_USER_BALANCE = 1000.00

    @classmethod
    def validate(cls):
        """Validate that required configuration is present."""
        if not cls.ODDS_API_KEY:
            raise ValueError(
                "ODDS_API_KEY is required. Please set it in your .env file or environment."
            )


config = Config()
