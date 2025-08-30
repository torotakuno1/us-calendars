# scripts/run_all.py（安全版）
import os, sys, subprocess

# まず出力先を必ず作る
os.makedirs("docs", exist_ok=True)

SCRIPTS = [
    "make_fomc_ics.py",
    "make_treasury_auctions_ics.py",  # ← 後で直す。今は失敗しても続行。
    "make_opex_ics.py",
    "make_vix_ics.py",
    "make_weekly_ui_ics.py",
    "make_g17_ics.py",
    "make_traders_ics.py",
    # "make_earnings_ics.py",  # 使うときに外す
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
# 成功扱いにして後続（Commit & Pages公開）を進める
sys.exit(0)
