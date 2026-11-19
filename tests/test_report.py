import unittest
from src.report import normalize


class ReportTests(unittest.TestCase):
    def test_wh_to_kwh(self):
        self.assertEqual(
            normalize(
                {
                    "energy": {
                        "unit": "Wh",
                        "values": [{"date": "2026-01-01", "value": 1200}],
                    }
                }
            )[0]["energy_kwh"],
            1.2,
        )


if __name__ == "__main__":
    unittest.main()
