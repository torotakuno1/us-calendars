# scripts/make_weekly_ui_ics.py
import csv
from datetime import date, timedelta, datetime
from zoneinfo import ZoneInfo
from ics_common import ics_header, ics_footer, vevent_with_time, save_ics, ET

# Exceptions CSV format:
# YYYY-MM-DD,HH:MM,Note   (for weeks that shift due to holidays; default is Thursday 08:30 ET)
CSV = "data/ui_exceptions_2025.csv"

def default_time():
    return (8,30)  # 08:30 ET

def daterange(start, end):
    cur = start
    while cur <= end:
        yield cur
        cur += timedelta(days=1)

def build_ics(year):
    out = [ics_header(f"Weekly Initial Jobless Claims {year}")]
    # Iterate Thursdays in year
    d = date(year,1,1)
    # find first Thursday
    while d.weekday() != 3:
        d += timedelta(days=1)
    end = date(year,12,31)
    # Load exceptions
    ex = {}
    try:
        import csv
        with open(CSV, newline="", encoding="utf-8") as f:
            for row in csv.reader(f):
                if not row or row[0].startswith("#"):
                    continue
                exd = datetime.strptime(row[0].strip(), "%Y-%m-%d").date()
                time = row[1].strip() if len(row)>1 and row[1].strip() else "08:30"
                note = row[2].strip() if len(row)>2 else ""
                ex[exd] = (time, note)
    except FileNotFoundError:
        pass

    while d <= end:
        if d in ex:
            hh, mm = map(int, ex[d][0].split(":"))
            note = ex[d][1]
        else:
            hh, mm = default_time()
            note = ""
        start = datetime(d.year, d.month, d.day, hh, mm, tzinfo=ET)
        endt = start + timedelta(minutes=30)
        title = "Initial Jobless Claims (Weekly)"
        desc = ("US Department of Labor (ETA) weekly release. " + note).strip()
        out.append(vevent_with_time(start, endt, title, desc))
        d += timedelta(days=7)
    out.append(ics_footer())
    return "".join(out)

def main():
    from datetime import date
    y = date.today().year
    ics = build_ics(y)
    save_ics("docs/weekly_initial_claims.ics", ics)

if __name__ == "__main__":
    main()
