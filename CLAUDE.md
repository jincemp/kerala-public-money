# Kerala Public Money – notes for Claude

A citizen-run dashboard showing where Kerala's public money goes, built only from official public data. The owner is a product designer, not a developer. Write to them in plain language: short sentences, everyday words, no jargon.

## Current state (29 Oct 2026)

- `collectors/` – Python (requests, BeautifulSoup). `run_all.py` runs each collector, records results in `data/status.json`, then `build_summary.py` writes `site/data/summary.json`.
- `site/` – plain HTML, CSS and JavaScript. No build step. It reads `data/summary.json`. Insert data as text only (see `el()` in `app.js`), never as HTML.
- `.github/workflows/collect.yml` – runs daily at 06:17 India time and on pushes to `collectors/`. It commits new data. A failed run opens a GitHub issue with the log, and `data/last_run.log` keeps the latest log.
- `data/manual/` – hand-entered figures with sources (state budget, audit findings, outcomes).
- Not yet hosted. The repository has been public since 28 Oct 2026, so GitHub Pages is free. Render is another free option for a static site (publish folder `site`). Choose with the owner.
- **GitHub Actions works since the repository went public (28 Oct).** The first good run (started by hand, 28 Oct 19:53 UTC) took about a minute. KIIFB collected 1,408 projects (1,401 with a district). LSGD failed because its page has gone (see below). Before that, two runs failed in 2 seconds with no runner and no log: the account had used up its Actions minutes for private repositories. A job that never starts can't open an issue, so if that happens again, look at GitHub's "Run failed" emails.
- Only a whole-run crash fails the job and opens an issue. If one collector fails, the run still passes, and the error is recorded only in `data/status.json`.

## Sources and their quirks

### KIIFB – https://www.kiifb.org/prjStatus.jsp
- One table, `#tblProjects`, with about 1,400 rows: department, project name, implementing agency (SPV), approved amount, payment released and status ("Project Approved" or "Project Under Evaluation").
- Amounts are in **rupees**. Divide by 1e7 for crore.
- Each row has `onclick="selectProject('<id>')"`. Use that id to track projects over time.
- There's no district column. To get districts, POST to `prjStatus.jsp?shw` with `optDistrict=1..14` (1 is Thiruvananthapuram, 14 is Kasaragod) and the other fields set to 0 or ALL. Some projects appear under several districts, and two appear under all 14.
- About 281 approved projects show more released than approved. One shows ₹15,805 crore released against ₹236 crore approved. Treat these as likely data errors: leave them out of released totals and list them separately.
- The list includes a placeholder row, "Dummy Sub Project for compensating the Conditionally Approved amount 5200 Cr…" (KSEBL Transgrid, ₹2,507 crore approved, nothing released). On 28 Oct it topped the "no money released" flags, and it's counted in the approved total. Decide with the owner how to show it.
- KIIFB's homepage says ₹60,102 crore approved, but the list adds up to about ₹93,101 crore. Show the list as published, with a note.
- Be polite: pause 2 seconds between requests and run once a day.

### LSGD Plan Dashboard – https://lsgkerala.gov.in/plandashboard/Plan/Annualplandetails.php
- Shows local government plan budget and spending by district, in crore.
- **The page has gone (checked 28 Oct 2026).** Every address under `/plandashboard/`, even made-up ones, now returns a permanent redirect (301) to https://plan.lsgkerala.gov.in/. That's the "Sulekha – Plan Monitoring" welcome page, with no table. A web reader got "503 Service Unavailable". The owner checked from India in their browser and also landed on the Sulekha login page, so it has moved or closed for everyone. The collector now says so in `data/status.json`. A new source is needed.
- Search results show dashboard pages dated up to "as on 13 October 2026" (for example `ExpenditureLBwise.php?id=5`), so it went away in late October 2026. The redirect keeps `?id=`, so it may have moved into Sulekha. Asking LSGD or Information Kerala Mission (IKM) where it went is the cheapest fix.

### Sulekha "View Projects" – https://plan.lsgkerala.gov.in/formulation/Public.aspx
Explored on 28 Oct 2026 with 26 polite requests. Saved pages aren't in the repository.
- Official (IKM's Sulekha), public, no captcha, no login. Current: 2026-27 spending is being filled in. No "as on" date anywhere, so show "as seen on <collection date>". The PDF footer time isn't an "as on" date.
- ASP.NET form. Every request is a POST to `Public.aspx` that sends back the hidden fields from the last response (`__VIEWSTATE`, `__VIEWSTATEGENERATOR`, `__VIEWSTATEENCRYPTED`, `__EVENTVALIDATION`) and keeps the `ASP.NET_SessionId_Sulekha` cookie. Our User-Agent gets the page without JavaScript, so set `__EVENTTARGET` and `__EVENTARGUMENT` yourself.
  1. `drpYear` (30 = 2026-2027, 29 = 2025-2026 … 16 = 2012-2013) plus `drpType` (1 District Panchayat, 2 Block Panchayat, 3 Municipality, 4 Corporation, 5 Grama Panchayat), with `__EVENTTARGET=drpType`. Returns `#gvState`, "DPC Approved Details": per district, the number of councils, the number of projects, and the approved amount in **lakh**, split into Productive, Service and Infrastructure, plus a Total row. District spelling "Kasargod". Corporations have only 6 rows.
  2. `__EVENTTARGET=gvState`, `__EVENTARGUMENT=Select$<row position>`. Returns `#gvStat`: the councils in that district, with the same approved columns.
  3. `__EVENTTARGET=gvStat`, `Select$<row position>`. Returns `#gvProjects`: No., Project Name (Malayalam), Formulation (approved, **rupees**) and Expense (spent, **rupees**), 20 per page. More pages: `__EVENTTARGET=gvProjects`, `Page$<n>`. "No." has gaps, so check a list is complete by its sums. In one council, project Formulation added up exactly to the council total.
  4. `gvProjects` `Select$<row>` redirects to a project PDF on `sgwapi.lsgkerala.gov.in`. It names officials and its Malayalam text extracts garbled. Don't collect these.
- **Spending exists only per project.** District spending would mean every project page: about 13,600 requests for 2026-27, or roughly 20 hours. That's not polite to run daily, and it's longer than GitHub Actions' 6-hour job limit. Approved amounts by district and council type cost 6 requests a year, or about 68 with every council.
- No split by fund (General, SCP, TSP, FC, KLGSDP), only by sector. "Formulation" is the approved project cost from all sources, so it's much bigger than the state's plan grant. Some projects are shares passed to other councils, so don't add council types into one state total. Show each type as published.
- Project names are activities, schemes and places, with no beneficiary names. Individual schemes (housing, cows, scholarships) appear as one total line.
- Same certificate as lsgkerala.gov.in (see below).

### Other official sources checked (28 Oct 2026)
None gives current spending by district. Only the old dashboard did, and the news quoted it.
- Budget by council, grouped by district: Budget Appendix IV 2026-27. The revised June 2026 version is the current one (Development Fund ₹8,655.45 crore), but its council pages are scanned, so they need OCR: https://www.niyamasabha.org/codes/16kla/session_1/Revised%20Budget%20Documents_June%202026/14.%20Appendix%20IV%202026-27.pdf. The January version has a text layer, but its figures have been replaced (₹10,189 crore): https://www.niyamasabha.org/codes/15kla/Session_16/Budget%20Documents/20.%20Appendix%20IV_2026-27.pdf
- Spending, whole state by council type and General/SCP/TSP, once a year: Economic Review 2025 Vol 2, Appendix 12.1.1 (2024-25: ₹7,746.29 crore released, ₹6,792.60 crore spent, 87.69%): https://spb.kerala.gov.in/sites/default/files/2026-01/ER%202025%20Volume%202%20Eng%20final.pdf
- SCP and TSP spending 2016-17 to 2025-26: Assembly answer U1644, 1 July 2026: https://niyamasabha.org/codes/16kla/session_1/ans/u01644-010726-01-16.pdf
- PlanSpace (https://www.planspace.kerala.gov.in/) may show current state-wide spending percentages, but it returned 403 to the project. dop.lsgkerala.gov.in also returned 403. KILA has a Cloudflare bot check. Saankhya needs a login. Don't try to get around any of these.
- The LSGD portal's "Plan progress" posts stop at 31 March 2018.
- The Internet Archive has a good copy from 11 June 2026: https://web.archive.org/web/20260611100654/https://lsgkerala.gov.in/plandashboard/Plan/Annualplandetails.php. The Claude cloud workspace couldn't reach web.archive.org.
- Search results still show the heading "Annual Plan % of Expenditure as on 13 July 2025, 10:00AM". Always show the "as on" date.
- Columns: District, 6 budget columns (General, SCP, TSP, FC Untied, FC Tied, KLGSDP) and a budget Total, 6 matching expenditure columns and an expenditure Total, then New and SpillOver projects, then percentage. Expenditure cells look like `28.04 [ 10.02%]`.
- Certificate: the chain ends in the root "emSign Root CA - G1". Python's `certifi` list (which `requests` uses by default, as in GitHub Actions) includes it. Ubuntu 24.04's system list doesn't. The Claude cloud workspace forces the system list with `REQUESTS_CA_BUNDLE`, which causes "self-signed certificate in certificate chain". To test there, point `REQUESTS_CA_BUNDLE` at a file that joins `/root/.ccr/ca-bundle.crt` and `certifi`'s `cacert.pem`. The 28 Oct Actions run reached the site with no certificate error. But `certifi` has changed back and forth: 2026.10.18 has no emSign root, and 2026.10.23 has "emSign Root CA - G1". `requirements.txt` doesn't pin `certifi`, so a run could install a version that fails on every `*.lsgkerala.gov.in` site. Consider pinning a known-good version. **Never turn off certificate checks.**
- eMudhra, which runs emSign, announced on 22 Oct 2026 that it's leaving the website-certificate business. The site's certificate runs out on 16 Dec 2026, so expect a new chain.
- The parser in `collectors/lsgd_plan.py` passes on a made-up table in the layout above (14 districts, Total row, nested tables). It has still not been tested against the real HTML.

## Rules

- Show figures as published, with their source and date.
- Flags use fixed, stated rules and neutral wording ("needs a look"), never words like "misuse" or "scam".
- No personal data about private individuals. No beneficiary names.
- Don't collect sites that use a captcha (for example etenders.kerala.gov.in).
- Always identify as this project (the `USER_AGENT` in `common.py`). Never pretend to be a browser to get around a block or a redirect.

## Next steps (in order)

1. Replace the LSGD collector. The owner chooses between: asking LSGD or IKM where the dashboard went; collecting Sulekha approved amounts daily, with spending later (a monthly rotation, or one area on demand); or the yearly Appendix IV budget.
2. Choose hosting with the owner (Render static site, or GitHub Pages if the repository goes public).
3. Use the daily KIIFB copies to add history-based flags, such as no payment change in 12 months.
4. Add a district page ("My area") and a project page.
5. Later: news matching (Google News RSS, Kerala outlet feeds, Reddit API) and citizen checks.

Research doc: https://claude.ai/artifact/SfXqaJHpmHUyXSDjfFWXTt · Design: https://claude.ai/artifact/1NaQyeuYcPH4k39jDvVUkK
