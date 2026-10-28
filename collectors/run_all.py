"""Run every collector, record what worked in data/status.json, then rebuild
the site summary. One failing source never stops the others."""

import json
import traceback

import build_summary
import kiifb
import lsgd_plan
from common import DATA, now_iso

COLLECTORS = {
    "kiifb": kiifb.main,
    "lsgd_plan": lsgd_plan.main,
}


def main():
    status_path = DATA / "status.json"
    try:
        status = json.loads(status_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        status = {}

    for name, run in COLLECTORS.items():
        entry = status.get(name, {})
        entry["last_attempt"] = now_iso()
        try:
            run()
            entry["last_success"] = entry["last_attempt"]
            entry["last_error"] = None
        except Exception as exc:
            entry["last_error"] = f"{type(exc).__name__}: {exc}"[:500]
            traceback.print_exc()
        status[name] = entry

    status_path.write_text(json.dumps(status, indent=1), encoding="utf-8")
    build_summary.main()


if __name__ == "__main__":
    main()
