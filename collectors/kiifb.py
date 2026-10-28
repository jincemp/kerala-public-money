"""Collect the KIIFB project list from kiifb.org.

The public page lists every project with department, implementing agency (SPV),
approved amount, payment released and status. It has no district column, so we
also ask the page for each district's list and record which districts each
project appears under.

Amounts on the page are in rupees. We store them in rupees and convert to
crore only when building the site summary.
"""

import re
import sys
import time

from bs4 import BeautifulSoup

from common import DISTRICT_ORDER, fetch, normalize_district, now_iso, parse_amount, save_snapshot

URL = "https://www.kiifb.org/prjStatus.jsp"
FILTER_URL = "https://www.kiifb.org/prjStatus.jsp?shw"


def parse_projects(html):
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find(id="tblProjects")
    if table is None:
        raise RuntimeError("Project table not found on the KIIFB page")
    projects = []
    for row in table.find_all("tr"):
        cells = row.find_all("td")
        if len(cells) < 6:
            continue
        onclick = row.get("onclick") or ""
        match = re.search(r"selectProject\('([^']*)'\)", onclick)
        text = [c.get_text(" ", strip=True) for c in cells]
        projects.append({
            "id": match.group(1) if match else None,
            "department": text[0],
            "name": text[1],
            "agency": text[2],
            "approved_rs": parse_amount(text[3]),
            "released_rs": parse_amount(text[4]),
            "status": text[5],
        })
    return projects, soup


def district_options(soup):
    select = soup.find("select", id="optDistrict")
    options = []
    for opt in select.find_all("option") if select else []:
        value = opt.get("value")
        name = normalize_district(opt.get_text(strip=True))
        if value and value != "0" and name:
            options.append((value, name))
    return options


def fetch_district(value):
    form = {
        "optDeptName": "0", "hidDid": "0",
        "optDistrict": value, "hidSelDist": "0",
        "optConstituency": "0", "hidSelConstituency": "0",
        "optStatus": "ALL", "hidStatus": "ALL",
        "hidSelProject": "",
    }
    resp = fetch(FILTER_URL, method="POST", data=form)
    projects, _ = parse_projects(resp.text)
    return projects


def key(p):
    return p["id"] or f"{p['name']}|{p['agency']}"


def main():
    resp = fetch(URL)
    projects, soup = parse_projects(resp.text)
    if len(projects) < 100:
        raise RuntimeError(f"Only {len(projects)} projects found; the page may have changed")

    by_key = {key(p): p for p in projects}
    for p in projects:
        p["districts"] = []

    options = district_options(soup)
    for value, name in options:
        time.sleep(2)  # be gentle with the server
        try:
            for p in fetch_district(value):
                target = by_key.get(key(p))
                if target is not None and name not in target["districts"]:
                    target["districts"].append(name)
        except Exception as exc:  # keep going if one district fails
            print(f"District {name} failed: {exc}", file=sys.stderr)

    for p in projects:
        p["districts"].sort(key=DISTRICT_ORDER.index)

    payload = {
        "source": "KIIFB project status",
        "source_url": URL,
        "collected_at": now_iso(),
        "amount_unit": "rupees",
        "project_count": len(projects),
        "districts_checked": [n for _, n in options],
        "projects": projects,
    }
    path = save_snapshot("kiifb", payload)
    tagged = sum(1 for p in projects if p["districts"])
    print(f"KIIFB: {len(projects)} projects, {tagged} with a district, saved to {path}")


if __name__ == "__main__":
    main()
