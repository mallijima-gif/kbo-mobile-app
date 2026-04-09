from pydantic import BaseModel


class GameSchedule(BaseModel):
    date_label: str
    time: str
    home_team: str
    away_team: str
    stadium: str


class TeamStanding(BaseModel):
    rank: int
    team_name: str
    wins: int
    losses: int
    draws: int
    win_rate: str
    streak: str
    games_behind: str = "-"


class PlayerStat(BaseModel):
    rank: int
    name: str
    team_name: str
    position: str | None = None
    average: str
    home_runs: int
    rbis: int


class ApiEnvelope(BaseModel):
    source: str
    cached: bool
    items: list
