# scripts/ics_common.py

import hashlib
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo  # tzdata は requirements.txt に追加済み前提

ET = ZoneInfo("America/New_York")
JST = ZoneInfo("Asia/Tokyo")

def now_jst():
    return datetime.now(JST)

def dtstamp():
    return now_jst().strftime("%Y%m%dT%H%M%S")

def uid(*parts):
    key = "|".join(parts).encode("utf-8")
    return hashlib.md5(key).hexdigest() + "@custom-ics"

def escape_text(s: str) -> str:
    return (s or "").replace("\\", "\\\\").replace(",", "\\,").replace(";", "\\;").replace("\n", "\\n")

def ics_header(name="Calendar"):
    return (
        "BEGIN:VCALENDAR\r\n"
        "VERSION:2.0\r\n"
        "PRODID:-//custom//calendar//EN\r\n"
        "CALSCALE:GREGORIAN\r\n"
        f"X-WR-CALNAME:{name}\r\n"
        "METHOD:PUBLISH\r\n"
    )

def ics_footer():
    return "END:VCALENDAR\r\n"

def vevent_all_day(date_obj, summary, description=""):
    u = uid(date_obj.strftime("%Y-%m-%d"), summary)
    return (
        "BEGIN:VEVENT\r\n"
        f"UID:{u}\r\n"
        f"DTSTAMP:{dtstamp()}\r\n"
        f"SUMMARY:{escape_text(summary)}\r\n"
        f"DESCRIPTION:{escape_text(description)}\r\n"
        f"DTSTART;VALUE=DATE:{date_obj.strftime('%Y%m%d')}\r\n"
        f"DTEND;VALUE=DATE:{(date_obj + timedelta(days=1)).strftime('%Y%m%d')}\r\n"
        "TRANSP:TRANSPARENT\r\n"
        "END:VEVENT\r\n"
    )

def vevent_with_time(start_dt, end_dt, summary, description=""):
    u = uid(start_dt.isoformat(), summary)
    return (
        "BEGIN:VEVENT\r\n"
        f"UID:{u}\r\n"
        f"DTSTAMP:{dtstamp()}\r\n"
        f"SUMMARY:{escape_text(summary)}\r\n"
        f"DESCRIPTION:{escape_text(description)}\r\n"
        f"DTSTART;TZID=America/New_York:{start_dt.strftime('%Y%m%dT%H%M%S')}\r\n"
        f"DTEND;TZID=America/New_York:{end_dt.strftime('%Y%m%dT%H%M%S')}\r\n"
        "END:VEVENT\r\n"
    )

import os
def save_ics(path, content):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    if not content.endswith("\r\n"):
        content += "\r\n"
    with open(path, "w", encoding="utf-8", newline="\r\n") as f:
        f.write(content)

def vevent_with_time_tz(tzid, start_dt, end_dt, summary, description=""):
    # start_dt / end_dt は tzinfo 付き（start_dt.tzinfo の名前は tzid と一致させる）
    u = uid(start_dt.isoformat(), summary)
    return (
        "BEGIN:VEVENT\r\n"
        f"UID:{u}\r\n"
        f"DTSTAMP:{dtstamp()}\r\n"
        f"SUMMARY:{escape_text(summary)}\r\n"
        f"DESCRIPTION:{escape_text(description)}\r\n"
        f"DTSTART;TZID={tzid}:{start_dt.strftime('%Y%m%dT%H%M%S')}\r\n"
        f"DTEND;TZID={tzid}:{end_dt.strftime('%Y%m%dT%H%M%S')}\r\n"
        "END:VEVENT\r\n"
    )
