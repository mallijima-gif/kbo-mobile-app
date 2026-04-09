from .models import GameSchedule, PlayerStat, TeamStanding


SAMPLE_SCHEDULES = [
    GameSchedule(date_label="4월 9일", time="18:30", home_team="두산", away_team="LG", stadium="잠실"),
    GameSchedule(date_label="4월 9일", time="18:30", home_team="롯데", away_team="SSG", stadium="사직"),
    GameSchedule(date_label="4월 9일", time="18:30", home_team="한화", away_team="KIA", stadium="대전"),
]

SAMPLE_STANDINGS = [
    TeamStanding(rank=1, team_name="LG 트윈스", wins=10, losses=4, draws=0, win_rate="0.714", streak="3연승", games_behind="0.0"),
    TeamStanding(rank=2, team_name="KIA 타이거즈", wins=9, losses=5, draws=0, win_rate="0.643", streak="1연승", games_behind="1.0"),
    TeamStanding(rank=3, team_name="두산 베어스", wins=8, losses=6, draws=0, win_rate="0.571", streak="1연패", games_behind="2.0"),
]

SAMPLE_PLAYERS = [
    PlayerStat(rank=1, name="김도영", team_name="KIA", position="내야수", average="0.347", home_runs=4, rbis=13),
    PlayerStat(rank=2, name="구자욱", team_name="삼성", position="외야수", average="0.333", home_runs=3, rbis=11),
    PlayerStat(rank=3, name="홍창기", team_name="LG", position="외야수", average="0.326", home_runs=1, rbis=8),
]
