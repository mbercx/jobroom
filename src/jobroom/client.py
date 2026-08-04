"""HTTP client for the public Job-Room job-advertisement API."""

from __future__ import annotations

from typing import Any

import requests

from jobroom.models import SearchHit

API_BASE = "https://api.job-room.ch/jobadservice/api/jobAdvertisements"
USER_AGENT = "jobroom/0.1 (+https://github.com/mbercx/jobroom)"


class JobRoomClient:
    """Client for the Job-Room job-advertisement API."""

    def __init__(self) -> None:
        self.session = requests.Session()
        self.session.headers["User-Agent"] = USER_AGENT

    def search(
        self,
        keywords: list[str],
        workload_min: int = 0,
        online_since: int = 30,
    ) -> list[SearchHit]:
        """Return one page of search results.

        Each `SearchHit` carries a keyword-context `snippet`, not the full ad;
        use `get` to fetch the complete advertisement.
        """
        body: dict[str, Any] = {
            "keywords": keywords,
            "workloadPercentageMin": workload_min,
            "workloadPercentageMax": 100,
            "onlineSince": online_since,
            "displayRestricted": False,
        }
        params: dict[str, str | int] = {"page": 0, "size": 20, "sort": "date_desc"}
        response = self.session.post(f"{API_BASE}/_search", json=body, params=params)
        response.raise_for_status()
        return [SearchHit.model_validate(record) for record in response.json()]

    def get(self, ad_id: str) -> dict[str, Any]:
        """Return the raw record of a single advertisement."""
        response = self.session.get(f"{API_BASE}/{ad_id}")
        response.raise_for_status()
        return response.json()
