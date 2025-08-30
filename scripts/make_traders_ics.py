# scripts/make_traders_ics.py 〔JST時刻付き版〕
import re, hashlib, requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from ics_common import (
    ics_header, ics_footer, vevent_all_day, vevent_with_time_tz, save_ics
)

BASE_URL = "https://www.traders.co.jp/market_fo/schedule_m"
JST = ZoneInfo("Asia/Tokyo")

def normalize_text(s):
    return re.sub(r"\s+", " ", s.strip())

def fetch_html():
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; CalendarsBot/1.0; +https://github.com/your/repo)"
    }
    r = requests.get(BASE_URL, headers=headers, timeout=30)
    r.raise_for_status()
    return r.text

def parse_month_and_items(html):
    """
    ページ本文から
      kind: "time" or "all"
      date_obj: datetime.date
      hhmm: "HH:MM" or None
      title: テキスト
      block_title: セクション見出し（《…》）
    のタプルを列挙
    """
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text("\n")
    lines = [l.rstrip() for l in text.splitlines() if l.strip()]

    # 例: 「2025年08月」
    month_pat = re.compile(r"(\d{4})年(\d{2})月")
    year, month = None, None
    for i, line in enumerate(lines):
        m = month_pat.search(line)
        if m:
            year, month = int(m.group(1)), int(m.group(2))
            break
    if not year:
        raise RuntimeError("月が見つかりませんでした")

    # 例: 「1（木）」のような行
    day_pat  = re.compile(r"^(\d{1,2})[（(].+[)）]")
    # 全角括弧に入った時刻（例: （21:30））
    time_pat = re.compile(r"[（(](\d{1,2}:\d{2})[)）]")

    events = []
    i = 0
    while i < len(lines):
        line = lines[i]
        md = day_pat.match(line)
        if md:
            day = int(md.group(1))
            date_obj = datetime(year, month, day).date()

            j = i + 1
            daily_blocks = []
            while j < len(lines) and not day_pat.match(lines[j]):
                daily_blocks.append(lines[j])
                j += 1

            block_title = None
            for blk in daily_blocks:
                s = normalize_text(blk)
                if not s:
                    continue
                # 見出し 《…》
                if s.startswith("《") and s.endswith("》"):
                    block_title = s.strip("《》")
                    continue

                # 時刻付き
                tm = time_pat.search(s)
                if tm:
                    hhmm = tm.group(1)
                    title = time_pat.sub("", s).strip()
                    events.append(("time", date_obj, hhmm, title, block_title or ""))
                else:
                    # 決算ブロックは銘柄行を分割
                    if block_title and "決算" in block_title:
                        for name in re.split(r"[、,]", s):
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
    out = [ics_header(f"Traders US (JST) {y}-{m:02d}")]

    for kind, date_obj, hhmm, title, desc in events:
        # 時刻が明記されている行は JST の時刻付きイベントで出力
        if kind == "time" and hhmm:
            try:
                hh, mm = map(int, hhmm.split(":"))
                start = datetime(date_obj.year, date_obj.month, date_obj.day, hh, mm, tzinfo=JST)
                end   = start + timedelta(minutes=60)  # 必要なら30分に変更可
                out.append(vevent_with_time_tz("Asia/Tokyo", start, end, title, desc or "source: Traders (JST)"))
            except Exception:
                # パース失敗時のフォールバック：終日
                out.append(vevent_all_day(date_obj, title, desc or "source: Traders"))
        else:
            # 時刻が無い/未定の行は終日
            out.append(vevent_all_day(date_obj, title, desc or "source: Traders"))

    out.append(ics_footer())
    return "".join(out)

def main():
    html = fetch_html()
    ics = build_ics(html)
    save_ics("docs/traders_us.ics", ics)

if __name__ == "__main__":
    main()
