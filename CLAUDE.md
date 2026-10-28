# Kerala Public Money – notes for Claude

A citizen-run dashboard showing where Kerala's public money goes, built only from official public data. The owner is a product designer, not a developer. Write to them in plain language: short sentences, everyday words, no jargon.

## Current state (29 Oct 2026)

- `collectors/` – Python (requests, BeautifulSoup). `run_all.py` runs each collector, records results in `data/status.json`, then `build_summary.py` writes `site/data/summary.json`.
- `site/` – plain HTML, CSS and JavaScript. No build step. It reads `data/summary.json`. Insert data as text only (see `el()` in `app.js`), never as HTML.
- `.github/workflows/collect.yml` – runs daily at 06:17 India time and on pushes to `collectors/`. It commits new data. A failed run opens a GitHub issue with the log, and `data/last_run.log` keeps the latest log.
- `data/manual/` – hand-entered figures with sources (state budget, audit findings, outcomes).
- Not yet hosted. The repository is private, so GitHub Pages needs a paid plan. Render is a free option for a static site (publish folder `site`). Check with the owner before putting anything public.
- **GitHub Actions can't run yet.** The two push runs on 28 Oct failed in 2 seconds with no runner, no log and 0 billed minutes. The owner's account had used its 2,000 included Actions minutes (12 Oct) and its monthly Actions budget (17 Oct). Both reset on 1 Nov. The minutes and budget cover all the owner's private repositories. This one is new, so other repositories used them up. A job that never starts can't open an issue, so watch GitHub's "Run failed" emails too. Fixes are the owner's call: make this repository public (Actions minutes are free for public repositories), raise the budget, or wait for the reset.
- Only a whole-run crash fails the job and opens an issue. If one collector fails, the run still passes, and the error is recorded only in `data/status.json`.

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
- **The page has gone (checked 28 Oct 2026).** Every address under `/plandashboard/`, even made-up ones, now returns a permanent redirect (301) to https://plan.lsgkerala.gov.in/. That's the "Sulekha – Plan Monitoring" welcome page, with no table. A web reader got "503 Service Unavailable". We don't know if the dashboard moved, closed, or is only hidden from visitors outside India. The collector now says so in `data/status.json`. A new source is needed.
- The Internet Archive has a good copy from 11 June 2026: https://web.archive.org/web/20260611100654/https://lsgkerala.gov.in/plandashboard/Plan/Annualplandetails.php. The Claude cloud workspace couldn't reach web.archive.org.
- Search results still show the heading "Annual Plan % of Expenditure as on 13 July 2025, 10:00AM". Always show the "as on" date.
- Columns: District, 6 budget columns (General, SCP, TSP, FC Untied, FC Tied, KLGSDP) and a budget Total, 6 matching expenditure columns and an expenditure Total, then New and SpillOver projects, then percentage. Expenditure cells look like `28.04 [ 10.02%]`.
- Certificate: the chain ends in the root "emSign Root CA - G1". Python's `certifi` list (which `requests` uses by default, as in GitHub Actions) includes it. Ubuntu 24.04's system list doesn't. The Claude cloud workspace forces the system list with `REQUESTS_CA_BUNDLE`, which causes "self-signed certificate in certificate chain". To test there, point `REQUESTS_CA_BUNDLE` at a file that joins `/root/.ccr/ca-bundle.crt` and `certifi`'s `cacert.pem`. **Never turn off certificate checks.**
- eMudhra, which runs emSign, announced on 22 Oct 2026 that it's leaving the website-certificate business. The site's certificate runs out on 16 Dec 2026, so expect a new chain.
- The parser in `collectors/lsgd_plan.py` passes on a made-up table in the layout above (14 districts, Total row, nested tables). It has still not been tested against the real HTML.

## Rules

- Show figures as published, with their source and date.
- Flags use fixed, stated rules and neutral wording ("needs a look"), never words like "misuse" or "scam".
- No personal data about private individuals. No beneficiary names.
- Don't collect sites that use a captcha (for example etenders.kerala.gov.in).
- Always identify as this project (the `USER_AGENT` in `common.py`). Never pretend to be a browser to get around a block or a redirect.

## Next steps (in order)

1. Get GitHub Actions running (the owner chooses: public repository, higher budget, or wait for 1 Nov). Then run it by hand ("Run workflow") and check `data/status.json`. Also find a new source for local government plan spending.
2. Choose hosting with the owner (Render static site, or GitHub Pages if the repository goes public).
3. Use the daily KIIFB copies to add history-based flags, such as no payment change in 12 months.
4. Add a district page ("My area") and a project page.
5. Later: news matching (Google News RSS, Kerala outlet feeds, Reddit API) and citizen checks.

Research doc: https://claude.ai/artifact/SfXqaJHpmHUyXSDjfFWXTt · Design: https://claude.ai/artifact/1NaQyeuYcPH4k39jDvVUkK
