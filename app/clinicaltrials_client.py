import time
from typing import Any, Dict, List, Optional
from urllib.parse import urlencode

from curl_cffi import requests


BASE_URL = "https://clinicaltrials.gov/api/v2/studies"

CACHE_TTL_SECONDS = 300

_STUDIES_CACHE: Dict[str, Dict[str, Any]] = {}


def remove_none_params(params: Dict[str, Any]) -> Dict[str, Any]:
    return {
        key: value
        for key, value in params.items()
        if value is not None and value != ""
    }

def make_cache_key(params: Dict[str, Any], max_studies: int) -> str:
    cache_payload = {
        "params": sorted(params.items()),
        "max_studies": max_studies,
    }

    return str(cache_payload)

async def fetch_studies(
    drug_name: Optional[str] = None,
    condition: Optional[str] = None,
    sponsor: Optional[str] = None,
    country: Optional[str] = None,
    overall_status: Optional[str] = None,
    max_studies: int = 100,
) -> List[Dict[str, Any]]:
    params: Dict[str, Any] = {
        "format": "json",
        "pageSize": min(max_studies, 100),
        "query.intr": drug_name,
        "query.cond": condition,
        "query.spons": sponsor,
        "query.locn": country,
        "filter.overallStatus": overall_status,
    }

    params = remove_none_params(params)

    cache_key = make_cache_key(params, max_studies)
    cached = _STUDIES_CACHE.get(cache_key)

    if cached:
        age_seconds = time.time() - cached["created_at"]

        if age_seconds < CACHE_TTL_SECONDS:
            return cached["studies"]

    studies: List[Dict[str, Any]] = []
    next_page_token = None

    while len(studies) < max_studies:
        request_params = dict(params)

        if next_page_token:
            request_params["pageToken"] = next_page_token

        url = f"{BASE_URL}?{urlencode(request_params)}"

        response = requests.get(
            url,
            impersonate="chrome",
            timeout=30,
            headers={
                "Accept": "application/json,text/plain,*/*",
                "Accept-Language": "en-US,en;q=0.9",
            },
        )

        if response.status_code == 403:
            raise RuntimeError(
                "ClinicalTrials.gov returned 403 Forbidden even with browser impersonation. "
                f"URL: {url}"
            )

        response.raise_for_status()

        payload = response.json()
        batch = payload.get("studies", [])
        studies.extend(batch)

        next_page_token = payload.get("nextPageToken")

        if not next_page_token or not batch:
            break

        final_studies = studies[:max_studies]

    _STUDIES_CACHE[cache_key] = {
        "created_at": time.time(),
        "studies": final_studies,
    }

    return final_studies