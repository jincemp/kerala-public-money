"""Combine the latest collected data and hand-entered figures into
site/data/summary.json, which the website reads."""

import json

from common import DATA, DISTRICT_ORDER, ROOT, now_iso

CRORE = 1e7  # rupees in one crore

# Fixed flag rules. Wording is neutral: a flag is a reason to ask, not a finding.
BIG_UNPAID_CR = 100


def load(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None


def cr(rupees):
    return None if rupees is None else round(rupees / CRORE, 2)


def is_approved(p):
    return "approved" in (p.get("status") or "").lower()


def kiifb_summary(raw):
    if not raw:
        return None
    projects = raw["projects"]
    approved = [p for p in projects if is_approved(p)]
    evaluating = [p for p in projects if not is_approved(p)]

    def amt(p, field):
        return p.get(field) or 0

    # Some rows show more money released than approved (one shows ₹15,805 crore
    # released against ₹236 crore approved). These look like data errors, so we
    # leave them out of the released totals and list them separately.
    def consistent(p):
        return amt(p, "released_rs") <= amt(p, "approved_rs") * 1.001

    clean = [p for p in approved if consistent(p)]
    suspect = [p for p in approved if not consistent(p)]

    total_approved = sum(amt(p, "approved_rs") for p in approved)
    clean_approved = sum(amt(p, "approved_rs") for p in clean)
    clean_released = sum(amt(p, "released_rs") for p in clean)
    with_payment = [p for p in clean if amt(p, "released_rs") > 0]
    mostly_paid = [p for p in clean if amt(p, "approved_rs") and amt(p, "released_rs") >= 0.9 * amt(p, "approved_rs")]

    def money(rs):
        return f"₹{rs / CRORE:,.0f} cr"

    share = 100 * clean_released / clean_approved if clean_approved else None
    pipeline = [
        {"label": "Under evaluation", "value": f"{len(evaluating):,}", "sub": "projects waiting for approval"},
        {"label": "Approved", "value": money(total_approved), "sub": f"{len(approved):,} projects"},
        {"label": "Money released", "value": money(clean_released),
         "sub": f"{share:.0f}% of their approved amount, to {len(with_payment):,} projects" if share is not None else ""},
        {"label": "Mostly paid", "value": f"{len(mostly_paid):,}",
         "sub": "projects with 90% or more of their approved amount released"},
    ]

    # Count a project in a district only when KIIFB lists it under that district
    # alone. Projects listed under several districts are counted separately.
    by_district = {}
    for name in DISTRICT_ORDER:
        ps = [p for p in approved if p.get("districts") == [name]]
        cs = [p for p in ps if consistent(p)]
        by_district[name] = {
            "count": len(ps),
            "approved_cr": cr(sum(amt(p, "approved_rs") for p in ps)),
            "released_cr": cr(sum(amt(p, "released_rs") for p in cs)),
        }
    multi = [p for p in approved if len(p.get("districts", [])) != 1]

    def flag_item(p):
        return {
            "name": p["name"],
            "agency": p["agency"],
            "district": ", ".join(p.get("districts", [])) or None,
            "approved_cr": cr(amt(p, "approved_rs")),
            "released_cr": cr(amt(p, "released_rs")),
        }

    unpaid = sorted(
        (p for p in clean if amt(p, "approved_rs") >= BIG_UNPAID_CR * CRORE and amt(p, "released_rs") == 0),
        key=lambda p: -amt(p, "approved_rs"))
    suspect_sorted = sorted(suspect, key=lambda p: -(amt(p, "released_rs") - amt(p, "approved_rs")))

    flag_groups = [
        {
            "rule": f"Approved for ₹{BIG_UNPAID_CR} crore or more, no money released yet",
            "count": len(unpaid),
            "items": [flag_item(p) for p in unpaid[:4]],
        },
        {
            "rule": "More money released than approved (possible data error on KIIFB's site)",
            "count": len(suspect),
            "items": [flag_item(p) for p in suspect_sorted[:4]],
        },
    ]

    return {
        "source_url": raw["source_url"],
        "collected_at": raw["collected_at"],
        "project_count": len(approved),
        "evaluating_count": len(evaluating),
        "total_approved_cr": cr(total_approved),
        "total_released_cr": cr(clean_released),
        "released_note": (
            f"Released totals leave out {len(suspect)} projects where KIIFB's list shows "
            f"more released than approved."),
        "headline_note": (
            "KIIFB's homepage gives a lower total of ₹60,102 crore approved. "
            "We show the sum of its published project list."),
        "pipeline": pipeline,
        "by_district": by_district,
        "multi_district": {"count": len(multi), "approved_cr": cr(sum(amt(p, "approved_rs") for p in multi))},
        "flag_groups": flag_groups,
    }


def main():
    manual = DATA / "manual"
    summary = {
        "generated_at": now_iso(),
        "district_order": DISTRICT_ORDER,
        "state_figures": load(manual / "state_figures.json"),
        "audits": load(manual / "audit_findings.json") or [],
        "outcomes": load(manual / "outcomes.json") or [],
        "kiifb": kiifb_summary(load(DATA / "kiifb" / "latest.json")),
        "lsgd_plan": load(DATA / "lsgd_plan" / "latest.json"),
    }
    out = ROOT / "site" / "data" / "summary.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
