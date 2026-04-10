from __future__ import annotations

import re
from datetime import datetime

import httpx
from bs4 import BeautifulSoup

from .models import GameSchedule, PitcherStat, PlayerStat, TeamStanding
from .sample_payloads import SAMPLE_PITCHERS, SAMPLE_PLAYERS, SAMPLE_SCHEDULES, SAMPLE_STANDINGS

STANDINGS_URL = "https://www.koreabaseball.com/Record/TeamRank/TeamRankDaily.aspx"
PLAYERS_URL = "https://www.koreabaseball.com/Record/Player/HitterBasic/Basic1.aspx"
PITCHERS_URL = "https://www.koreabaseball.com/Record/Player/PitcherBasic/Basic1.aspx"
SCHEDULE_API_URL = "https://www.koreabaseball.com/ws/Schedule.asmx/GetScheduleList"


class KboProvider:
    def __init__(self) -> None:
        self.client = httpx.Client(
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/123.0.0.0 Safari/537.36"
                ),
                "Referer": "https://www.koreabaseball.com/",
                "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
            },
            timeout=15.0,
            follow_redirects=True,
        )

    def get_schedules(self) -> tuple[list[GameSchedule], str]:
        data = self._parse_schedule_page()
        return (data, "live") if data else (SAMPLE_SCHEDULES, "sample")

    def get_standings(self) -> tuple[list[TeamStanding], str]:
        data = self._parse_team_rank_page()
        return (data, "live") if data else (SAMPLE_STANDINGS, "sample")

    def get_players(self) -> tuple[list[PlayerStat], str]:
        data = self._parse_hitter_rank_page()
        return (data, "live") if data else (SAMPLE_PLAYERS, "sample")

    def get_pitchers(self) -> tuple[list[PitcherStat], str]:
        data = self._parse_pitcher_rank_page()
        return (data, "live") if data else (SAMPLE_PITCHERS, "sample")

    def _fetch_html(self, url: str) -> str | None:
        try:
            response = self.client.get(url)
            response.raise_for_status()
            return response.text
        except Exception:
            return None

    def _post_json(self, url: str, data: dict[str, str | int]) -> dict | None:
        try:
            response = self.client.post(url, data=data)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None

    def _parse_schedule_page(self) -> list[GameSchedule]:
        now = datetime.now()
        payload = self._post_json(
            SCHEDULE_API_URL,
            data={
                "leId": 1,
                "srIdList": "0,9",
                "seasonId": str(now.year),
                "gameMonth": f"{now.month:02d}",
                "teamId": "",
            },
        )
        if not payload:
            return []

        games: list[tuple[tuple[int, int], GameSchedule]] = []
        current_date_label = ""
        for row_data in payload.get("rows", []):
            row = row_data.get("row", [])
            if len(row) < 8:
                continue

            start_index = 0
            first_text = self._clean_text(row[0].get("Text", ""))
            if re.search(r"\d{2}\.\d{2}\(.+\)", first_text):
                current_date_label = first_text
                start_index = 1

            if len(row) <= start_index + 6:
                continue

            matchup_html = row[start_index + 1].get("Text", "")
            away_team, home_team = self._parse_matchup_html(matchup_html)
            if not away_team or not home_team:
                continue

            games.append(
                (
                    self._date_key(current_date_label),
                    GameSchedule(
                        date_label=current_date_label or "오늘 경기",
                        time=self._clean_text(row[start_index].get("Text", "")) or "-",
                        away_team=away_team,
                        home_team=home_team,
                        stadium=self._clean_text(row[start_index + 6].get("Text", "")) or "-",
                        status=self._schedule_status(matchup_html),
                        broadcast=self._clean_schedule_channel(row[start_index + 4].get("Text", "")) or "-",
                    ),
                )
            )

        today_key = (now.month, now.day)
        upcoming = [game for key, game in games if key >= today_key]
        if upcoming:
            return upcoming[:25]
        return [game for _, game in games[:25]]

    def _parse_team_rank_page(self) -> list[TeamStanding]:
        html = self._fetch_html(STANDINGS_URL)
        if not html:
            return []

        soup = BeautifulSoup(html, "html.parser")
        table = soup.select_one("table.tData") or soup.select_one("table")
        if table is None:
            return []

        standings: list[TeamStanding] = []
        for row in table.select("tbody tr"):
            cells = [cell.get_text(" ", strip=True) for cell in row.select("td")]
            if len(cells) < 10 or not cells[0].isdigit():
                continue

            standings.append(
                TeamStanding(
                    rank=int(cells[0]),
                    team_name=cells[1],
                    wins=self._to_int(cells[3]),
                    losses=self._to_int(cells[4]),
                    draws=self._to_int(cells[5]),
                    win_rate=cells[6],
                    games_behind=cells[7] or "-",
                    streak=cells[9] or "-",
                )
            )

        return standings[:10]

    def _parse_hitter_rank_page(self) -> list[PlayerStat]:
        html = self._fetch_html(PLAYERS_URL)
        if not html:
            return []

        soup = BeautifulSoup(html, "html.parser")
        table = soup.select_one("table.tData") or soup.select_one("table")
        if table is None:
            return []

        players: list[PlayerStat] = []
        for row in table.select("tbody tr"):
            cells = [cell.get_text(" ", strip=True) for cell in row.select("td")]
            if len(cells) < 14 or not cells[0].isdigit():
                continue

            players.append(
                PlayerStat(
                    rank=int(cells[0]),
                    name=cells[1],
                    team_name=cells[2],
                    average=cells[3],
                    home_runs=self._to_int(cells[11]),
                    rbis=self._to_int(cells[13]),
                )
            )

        return players[:20]

    def _parse_pitcher_rank_page(self) -> list[PitcherStat]:
        html = self._fetch_html(PITCHERS_URL)
        if not html:
            return []

        soup = BeautifulSoup(html, "html.parser")
        table = soup.select_one("table.tData01") or soup.select_one("table")
        if table is None:
            return []

        pitchers: list[PitcherStat] = []
        for row in table.select("tbody tr"):
            cells = [cell.get_text(" ", strip=True) for cell in row.select("td")]
            if len(cells) < 16 or not cells[0].isdigit():
                continue

            pitchers.append(
                PitcherStat(
                    rank=int(cells[0]),
                    name=cells[1],
                    team_name=cells[2],
                    era=cells[3],
                    wins=self._to_int(cells[5]),
                    saves=self._to_int(cells[7]),
                    innings_pitched=cells[10],
                    strikeouts=self._to_int(cells[15]),
                )
            )

        return pitchers[:20]

    @staticmethod
    def _split_matchup(value: str) -> tuple[str, str]:
        if not value:
            return "", ""

        normalized = re.sub(r"\s+", " ", value).strip()
        for pattern in (r"(?i)\s*vs\s*", r"\s*:\s*"):
            parts = re.split(pattern, normalized)
            if len(parts) == 2:
                return parts[0].strip(), parts[1].strip()
        return "", ""

    @staticmethod
    def _to_int(value: str) -> int:
        match = re.search(r"-?\d+", value.replace(",", ""))
        return int(match.group()) if match else 0

    @staticmethod
    def _clean_text(value: str) -> str:
        return BeautifulSoup(value, "html.parser").get_text(" ", strip=True)

    def _parse_matchup_html(self, value: str) -> tuple[str, str]:
        soup = BeautifulSoup(value, "html.parser")
        team_spans = [span.get_text(" ", strip=True) for span in soup.select("span") if span.get_text(" ", strip=True)]
        team_spans = [text for text in team_spans if text.lower() != "vs" and not re.fullmatch(r"\d+", text)]
        if len(team_spans) >= 2:
            return team_spans[0], team_spans[-1]
        return self._split_matchup(self._clean_text(value))

    @staticmethod
    def _clean_schedule_channel(value: str) -> str:
        html = value.replace("<br />", " | ").replace("<br/>", " | ")
        return BeautifulSoup(html, "html.parser").get_text(" ", strip=True)

    @staticmethod
    def _schedule_status(matchup_html: str) -> str:
        digits = re.findall(r">(\d+)<", matchup_html)
        return "종료" if len(digits) >= 2 else "예정"

    @staticmethod
    def _date_key(value: str) -> tuple[int, int]:
        match = re.search(r"(\d{2})\.(\d{2})", value)
        if match:
            return int(match.group(1)), int(match.group(2))
        return 0, 0
