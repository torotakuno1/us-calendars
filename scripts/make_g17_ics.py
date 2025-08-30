# scripts/make_g17_ics.py
import csv
from datetime import datetime, timedelta
from ics_common import ics_header, ics_footer, vevent_with_time, save_ics, ET

# CSV format: YYYY-MM-DD,HH:MM,Note
CSV = "data/g17_schedule_2025.csv"

def load_rows(path):
    rows = []
    try:
        with open(path, newline="", encoding="utf-8") as f:
            for row in csv.reader(f):
                if not row or row[0].startswith("#"):
                    continue
                d = datetime.strptime(row[0].strip(), "%Y-%m-%d").date()
                tm = row[1].strip() if len(row)>1 and row[1].strip() else "09:15"
                note = row[2].strip() if len(row)>2 else ""
                rows.append((d, tm, note))
    except FileNotFoundError:
        pass
    return rows

def build_ics(year):
    rows = load_rows(CSV)
    out = [ics_header(f"FRB G.17 Industrial Production {year}")]
    for d, tm, note in rows:
        if d.year != year: 
            continue
        hh, mm = map(int, tm.split(":"))
        start = datetime(d.year, d.month, d.day, hh, mm, tzinfo=ET)
        end = start + timedelta(minutes=45)
        out.append(vevent_with_time(start, end, "Industrial Production (G.17)", note))
    out.append(ics_footer())
    return "".join(out)

def main():
    from datetime import date
    y = date.today().year
    ics = build_ics(y)
    save_ics("docs/g17_industrial_production.ics", ics)

if __name__ == "__main__":
    main()
