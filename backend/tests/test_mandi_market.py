import unittest
from unittest.mock import patch

from backend.config import settings
from backend.services import mandi_market


class TestMandiMarket(unittest.TestCase):
    def setUp(self):
        self.original_key = settings.DATA_GOV_IN_API_KEY
        mandi_market._cache.clear()

    def tearDown(self):
        settings.DATA_GOV_IN_API_KEY = self.original_key
        mandi_market._cache.clear()

    @patch("backend.services.mandi_market.requests.get")
    def test_fetch_and_daily_trend(self, mock_get):
        settings.DATA_GOV_IN_API_KEY = "test-key"

        class Response:
            def raise_for_status(self):
                return None

            def json(self):
                return {
                    "records": [
                        {
                            "state": "Maharashtra",
                            "district": "Nashik",
                            "market": "Nashik",
                            "commodity": "Onion",
                            "variety": "Red",
                            "grade": "FAQ",
                            "arrival_date": "2026-09-03",
                            "min_price": "2000",
                            "max_price": "2400",
                            "modal_price": "2200",
                        },
                        {
                            "state": "Maharashtra",
                            "district": "Nashik",
                            "market": "Nashik",
                            "commodity": "Onion",
                            "variety": "Red",
                            "grade": "FAQ",
                            "arrival_date": "2026-09-02",
                            "min_price": "1900",
                            "max_price": "2300",
                            "modal_price": "2100",
                        },
                    ]
                }

        mock_get.return_value = Response()
        result = mandi_market.get_mandi_prices("Onion", limit=10)
        self.assertTrue(result["success"])
        self.assertEqual(result["source"], "data.gov.in Agmarknet")
        self.assertEqual(result["records"][0]["modal_price"], 2200.0)
        self.assertEqual(result["records"][0]["trend"]["change"], 100.0)
        self.assertEqual(result["records"][0]["trend"]["direction"], "up")
        mock_get.assert_called_once()

    def test_rejects_unsupported_commodity(self):
        settings.DATA_GOV_IN_API_KEY = "test-key"
        with self.assertRaises(ValueError):
            mandi_market.get_mandi_prices("Rice")

    def test_requires_api_key(self):
        settings.DATA_GOV_IN_API_KEY = None
        with self.assertRaises(RuntimeError):
            mandi_market.get_mandi_prices("Wheat")


if __name__ == "__main__":
    unittest.main()
