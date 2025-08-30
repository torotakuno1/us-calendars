# scripts/make_opex_ics.py
import csv
from datetime import date, timedelta, datetime
from zoneinfo import ZoneInfo
from ics_common import ics_header, ics_footer, vevent_all_day, save_ics, third_friday

# Exceptions CSV format:
# YYYY-MM,YYYY-MM-DD  (month,labelled 3rd Friday; actual expiration date after holiday adjustment)
EXCEPTIONS_CSV = "data/opex_exceptions_2025.csv"

def load_exceptions(path):
    ex = {}
    try:
        with open(path, newline="", encoding="utf-8") as f:
            for row in csv.reader(f):
                if not row or row[0].startswith("#"):
                    continue
                ym, ymd = row[0].strip(), row[1].strip()
                ex[ym] = datetime.strptime(ymd, "%Y-%m-%d").date()
    except FileNotFoundError:
        pass
    return ex

def build_ics(year):
    ex = load_exceptions(EXCEPTIONS_CSV)
    out = [ics_header(f"OPEX (US Options Expiration) {year}")]
    for m in range(1,13):
        ym = f"{year}-{m:02d}"
        exp = ex.get(ym, third_friday(year, m))
        out.append(vevent_all_day(exp, "US Equity/ETF Options Expiration", "Standard monthly expiration (3rd Friday) with holiday exceptions if provided."))
    out.append(ics_footer())
    return "".join(out)

def main():
    from datetime import date
    y = date.today().year
    ics = build_ics(y)
    save_ics("docs/opex_us.ics", ics)

if __name__ == "__main__":
    main()
