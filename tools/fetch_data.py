#!/usr/bin/env python3
"""Pull the contribution calendar GitHub itself publishes, and cache it.

    python3 tools/fetch_data.py      # needs `gh auth login`

Writes tools/data/contributions.json, which tools/build.py draws. Kept as a
separate step so the card can be rebuilt offline, and so the numbers on it are
always something GitHub returned rather than something this repo computed.

Language data is deliberately NOT collected. The two Tammy repositories carry a
committed virtualenv between them — 120 MB of the 127 MB across every repo —
so /languages reports 90% Python, which measures numpy and CPython rather than
anything that was written here. A share bar built on that would be false.
"""

import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "tools", "data", "contributions.json")
USER = os.environ.get("PROFILE_USER", "abdullatam")

QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount weekday } }
      }
    }
  }
}
"""


def main():
    r = subprocess.run(
        ["gh", "api", "graphql", "-f", f"query={QUERY}", "-F", f"login={USER}"],
        capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"gh failed: {r.stderr.strip()}")

    payload = json.loads(r.stdout)
    if "errors" in payload:
        sys.exit(f"graphql errors: {payload['errors']}")

    cal = payload["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    days = [d for w in cal["weeks"] for d in w["contributionDays"]]
    if not days:
        sys.exit("calendar came back empty — refusing to overwrite the cache")

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(cal, open(OUT, "w"), indent=1)
    print(f"{cal['totalContributions']} contributions over {len(days)} days "
          f"({days[0]['date']} → {days[-1]['date']}) -> {os.path.relpath(OUT, ROOT)}")


if __name__ == "__main__":
    main()
