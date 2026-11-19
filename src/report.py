"""Validate SolarEdge-style energy samples and export a daily CSV."""

import argparse
import csv
from datetime import datetime
import json
import math
from pathlib import Path
import re


def normalize(payload):
    try:
        energy = payload["energy"]
        unit = energy["unit"]
        values = energy["values"]
    except (KeyError, TypeError) as exc:
        raise ValueError("Expected energy.unit and energy.values") from exc
    if unit not in ("Wh", "kWh") or not isinstance(values, list):
        raise ValueError("Expected Wh/kWh units and a list of values")
    factor = 0.001 if unit == "Wh" else 1.0
    result, seen = [], set()
    for row in values:
        if not isinstance(row, dict) or "date" not in row or "value" not in row:
            raise ValueError("Each reading needs a date and value (null is allowed)")
        stamp = row["date"]
        if not isinstance(stamp, str) or not re.fullmatch(
            r"[0-9]{4}-[0-9]{2}-[0-9]{2}(?:[ T][0-9]{2}:[0-9]{2}:[0-9]{2})?", stamp
        ):
            raise ValueError("Invalid daily reading date")
        day = datetime.fromisoformat(stamp).date()
        if day in seen:
            raise ValueError("Duplicate daily reading")
        seen.add(day)
        value = row["value"]
        if value is not None:
            if isinstance(value, bool):
                raise ValueError("Energy must be finite and nonnegative")
            try:
                value = float(value)
            except (TypeError, OverflowError) as exc:
                raise ValueError("Invalid energy value") from exc
            if not math.isfinite(value) or value < 0:
                raise ValueError("Energy must be finite and nonnegative")
        result.append(
            {
                "date": stamp,
                "energy_kwh": "" if value is None else round(value * factor, 3),
            }
        )
    return sorted(result, key=lambda row: row["date"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("output/energy.csv"))
    args = parser.parse_args()
    try:
        result = normalize(json.loads(args.input.read_text(encoding="utf-8")))
        if args.input.resolve() == args.output.resolve():
            raise ValueError("Input and output must differ")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=["date", "energy_kwh"])
            writer.writeheader()
            writer.writerows(result)
    except (OSError, ValueError) as exc:
        parser.exit(1, f"Report failed: {exc}\n")
    print(f"Wrote {len(result)} records to {args.output}")


if __name__ == "__main__":
    main()
