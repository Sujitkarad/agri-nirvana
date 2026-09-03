"""Data.gov.in Agmarknet daily mandi price client."""

from __future__ import annotations

import os
import time
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any

import requests

RESOURCE_ID = "9ef84268-d588-465a-a308-a864a43d0070"
API_URL = f"https://api.data.gov.in/resource/{RESOURCE_ID}"
SUPPORTED_COMMODITIES = ("Wheat", "Onion", "Soybean", "Cotton", "Tomato")
CACHE_TTL_SECONDS = 600
REQUEST_TIMEOUT_SECONDS = 15

_cache: dict[str, tuple[float, Any]] = {}


def _api_key() -> str:
    key = os.getenv("DATA_GOV_IN_API_KEY", "").strip()
    if not key:
        raise RuntimeError("DATA_GOV_IN_API_KEY is not configured")
    return key


def _decimal(value: Any) -> float | None:
    try:
        return float(str(value).replace(",", "").strip())
    except (TypeError, ValueError):
        return None


def _fetch(commodity: str, limit: int = 1000) -> list[dict[str, Any]]:
    key = f"{commodity}:{limit}"
    cached = _cache.get(key)
    if cached and time.time() - cached[0] < CACHE_TTL_SECONDS:
        return cached[1]

    response = requests.get(
        API_URL,
        params={
            "api-key": _api_key(),
            "format": "json",
            "offset": 0,
            "limit": min(max(limit, 1), 1000),
            "filters[commodity]": commodity,
            "sort[arrival_date]": "desc",
        },
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    payload = response.json()
    records = payload.get("records", [])
    if not isinstance(records, list):
        raise RuntimeError("Unexpected Data.gov.in response: records is not a list")
    _cache[key] = (time.time(), records)
    return records


def _normalize_record(record: dict[str, Any]) -> dict[str, Any] | None:
    modal = _decimal(record.get("modal_price"))
    minimum = _decimal(record.get("min_price"))
    maximum = _decimal(record.get("max_price"))
    arrival_date = str(record.get("arrival_date") or "").strip()
    market = str(record.get("market") or "").strip()
    if modal is None or not arrival_date or not market:
        return None
    return {
        "state": str(record.get("state") or "").strip(),
        "district": str(record.get("district") or "").strip(),
        "market": market,
        "commodity": str(record.get("commodity") or "").strip(),
        "variety": str(record.get("variety") or "").strip(),
        "grade": str(record.get("grade") or "").strip(),
        "arrival_date": arrival_date,
        "min_price": minimum,
        "max_price": maximum,
        "modal_price": modal,
        "unit": "₹/quintal",
    }


def _trend(current: float, previous: float | None) -> dict[str, Any]:
    if previous is None or previous <= 0:
        return {"change": None, "direction": "flat", "change_pct": None}
    change = round(current - previous, 2)
    return {
        "change": change,
        "direction": "up" if change > 0 else "down" if change < 0 else "flat",
        "change_pct": round((change / previous) * 100, 2),
    }


def get_mandi_prices(commodity: str | None = None, state: str | None = None, limit: int = 50) -> dict[str, Any]:
    commodities = [commodity] if commodity else list(SUPPORTED_COMMODITIES)
    invalid = [c for c in commodities if c not in SUPPORTED_COMMODITIES]
    if invalid:
        raise ValueError(f"Unsupported commodity: {', '.join(invalid)}")

    output: list[dict[str, Any]] = []
    for name in commodities:
        raw = _fetch(name)
        rows = [r for r in (_normalize_record(x) for x in raw) if r is not None]
        if state:
            rows = [r for r in rows if r["state"].casefold() == state.casefold()]

        # Keep the latest observation for each market/variety/grade.
        latest: dict[tuple[str, str, str], dict[str, Any]] = {}
        for row in rows:
            key = (row["market"], row["variety"], row["grade"])
            existing = latest.get(key)
            if existing is None or row["arrival_date"] > existing["arrival_date"]:
                latest[key] = row

        # Find the previous observation for each market/variety/grade to calculate a daily move.
        grouped: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
        for row in rows:
            grouped[(row["market"], row["variety"], row["grade"])].append(row)
        for group in grouped.values():
            group.sort(key=lambda r: r["arrival_date"], reverse=True)

        for key, current in latest.items():
            group = grouped[key]
            previous = group[1]["modal_price"] if len(group) > 1 and group[1]["arrival_date"] != current["arrival_date"] else None
            item = dict(current)
            item["trend"] = _trend(current["modal_price"], previous)
            item["previous_modal_price"] = previous
            output.append(item)

    output.sort(key=lambda r: (r["arrival_date"], r["commodity"], r["market"]), reverse=True)
    return {
        "success": True,
        "source": "data.gov.in Agmarknet",
        "resource_id": RESOURCE_ID,
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "unit": "₹/quintal",
        "daily_data": True,
        "records": output[: max(1, min(limit, 200))],
    }
