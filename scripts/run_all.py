import os, sys, subprocess
os.makedirs("docs", exist_ok=True)

SCRIPTS = [
    "make_fomc_ics.py",
    # "make_treasury_auctions_ics.py",  # ← 入札は後で直すまで停止
    # "make_opex_ics.py",               # ←OPEXは一旦停止
    "make_vix_ics.py",
    "make_weekly_ui_ics.py",
    "make_g17_ics.py",
    "make_traders_ics.py",
]

failures = []
for s in SCRIPTS:
    print("==>", s, flush=True)
    r = subprocess.run([sys.executable, f"scripts/{s}"])
    if r.returncode != 0:
        failures.append(s)
        print(f"WARN: {s} failed (code {r.returncode}) — continuing", flush=True)

if failures:
    print("Completed with warnings. Failed:", ", ".join(failures), flush=True)
sys.exit(0)   # 失敗があっても他の.icsは出す
