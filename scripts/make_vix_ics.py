# scripts/make_vix_ics.py
import csv
from datetime import datetime, timedelta
from ics_common import ics_header, ics_footer, vevent_all_day, save_ics

# CSV format: YYYY-MM-DD,Note  (final settlement date per CFE calendar; usually Wednesdays with holiday exceptions)
CSV = "data/vix_settlement_2025.csv"

def load_dates(path):
    out = []
    try:
        with open(path, newline="", encoding="utf-8") as f:
            for row in csv.reader(f):
                if not row or row[0].startswith("#"):
                    continue
                d = datetime.strptime(row[0].strip(), "%Y-%m-%d").date()
                note = row[1].strip() if len(row) > 1 else ""
                out.append((d, note))
    except FileNotFoundError:
        pass
    return out

def build_ics(year):
    rows = load_dates(CSV)
    out = [ics_header(f"VIX Futures Final Settlement {year}")]
    for d, note in rows:
        if d.year != year: 
            continue
        title = "VIX Futures Final Settlement"
        desc = f"CFE Calendar. {note}".strip()
        out.append(vevent_all_day(d, title, desc))
    out.append(ics_footer())
    return "".join(out)

def main():
    from datetime import date
    y = date.today().year
    ics = build_ics(y)
    save_ics("docs/vix_settlement.ics", ics)

if __name__ == "__main__":
    main()
