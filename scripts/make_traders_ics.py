# scripts/make_traders_ics.py
import re, hashlib, requests
from bs4 import BeautifulSoup
from datetime import datetime as dt, timedelta, timezone
from ics_common import ics_header, ics_footer, vevent_all_day, vevent_with_time, save_ics

BASE_URL = "https://www.traders.co.jp/market_fo/schedule_m"
TZID = "Asia/Tokyo"

def normalize_text(s):
    import re
    return re.sub(r'\s+', ' ', s.strip())

def make_uid(date_str, title):
    key = (date_str + "|" + title).encode("utf-8")
    return hashlib.md5(key).hexdigest() + "@traders-schedule"

def fetch_html():
    r = requests.get(BASE_URL, timeout=30)
    r.raise_for_status()
    return r.text

def parse_month_and_items(html):
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text("\n")
    lines = [l.rstrip() for l in text.splitlines() if l.strip()]

    # 月見出し：例「2025年08月」
    month_pat = re.compile(r'(\d{4})年(\d{2})月')
    year, month = None, None
    for i, line in enumerate(lines):
        m = month_pat.search(line)
        if m:
            year, month = int(m.group(1)), int(m.group(2))
            break
    if not year:
        raise RuntimeError("月が見つかりませんでした")

    day_pat = re.compile(r'^(\d{1,2})[（(].+[)）]')
    time_pat = re.compile(r'（(\d{1,2}:\d{2})）')  # 全角括弧の中のHH:MM
    events = []
    i = 0
    while i < len(lines):
        line = lines[i]
        md = day_pat.match(line)
        if md:
            day = int(md.group(1))
            date_obj = dt(year, month, day).date()

            j = i + 1
            daily_blocks = []
            while j < len(lines) and not day_pat.match(lines[j]):
                daily_blocks.append(lines[j])
                j += 1

            block_title = None
            for blk in daily_blocks:
                s = normalize_text(blk)
                if s.startswith("《") and s.endswith("》"):
                    block_title = s.strip("《》")
                    continue
                if not s:
                    continue

                tm = time_pat.search(s)
                if tm:
                    hhmm = tm.group(1)
                    title = re.sub(time_pat, "", s).strip()
                    events.append(("time", date_obj, hhmm, title, block_title or ""))
                else:
                    if block_title and "決算" in block_title:
                        for name in re.split(r'[、,]', s):
                            name = name.strip()
                            if name:
                                title = f"{block_title}: {name}"
                                events.append(("all", date_obj, None, title, ""))
                    else:
                        events.append(("all", date_obj, None, s, block_title or ""))

            i = j
        else:
            i += 1

    return year, month, events

def build_ics(html):
    y, m, events = parse_month_and_items(html)
    out = [ics_header(f"Traders US (Parsed) {y}-{m:02d}")]
    for kind, date_obj, hhmm, title, desc in events:
        if kind == "time":
            hh, mm = map(int, hhmm.split(":"))
            # Treat as JST then convert to ET by simply storing local time as floating (iCal consumers convert)
            # We emit as all-day or set ET 1-hour window; here we use all-day for ambiguous items:
            # To keep simple and timezone-safe, we'll use all-day for now.
            out.append(vevent_all_day(date_obj, title, desc))
        else:
            out.append(vevent_all_day(date_obj, title, desc))
    out.append(ics_footer())
    return "".join(out)

def main():
    html = fetch_html()
    ics = build_ics(html)
    save_ics("docs/traders_us.ics", ics)

if __name__ == "__main__":
    main()
