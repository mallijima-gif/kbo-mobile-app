from __future__ import annotations

import re
from typing import Iterable

import httpx
from bs4 import BeautifulSoup

from .models import GameSchedule, PlayerStat, TeamStanding
from .sample_data import SAMPLE_PLAYERS, SAMPLE_SCHEDULES, SAMPLE_STANDINGS


class KboProvider:
    def __init__(self) -> None:
        self.client = httpx.Client(
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/123.0 Mobile Safari/537.36"
                )
            },
            timeout=15.0,
            follow_redirects=True,
        )

    def get_schedules(self) -> tuple[list[GameSchedule], str]:
        data = self._parse_schedule_page()
        if data:
            return data, "live"
        return SAMPLE_SCHEDULES, "sample"

    def get_standings(self) -> tuple[list[TeamStanding], str]:
        data = self._parse_team_rank_page()
        if data:
            return data, "live"
        return SAMPLE_STANDINGS, "sample"

    def get_players(self) -> tuple[list[PlayerStat], str]:
        data = self._parse_hitter_rank_page()
        if data:
            return data, "live"
        return SAMPLE_PLAYERS, "sample"

    def _fetch_html(self, url: str) -> str | None:
        try:
            response = self.client.get(url)
            response.raise_for_status()
            return response.text
        except Exception:
            return None

    def _extract_rows(self, html: str) -> Iterable[list[str]]:
        soup = BeautifulSoup(html, "html.parser")
        for table in soup.select("table"):
            for row in table.select("tr"):
                cells = [cell.get_text(" ", strip=True) for cell in row.select("th,td")]
                if len(cells) >= 3:
                    yield cells

    def _parse_schedule_page(self) -> list[GameSchedule]:
        html = self._fetch_html("https://sports.news.naver.com/kbaseball/schedule/index?category=kbo")
        if not html:
            return []

        games: list[GameSchedule] = []
        current_date = ""
        for cells in self._extract_rows(html):
            joined = " ".join(cells)
            if "월" in joined and "일" in joined and len(cells) <= 2:
                current_date = joined
                continue

            matchup = next((cell for cell in cells if "vs" in cell.lower()), "")
            teams = self._split_matchup(matchup)
            if not teams:
                continue
            time = next((cell for cell in cells if re.match(r"\d{1,2}:\d{2}", cell)), "-")
            stadium = cells[-1] if cells else "-"
            games.append(
                GameSchedule(
                    date_label=current_date or "오늘 경기",
                    time=time,
                    away_team=teams[0],
                    home_team=teams[1],
                    stadium=stadium,
                )
            )
        return games[:10]

    def _parse_team_rank_page(self) -> list[TeamStanding]:
        html = self._fetch_html("https://sports.news.naver.com/kbaseball/record/index?category=kbo&year=2026")
        if not html:
            return []

        standings: list[TeamStanding] = []
        for cells in self._extract_rows(html):
            if len(cells) < 7 or not cells[0].isdigit():
                continue
            try:
                standings.append(
                    TeamStanding(
                        rank=int(cells[0]),
                        team_name=cells[1],
                        wins=self._to_int(cells[2]),
                        losses=self._to_int(cells[3]),
                        draws=self._to_int(cells[4]),
                        win_rate=cells[5],
                        games_behind=cells[6] if len(cells) > 6 else "-",
                        streak=cells[7] if len(cells) > 7 else "-",
                    )
                )
            except Exception:
                continue
        return standings[:10]

    def _parse_hitter_rank_page(self) -> list[PlayerStat]:
        html = self._fetch_html("https://sports.news.naver.com/kbaseball/record/index?category=kbo&tab=player&year=2026")
        if not html:
            return []

        players: list[PlayerStat] = []
        for cells in self._extract_rows(html):
            if len(cells) < 6 or not cells[0].isdigit():
                continue
            try:
                players.append(
                    PlayerStat(
                        rank=int(cells[0]),
                        name=cells[1],
                        team_name=cells[2],
                        average=cells[3],
                        home_runs=self._to_int(cells[4]),
                        rbis=self._to_int(cells[5]),
                    )
                )
            except Exception:
                continue
        return players[:10]

    @staticmethod
    def _split_matchup(value: str) -> tuple[str, str] | None:
        normalized = re.sub(r"\s+", " ", value).strip()
        parts = re.split(r"(?i)\s*vs\s*", normalized)
        if len(parts) == 2:
            return parts[0].strip(), parts[1].strip()
        return None

    @staticmethod
    def _to_int(value: str) -> int:
        match = re.search(r"-?\d+", value.replace(",", ""))
        return int(match.group()) if match else 0
