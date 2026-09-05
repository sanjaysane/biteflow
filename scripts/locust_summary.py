"""Read a Locust --csv stats file and print a short Markdown throughput
summary for $GITHUB_STEP_SUMMARY. Usage: locust_summary.py <stats.csv>.
"""

from __future__ import annotations

import csv
import sys


def main() -> None:
    path = sys.argv[1]
    with open(path, encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    agg = next((r for r in rows if r["Name"] == "Aggregated"), None)
    if not agg:
        print("No aggregated stats found", file=sys.stderr)
        sys.exit(1)
    total = int(float(agg["Request Count"]))
    fails = int(float(agg["Failure Count"]))
    rps = float(agg["Requests/s"])
    p50 = float(agg["50%"])
    p95 = float(agg["95%"])
    p99 = float(agg["99%"])
    avg = float(agg["Average Response Time"])
    print("## Locust load-test summary\n")
    print(f"- Requests: **{total}** ({fails} failed)")
    print(f"- Throughput: **{rps:.1f} req/s**")
    print(
        f"- Latency avg/p50/p95/p99: **{avg:.0f} / {p50:.0f} / {p95:.0f} / {p99:.0f} ms**"
    )
    print("\nPer-endpoint breakdown:\n")
    print("| Endpoint | Reqs | Fail | avg ms | p95 ms |")
    print("|---|---|---|---|---|")
    for r in rows:
        if r["Name"] in ("Aggregated", "Total"):
            continue
        print(
            f"| {r['Name']} | {int(float(r['Request Count']))} | "
            f"{int(float(r['Failure Count']))} | {float(r['Average Response Time']):.0f} | "
            f"{float(r['95%']):.0f} |"
        )


if __name__ == "__main__":
    main()
