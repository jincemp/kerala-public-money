"""Collect the LSGD Annual Plan expenditure table.

The page shows each district's local government plan budget and spending,
in crore rupees, with an "as on" date in its heading. Columns seen so far:
District, six budget columns ending in Budget Total, six expenditure columns
ending in Expenditure Total, two project columns, then the percentage spent.
Expenditure cells look like "28.04 [ 10.02%]".
"""

import re

from bs4 import BeautifulSoup

from common import fetch, normalize_district, now_iso, parse_amount, save_snapshot

URL = "https://lsgkerala.gov.in/plandashboard/Plan/Annualplandetails.php"


def first_number(text):
    return parse_amount(text.split("[")[0])


def parse(html):
    soup = BeautifulSoup(html, "html.parser")
    page_text = soup.get_text(" ", strip=True)
    as_on = None
    # Keep the time when the heading has one, e.g. "as on 13 July 2025, 10:00AM".
    match = re.search(
        r"as on\s+([^|]{4,40}?(?:\d{4}(?:,?\s*\d{1,2}[:.]\d{2}\s*(?:AM|PM)?)?|AM|PM))",
        page_text, re.I)
    if match:
        as_on = "as on " + match.group(1).strip()

    rows = {}
    total = None
    for tr in soup.find_all("tr"):
        cells = [c.get_text(" ", strip=True) for c in tr.find_all(["td", "th"])]
        if len(cells) < 15:
            continue
        label = cells[0]
        numbers = [first_number(c) for c in cells[1:]]
        if any(n is None for n in numbers[:14]):
            continue  # header rows
        record = {
            "budget_cr": numbers[6],
            "spent_cr": numbers[13],
            "pct": numbers[-1],
            "budget_by_fund_cr": dict(zip(
                ["general", "scp", "tsp", "fc_untied", "fc_tied", "klgsdp"], numbers[0:6])),
        }
        if label.strip().lower() == "total":
            total = record
            continue
        name = normalize_district(label)
        if name:
            rows[name] = record

    if len(rows) < 10:
        raise RuntimeError(f"Only {len(rows)} districts found; the page may have changed")
    return as_on, rows, total


def main():
    resp = fetch(URL)
    try:
        as_on, rows, total = parse(resp.text)
    except RuntimeError:
        # Since Oct 2026 every /plandashboard/ address redirects to the Sulekha
        # welcome page, which has no table. Say so in data/status.json.
        if resp.url != URL:
            raise RuntimeError(f"No plan table found. {URL} now redirects to {resp.url}") from None
        raise
    payload = {
        "source": "LSGD Plan Dashboard",
        "source_url": URL,
        "collected_at": now_iso(),
        "as_on": as_on,
        "amount_unit": "crore",
        "total": total,
        "by_district": rows,
    }
    path = save_snapshot("lsgd_plan", payload)
    print(f"LSGD plan: {len(rows)} districts ({as_on}), saved to {path}")


if __name__ == "__main__":
    main()
