"""Illustrative Monitoring API adapter; live access has not been verified."""

from datetime import date
import os
import re
from urllib.parse import urlsplit
import requests
from dotenv import load_dotenv


def fetch_energy(start_date, end_date, http=requests):
    for value in (start_date, end_date):
        if not isinstance(value, str) or not re.fullmatch(
            r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value
        ):
            raise ValueError("Dates must be YYYY-MM-DD")
    if date.fromisoformat(start_date) > date.fromisoformat(end_date):
        raise ValueError("Start date cannot follow end date")
    load_dotenv()
    site, key = os.getenv("SOLAREDGE_SITE_ID"), os.getenv("SOLAREDGE_API_KEY")
    base = os.getenv(
        "SOLAREDGE_BASE_URL", "https://monitoringapi.solaredge.com"
    ).rstrip("/")
    if not site or not key:
        raise ValueError("Configure SOLAREDGE_SITE_ID and SOLAREDGE_API_KEY")
    parsed = urlsplit(base)
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or parsed.username
        or parsed.password
        or parsed.query
        or parsed.fragment
    ):
        raise ValueError("Use an HTTPS base URL without credentials, query or fragment")
    if not re.fullmatch(r"[0-9]+", site):
        raise ValueError("Site ID must be numeric")
    try:
        response = http.get(
            f"{base}/site/{site}/energy",
            params={
                "startDate": start_date,
                "endDate": end_date,
                "timeUnit": "DAY",
                "api_key": key,
            },
            timeout=30,
            allow_redirects=False,
        )
        response.raise_for_status()
        if 300 <= response.status_code < 400:
            raise ValueError("Redirect refused")
        return response.json()
    except (requests.RequestException, ValueError):
        raise RuntimeError(
            "Energy API request failed; verify authorized API access"
        ) from None
