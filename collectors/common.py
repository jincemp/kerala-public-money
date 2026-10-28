"""Shared helpers for the data collectors."""

import datetime as dt
import json
import re
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

USER_AGENT = (
    "kerala-public-money/0.1 (citizen transparency project; "
    "collects public pages once a day)"
)

# Kerala's 14 districts, north to south, with spellings seen on official sites.
DISTRICTS = [
    ("Kasaragod", ["kasaragod", "kasargod", "kasarkode", "kasargode"]),
    ("Kannur", ["kannur", "cannanore"]),
    ("Wayanad", ["wayanad", "wynad"]),
    ("Kozhikode", ["kozhikode", "calicut"]),
    ("Malappuram", ["malappuram"]),
    ("Palakkad", ["palakkad", "palghat"]),
    ("Thrissur", ["thrissur", "trichur"]),
    ("Ernakulam", ["ernakulam"]),
    ("Idukki", ["idukki"]),
    ("Kottayam", ["kottayam"]),
    ("Alappuzha", ["alappuzha", "alleppey"]),
    ("Pathanamthitta", ["pathanamthitta"]),
    ("Kollam", ["kollam", "quilon"]),
    ("Thiruvananthapuram", ["thiruvananthapuram", "trivandrum", "tvm"]),
]
DISTRICT_ORDER = [d for d, _ in DISTRICTS]


def normalize_district(text):
    """Return the standard district name for a label, or None."""
    if not text:
        return None
    key = re.sub(r"[^a-z]", "", text.lower())
    for name, variants in DISTRICTS:
        if any(key.startswith(v) for v in variants):
            return name
    return None


def parse_amount(text):
    """Turn '1,234.56' or '₹ 1,234' into a float. Returns None if empty."""
    if text is None:
        return None
    cleaned = re.sub(r"[^0-9.\-]", "", str(text))
    if cleaned in ("", ".", "-"):
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


def today():
    return dt.datetime.now(dt.timezone(dt.timedelta(hours=5, minutes=30))).date().isoformat()


def now_iso():
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def fetch(url, method="GET", **kwargs):
    headers = {"User-Agent": USER_AGENT}
    headers.update(kwargs.pop("headers", {}))
    resp = requests.request(method, url, headers=headers, timeout=60, **kwargs)
    resp.raise_for_status()
    return resp


def save_snapshot(source, payload, raw_html=None):
    """Save today's snapshot and update latest.json for a source."""
    folder = DATA / source
    folder.mkdir(parents=True, exist_ok=True)
    day = today()
    text = json.dumps(payload, ensure_ascii=False, indent=1)
    (folder / f"{day}.json").write_text(text, encoding="utf-8")
    (folder / "latest.json").write_text(text, encoding="utf-8")
    if raw_html is not None:
        raw = folder / "raw"
        raw.mkdir(exist_ok=True)
        (raw / f"{day}.html").write_text(raw_html, encoding="utf-8")
    return folder / f"{day}.json"
