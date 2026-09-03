"""Reliable Data.gov.in / AGMARKNET daily mandi price service."""

from __future__ import annotations

import time
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any

import requests
from requests import Response

from backend.config import settings

RESOURCE_ID = "9ef84268-d588-465a-a308-a864a43d0070"
API_URL = f"https://api.data.gov.in/resource/{RESOURCE_ID}"
SUPPORTED_COMMODITIES = ("Wheat", "Onion", "Soybean", "Cotton", "Tomato")
CACHE_TTL_SECONDS = 600
REQUEST_TIMEOUT_SECONDS = 12
MAX_API_LIMIT = 1000
RETRY_COUNT = 2

# key -> (expires_at, records). A stale copy is retained so a temporary
# government API outage does not erase the last known good response.
_cache: dict[str, tuple[float, list[dict[str, Any]]]] = {}


def _api_key() -> str:
    key = (settings.DATA_GOV_IN_API_KEY or "").strip()
    if not key:
        raise RuntimeError("DATA_GOV_IN_API_KEY is not configured")
    return key


def _decimal(value: Any) -> float | None:
    if value is None:
        return None
    try:
        parsed = float(str(value).replace(",", "").strip())
        return parsed if parsed >= 0 else None
    except (TypeError, ValueError):
        return None


def _date_key(value: Any) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"):
        try:
            return datetime.strptime(text, fmt).date().isoformat()
        except ValueError:
            continue
    return ""


def _request(params: dict[str, Any]) -> Response:
    last_error: Exception | None = None
    for attempt in range(RETRY_COUNT + 1):
        try:
            response = requests.get(API_URL, params=params, timeout=REQUEST_TIMEOUT_SECONDS)
            response.raise_for_status()
            return response
        except requests.RequestException as exc:
            last_error = exc
            if attempt < RETRY_COUNT:
                time.sleep(0.5 * (2**attempt))
    raise RuntimeError("Data.gov.in market feed request failed") from last_error


def _fetch(
    commodity: str,
    state: str | None = None,
    limit: int = MAX_API_LIMIT,
) -> list[dict[str, Any]]:
    normalized_state = state.strip() if state else None
    api_limit = min(max(limit, 1), MAX_API_LIMIT)
    cache_key = f"{commodity}:{normalized_state or '*'}:{api_limit}"
    now = time.time()
    cached = _cache.get(cache_key)

    if cached and now < cached[0]:
        return cached[1]

    params: dict[str, Any] = {
        "api-key": _api_key(),
        "format": "json",
        "offset": 0,
        "limit": api_limit,
        "filters[commodity]": commodity,
        "sort[arrival_date]": "desc",
    }
    if normalized_state:
        params["filters[state]"] = normalized_state

    try:
        payload = _request(params).json()
        records = payload.get("records", [])
        if not isinstance(records, list):
            raise RuntimeError("Unexpected Data.gov.in response")
        _cache[cache_key] = (now + CACHE_TTL_SECONDS, records)
        return records
    except Exception:
        if cached and cached[1]:
            return cached[1]
        raise


def _normalize_record(record: dict[str, Any]) -> dict[str, Any] | None:
    if not isinstance(record, dict):
        return None

    modal = _decimal(record.get("modal_price"))
    minimum = _decimal(record.get("min_price"))
    maximum = _decimal(record.get("max_price"))
    date_key = _date_key(record.get("arrival_date"))
    market = str(record.get("market") or "").strip()

    if modal is None or not date_key or not market:
        return None
    if minimum is not None and maximum is not None and minimum > maximum:
        minimum, maximum = maximum, minimum
    if minimum is not None and modal < minimum:
        minimum = None
    if maximum is not None and modal > maximum:
        maximum = None

    return {
        "state": str(record.get("state") or "").strip(),
        "district": str(record.get("district") or "").strip(),
        "market": market,
        "commodity": str(record.get("commodity") or "").strip(),
        "variety": str(record.get("variety") or "").strip(),
        "grade": str(record.get("grade") or "").strip(),
        "arrival_date": date_key,
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


def _merge_same_day(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Deduplicate observations without manufacturing a previous-day price."""
    grouped: dict[tuple[str, str, str, str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        key = (
            row["state"], row["district"], row["market"],
            row["commodity"], row["variety"], row["grade"],
        )
        grouped[key].append(row)

    result: list[dict[str, Any]] = []
    for observations in grouped.values():
        by_date: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in observations:
            by_date[row["arrival_date"]].append(row)

        for date, same_day in by_date.items():
            modal_values = [r["modal_price"] for r in same_day]
            min_values = [r["min_price"] for r in same_day if r["min_price"] is not None]
            max_values = [r["max_price"] for r in same_day if r["max_price"] is not None]
            base = dict(same_day[0])
            base["arrival_date"] = date
            base["modal_price"] = round(sum(modal_values) / len(modal_values), 2)
            base["min_price"] = round(min(min_values), 2) if min_values else None
            base["max_price"] = round(max(max_values), 2) if max_values else None
            result.append(base)
    return result


def _with_trends(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[str, str, str, str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[
            row["state"], row["district"], row["market"],
            row["commodity"], row["variety"], row["grade"],
        ].append(row)

    result: list[dict[str, Any]] = []
    for group in groups.values():
        group.sort(key=lambda r: r["arrival_date"], reverse=True)
        current = group[0]
        previous = group[1]["modal_price"] if len(group) > 1 else None
        item = dict(current)
        item["trend"] = _trend(current["modal_price"], previous)
        item["previous_modal_price"] = previous
        result.append(item)
    return result


def get_mandi_prices(
    commodity: str | None = None,
    state: str | None = None,
    limit: int = 50,
) -> dict[str, Any]:
    if limit < 1:
        raise ValueError("limit must be at least 1")

    commodities = [commodity] if commodity else list(SUPPORTED_COMMODITIES)
    invalid = [c for c in commodities if c not in SUPPORTED_COMMODITIES]
    if invalid:
        raise ValueError(f"Unsupported commodity: {', '.join(invalid)}")

    normalized_state = state.strip() if state else None
    output: list[dict[str, Any]] = []
    for name in commodities:
        raw = _fetch(name, state=normalized_state, limit=MAX_API_LIMIT)
        rows = [r for r in (_normalize_record(x) for x in raw) if r is not None]
        output.extend(_with_trends(_merge_same_day(rows)))

    output.sort(
        key=lambda r: (
            r["arrival_date"], r["commodity"], r["state"],
            r["district"], r["market"], r["variety"], r["grade"],
        ),
        reverse=True,
    )

    return {
        "success": True,
        "source": "data.gov.in Agmarknet",
        "resource_id": RESOURCE_ID,
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "unit": "₹/quintal",
        "daily_data": True,
        "records": output[: min(limit, 200)],
    }
