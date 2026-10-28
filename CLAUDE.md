# Kerala Public Money – notes for Claude

A citizen-run dashboard showing where Kerala's public money goes, built only from official public data. The owner is a product designer, not a developer. Write to them in plain language: short sentences, everyday words, no jargon.

## Current state (29 Oct 2026)

- `collectors/` – Python (requests, BeautifulSoup). `run_all.py` runs each collector, records results in `data/status.json`, then `build_summary.py` writes `site/data/summary.json`.
- `site/` – plain HTML, CSS and JavaScript. No build step. It reads `data/summary.json`. Insert data as text only (see `el()` in `app.js`), never as HTML.
- `.github/workflows/collect.yml` – runs daily at 06:17 India time and on pushes to `collectors/`. It commits new data. A failed run opens a GitHub issue with the log, and `data/last_run.log` keeps the latest log.
- `data/manual/` – hand-entered figures with sources (state budget, audit findings, outcomes).
- Not yet hosted. The repository is private, so GitHub Pages needs a paid plan. Render is a free option for a static site (publish folder `site`). Check with the owner before putting anything public.
- The first GitHub Actions runs had not been confirmed when this file was written. Check `data/status.json`, `data/last_run.log` and open issues first.

## Sources and their quirks

### KIIFB – https://www.kiifb.org/prjStatus.jsp
- One table, `#tblProjects`, with about 1,400 rows: department, project name, implementing agency (SPV), approved amount, payment released and status ("Project Approved" or "Project Under Evaluation").
- Amounts are in **rupees**. Divide by 1e7 for crore.
- Each row has `onclick="selectProject('<id>')"`. Use that id to track projects over time.
- There's no district column. To get districts, POST to `prjStatus.jsp?shw` with `optDistrict=1..14` (1 is Thiruvananthapuram, 14 is Kasaragod) and the other fields set to 0 or ALL. Some projects appear under several districts, and two appear under all 14.
- About 281 approved projects show more released than approved. One shows ₹15,805 crore released against ₹236 crore approved. Treat these as likely data errors: leave them out of released totals and list them separately.
- KIIFB's homepage says ₹60,102 crore approved, but the list adds up to about ₹93,101 crore. Show the list as published, with a note.
- Be polite: pause 2 seconds between requests and run once a day.

### LSGD Plan Dashboard – https://lsgkerala.gov.in/plandashboard/Plan/Annualplandetails.php
- Shows local government plan budget and spending by district, in crore.
- When last read (through a web reader), the heading said "as on 13 July 2025". The data may be stale, so always show the "as on" date.
- Columns: District, 6 budget columns (General, SCP, TSP, FC Untied, FC Tied, KLGSDP) ending in Total, 6 matching expenditure columns ending in Total, then New and SpillOver projects, then percentage. Expenditure cells look like `28.04 [ 10.02%]`.
- The site's TLS certificate chain failed to verify in the Claude cloud workspace ("self-signed certificate in certificate chain"). It may also fail in GitHub Actions. If so, add the missing intermediate certificate to a bundle. **Never turn off certificate checks.**
- The parser in `collectors/lsgd_plan.py` has not yet been tested against the real HTML.

## Rules

- Show figures as published, with their source and date.
- Flags use fixed, stated rules and neutral wording ("needs a look"), never words like "misuse" or "scam".
- No personal data about private individuals. No beneficiary names.
- Don't collect sites that use a captcha (for example etenders.kerala.gov.in).

## Next steps (in order)

1. Confirm the GitHub Actions run works, including the LSGD collector and any certificate problem.
2. Choose hosting with the owner (Render static site, or GitHub Pages if the repository goes public).
3. Use the daily KIIFB copies to add history-based flags, such as no payment change in 12 months.
4. Add a district page ("My area") and a project page.
5. Later: news matching (Google News RSS, Kerala outlet feeds, Reddit API) and citizen checks.

Research doc: https://claude.ai/artifact/SfXqaJHpmHUyXSDjfFWXTt · Design: https://claude.ai/artifact/1NaQyeuYcPH4k39jDvVUkK
