# scripts/make_fomc_ics.py
from bs4 import BeautifulSoup
import requests, re
from datetime import datetime, timedelta, date
from zoneinfo import ZoneInfo
from ics_common import ics_header, ics_footer, vevent_all_day, save_ics

FRB_URL = "https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm"

def fetch_html():
    r = requests.get(FRB_URL, timeout=30)
    r.raise_for_status()
    return r.text

def parse(html):
    # The page contains sections per year. We attempt to find current and next year meetings.
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text("\n")
    # Simple heuristic: lines with Month Day–Day, Year (or Month Day, Year) and "FOMC Meeting"
    # We'll also capture single-day virtual meetings if present.
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    pat = re.compile(r"([A-Za-z]+)\s+(\d{1,2})(?:–|-|—)?(?:\s*(\d{1,2}))?,\s*(\d{4})")
    events = []
    for i, line in enumerate(lines):
        m = pat.search(line)
        if not m: 
            continue
        mon, d1, d2, yr = m.group(1), m.group(2), m.group(3), m.group(4)
        try:
            start = datetime.strptime(f"{mon} {d1} {yr}", "%B %d %Y").date()
        except ValueError:
            continue
        end = start if not d2 else datetime.strptime(f"{mon} {d2} {yr}", "%B %d %Y").date()
        # crude filter: require "FOMC" nearby within a few lines
        nearby = "\n".join(lines[max(0,i-2):i+3])
        if "FOMC" not in nearby.upper():
            continue
        events.append((start, end))
    return events

def build_ics(events):
    out = [ics_header("FOMC (FRB)")]
    for start, end in events:
        cur = start
        while cur <= end:
            out.append(vevent_all_day(cur, "FOMC Meeting", "FRB official calendar"))
            cur += timedelta(days=1)
    out.append(ics_footer())
    return "".join(out)

def main():
    html = fetch_html()
    ev = parse(html)
    ics = build_ics(ev)
    save_ics("docs/fomc.ics", ics)

if __name__ == "__main__":
    main()
