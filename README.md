# Kerala Public Money

A citizen-run dashboard that shows where Kerala's public money goes. It uses only official public data. This is not a government website.

## What it does

Every day, a scheduled job on GitHub:

1. Collects the KIIFB project list from [kiifb.org](https://www.kiifb.org/prjStatus.jsp), including which districts each project is listed under.
2. Collects local government plan spending from the [LSGD Plan Dashboard](https://lsgkerala.gov.in/plandashboard/Plan/Annualplandetails.php).
3. Saves a dated copy of each in `data/`, so changes can be tracked over time.
4. Rebuilds `site/data/summary.json`, which the website reads.

Figures that change rarely, such as the state budget and audit findings, are entered by hand in `data/manual/`. Each one has its source.

## Folders

| Folder | What's in it |
| --- | --- |
| `collectors/` | Python scripts that collect and combine the data |
| `data/kiifb/`, `data/lsgd_plan/` | One file per day, plus `latest.json` |
| `data/manual/` | Hand-entered figures with sources |
| `data/status.json` | When each source last worked, and any error |
| `site/` | The website: plain HTML, CSS and JavaScript |

## Known data problems

- About a quarter of approved KIIFB projects show more money released than approved. We leave these out of released totals and list them as possible data errors.
- KIIFB's homepage gives ₹60,102 crore approved, but its project list adds up to more. We show the list as published.
- The LSGD Plan Dashboard showed data "as on 13 July 2025" when this project started. The site shows that date next to every figure.

## Run it yourself

```
pip install -r collectors/requirements.txt
cd collectors
python run_all.py
cd ../site
python -m http.server 8000
```

Then open http://localhost:8000.

## Rules we follow

- Show figures as published, with the source and date.
- Flag projects only with fixed, stated rules. A flag is a reason to ask questions, not a finding of wrongdoing.
- No personal data about private individuals.
- Collect each page once a day, with a pause between requests.
