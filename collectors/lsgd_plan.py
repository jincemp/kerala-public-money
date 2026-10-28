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
    match = re.search(r"as on\s+([^|]{4,40}?(?:AM|PM|\d{4}))", page_text, re.I)
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
    as_on, rows, total = parse(resp.text)
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
