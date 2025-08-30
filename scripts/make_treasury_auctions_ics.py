# scripts/make_treasury_auctions_ics.py
import requests, datetime as dt
from zoneinfo import ZoneInfo
from ics_common import ics_header, ics_footer, vevent_with_time, save_ics, ET

# Docs: https://api.fiscaldata.treasury.gov/services/api/fiscal_service/
# We'll use the "auction_schedules" endpoint as a starting point (Upcoming Auctions).
API_URL = "https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v2/accounting/od/auction_schedules"

def fetch(start_date, end_date):
    params = {
        "filter": f"auction_date:gte:{start_date},auction_date:lte:{end_date}",
        "sort": "auction_date",
        "page[number]": 1,
        "page[size]": 1000
    }
    r = requests.get(API_URL, params=params, timeout=60)
    r.raise_for_status()
    return r.json().get("data", [])

def to_dt_et(date_str, time_str="13:00"):
    # Many announcements/auctions occur around 11:00-13:00 ET; this is a placeholder.
    # Adjust if the endpoint provides specific time fields.
    y, m, d = map(int, date_str.split("-"))
    hh, mm = map(int, time_str.split(":"))
    return dt.datetime(y, m, d, hh, mm, tzinfo=ET)

def build_ics(rows):
    out = [ics_header("Treasury Auctions (Upcoming)")]
    for x in rows:
        d = x.get("auction_date")
        sec = x.get("security_type") or ""
        term = x.get("term") or x.get("security_term") or ""
        title = f"Treasury Auction: {sec} {term}".strip()
        start = to_dt_et(d, "13:00")
        end = start + dt.timedelta(hours=1)
        desc = f"Source: FiscalData Treasury | CUSIP={x.get('cusip') or ''}"
        out.append(vevent_with_time(start, end, title, desc))
    out.append(ics_footer())
    return "".join(out)

def main():
    today = dt.date.today()
    end = today + dt.timedelta(days=120)
    rows = fetch(today.isoformat(), end.isoformat())
    ics = build_ics(rows)
    save_ics("docs/treasury_auctions.ics", ics)

if __name__ == "__main__":
    main()
