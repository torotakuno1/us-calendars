# scripts/make_earnings_ics.py
# Optional: enable if you want API-based earnings instead of Traders' list
import os, requests, hashlib, csv
from datetime import datetime, timedelta, timezone
from ics_common import ics_header, ics_footer, vevent_all_day, save_ics

FINNHUB_TOKEN = os.environ.get("FINNHUB_TOKEN","")
WATCHLIST_CSV = "data/watchlist.csv"  # one symbol per line (e.g., AAPL)

def uid(*xs): 
    return hashlib.md5("|".join(xs).encode()).hexdigest()+"@earnings"

def load_watchlist():
    syms = []
    try:
        with open(WATCHLIST_CSV, encoding="utf-8") as f:
            for line in f:
                s = line.strip()
                if s and not s.startswith("#"):
                    syms.append(s.upper())
    except FileNotFoundError:
        pass
    return set(syms)

def fetch(from_date, to_date):
    url = f"https://finnhub.io/api/v1/calendar/earnings?from={from_date}&to={to_date}&token={FINNHUB_TOKEN}"
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    return r.json().get("earningsCalendar", [])

def build_ics(rows):
    out = [ics_header("Earnings (Finnhub)")]
    for x in rows:
        d = x.get("date")
        sym = x.get("symbol") or ""
        if not d or not sym:
            continue
        title = f"{sym} Earnings"
        desc = f"when={x.get('hour') or x.get('time')}; epsEst={x.get('epsEstimate')}"
        # Earnings 'date' is treated as all-day; exact time varies (BMO/AMC)
        from datetime import datetime, timedelta
        dt_ = datetime.strptime(d, "%Y-%m-%d").date()
        out.append(vevent_all_day(dt_, title, desc))
    out.append(ics_footer())
    return "".join(out)

def main():
    from datetime import date
    today = date.today()
    from_date = (today - timedelta(days=1)).strftime("%Y-%m-%d")
    to_date = (today + timedelta(days=90)).strftime("%Y-%m-%d")
    watch = load_watchlist()
    if not FINNHUB_TOKEN:
        print("WARN: FINNHUB_TOKEN not set; skipping earnings.")
        return
    all_rows = fetch(from_date, to_date)
    if watch:
        rows = [r for r in all_rows if (r.get("symbol") or "").upper() in watch]
    else:
        rows = all_rows
    ics = build_ics(rows)
    save_ics("docs/earnings.ics", ics)

if __name__ == "__main__":
    main()
