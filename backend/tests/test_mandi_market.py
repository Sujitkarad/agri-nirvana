import unittest
from unittest.mock import patch

from backend.config import settings
from backend.services import mandi_market


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


class TestMandiMarket(unittest.TestCase):
    def setUp(self):
        self.original_key = settings.DATA_GOV_IN_API_KEY
        settings.DATA_GOV_IN_API_KEY = "test-key"
        mandi_market._cache.clear()

    def tearDown(self):
        settings.DATA_GOV_IN_API_KEY = self.original_key
        mandi_market._cache.clear()

    @patch("backend.services.mandi_market.requests.get")
    def test_fetch_and_daily_trend(self, mock_get):
        mock_get.return_value = FakeResponse({"records": [
            {"state": "Maharashtra", "district": "Nashik", "market": "Nashik", "commodity": "Onion", "variety": "Red", "grade": "FAQ", "arrival_date": "03/09/2026", "min_price": "2000", "max_price": "2400", "modal_price": "2200"},
            {"state": "Maharashtra", "district": "Nashik", "market": "Nashik", "commodity": "Onion", "variety": "Red", "grade": "FAQ", "arrival_date": "2026-09-02", "min_price": "1900", "max_price": "2300", "modal_price": "2100"},
        ]})
        result = mandi_market.get_mandi_prices("Onion", state="Maharashtra", limit=10)
        row = result["records"][0]
        self.assertTrue(result["success"])
        self.assertEqual(row["arrival_date"], "2026-09-03")
        self.assertEqual(row["modal_price"], 2200.0)
        self.assertEqual(row["previous_modal_price"], 2100.0)
        self.assertEqual(row["trend"]["change"], 100.0)
        self.assertEqual(row["trend"]["change_pct"], 4.76)
        self.assertEqual(mock_get.call_args.kwargs["params"]["filters[state]"], "Maharashtra")

    @patch("backend.services.mandi_market.requests.get")
    def test_duplicate_same_day_does_not_create_false_trend(self, mock_get):
        mock_get.return_value = FakeResponse({"records": [
            {"state": "Maharashtra", "district": "Nashik", "market": "Nashik", "commodity": "Onion", "variety": "Red", "grade": "FAQ", "arrival_date": "2026-09-03", "min_price": "2000", "max_price": "2400", "modal_price": "2200"},
            {"state": "Maharashtra", "district": "Nashik", "market": "Nashik", "commodity": "Onion", "variety": "Red", "grade": "FAQ", "arrival_date": "2026-09-03", "min_price": "2100", "max_price": "2500", "modal_price": "2300"},
        ]})
        result = mandi_market.get_mandi_prices("Onion", limit=10)
        self.assertEqual(len(result["records"]), 1)
        self.assertEqual(result["records"][0]["modal_price"], 2250.0)
        self.assertIsNone(result["records"][0]["trend"]["change"])

    @patch("backend.services.mandi_market.requests.get")
    def test_malformed_records_are_ignored(self, mock_get):
        mock_get.return_value = FakeResponse({"records": [
            {"market": "Nashik", "arrival_date": "not-a-date", "modal_price": "2200"},
            {"market": "Nashik", "arrival_date": "2026-09-03", "modal_price": "2200"},
        ]})
        result = mandi_market.get_mandi_prices("Onion", limit=10)
        self.assertEqual(len(result["records"]), 1)

    @patch("backend.services.mandi_market.requests.get")
    def test_stale_cache_is_used_after_feed_failure(self, mock_get):
        mock_get.return_value = FakeResponse({"records": [
            {"state": "Maharashtra", "district": "Nashik", "market": "Nashik", "commodity": "Onion", "variety": "Red", "grade": "FAQ", "arrival_date": "2026-09-03", "modal_price": "2200"}
        ]})
        first = mandi_market.get_mandi_prices("Onion", limit=10)
        self.assertEqual(first["records"][0]["modal_price"], 2200.0)
        key = "Onion:*:1000"
        cached_records = mandi_market._cache[key][1]
        mandi_market._cache[key] = (0, cached_records)
        mock_get.side_effect = mandi_market.requests.RequestException("timeout")
        second = mandi_market.get_mandi_prices("Onion", limit=10)
        self.assertEqual(second["records"][0]["modal_price"], 2200.0)

    def test_rejects_unsupported_commodity(self):
        with self.assertRaises(ValueError):
            mandi_market.get_mandi_prices("Rice")

    def test_requires_api_key(self):
        settings.DATA_GOV_IN_API_KEY = None
        with self.assertRaises(RuntimeError):
            mandi_market.get_mandi_prices("Wheat")


if __name__ == "__main__":
    unittest.main()
