import os
import unittest
from unittest.mock import Mock, patch
import requests
from src.report import normalize
from src.fetch_live import fetch_energy


class ValidationTests(unittest.TestCase):
    def payload(self, value=1000, date="2026-10-01", unit="Wh"):
        return {"energy": {"unit": unit, "values": [{"date": date, "value": value}]}}

    def test_null_and_kwh(self):
        self.assertEqual(normalize(self.payload(None))[0]["energy_kwh"], "")
        self.assertEqual(normalize(self.payload(2, unit="kWh"))[0]["energy_kwh"], 2)

    def test_invalid_values(self):
        for value in ("NaN", "inf", -1, True, {}):
            with self.subTest(value=value), self.assertRaises(ValueError):
                normalize(self.payload(value))

    def test_dates_units_duplicates_and_missing_fields(self):
        for payload in ({}, self.payload(date="bad"), self.payload(unit="MWh")):
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                normalize(payload)
        payload = self.payload()
        payload["energy"]["values"] *= 2
        with self.assertRaises(ValueError):
            normalize(payload)

    @patch.dict(
        os.environ,
        {
            "SOLAREDGE_API_KEY": "synthetic-key",
            "SOLAREDGE_SITE_ID": "123",
            "SOLAREDGE_BASE_URL": "https://example.invalid",
        },
        clear=True,
    )
    def test_mock_adapter_and_sanitized_failure(self):
        http = Mock()
        http.get.return_value.status_code = 200
        http.get.return_value.json.return_value = self.payload()
        self.assertEqual(fetch_energy("2026-10-01", "2026-10-02", http), self.payload())
        http.get.side_effect = requests.HTTPError("url-with-synthetic-key")
        with self.assertRaises(RuntimeError) as caught:
            fetch_energy("2026-10-01", "2026-10-02", http)
        self.assertNotIn("synthetic-key", str(caught.exception))

    def test_reversed_dates_fail_before_network(self):
        http = Mock()
        with self.assertRaises(ValueError):
            fetch_energy("2026-10-02", "2026-10-01", http)
        http.get.assert_not_called()
