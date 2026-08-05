"""HTTP client for the public Job-Room job-advertisement API."""

from __future__ import annotations

import time
from typing import Any

import requests
from tqdm.auto import tqdm

from jobroom.models import JobAd, SearchHit

API_BASE = "https://api.job-room.ch/jobadservice/api/jobAdvertisements"
USER_AGENT = "jobroom/0.1 (+https://github.com/mbercx/jobroom)"
PAGE_SIZE = 100
MIN_INTERVAL = 0.5  # seconds between paginated requests


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
        limit: int = 1000,
    ) -> list[SearchHit]:
        """Return search results, fetching at most `limit` ads.

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
        hits: list[SearchHit] = []
        size = min(PAGE_SIZE, limit)
        progress = None
        page = 0
        while True:
            params: dict[str, str | int] = {
                "page": page,
                "size": size,
                "sort": "date_desc",
            }
            response = self.session.post(
                f"{API_BASE}/_search", json=body, params=params
            )
            response.raise_for_status()
            records = response.json()
            hits.extend(SearchHit.model_validate(record) for record in records)

            target = min(int(response.headers.get("X-Total-Count", len(hits))), limit)
            if progress is None:
                progress = tqdm(total=target, unit="ads", disable=target <= size)
            progress.update(min(len(records), target - progress.n))

            if len(hits) >= target or not records:
                break
            time.sleep(MIN_INTERVAL)
            page += 1
        progress.close()
        return hits[:limit]

    def get(self, ad_id: str) -> JobAd:
        """Return the complete advertisement with the given id."""
        response = self.session.get(f"{API_BASE}/{ad_id}")
        response.raise_for_status()
        return JobAd.model_validate(response.json())
