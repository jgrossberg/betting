from enum import Enum


class GameStatus(str, Enum):
    UPCOMING = "upcoming"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class BetType(str, Enum):
    MONEYLINE = "moneyline"
    SPREAD = "spread"
    OVER_UNDER = "over_under"


class BetSelection(str, Enum):
    HOME = "home"
    AWAY = "away"
    OVER = "over"
    UNDER = "under"


class BetStatus(str, Enum):
    PENDING = "pending"
    WON = "won"
    LOST = "lost"
    PUSH = "push"
