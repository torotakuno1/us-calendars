# scripts/run_all.py
import subprocess, sys

SCRIPTS = [
    "make_fomc_ics.py",
    "make_treasury_auctions_ics.py",
    "make_opex_ics.py",
    "make_vix_ics.py",
    "make_weekly_ui_ics.py",
    "make_g17_ics.py",
    "make_traders_ics.py",
    # "make_earnings_ics.py",  # optional: uncomment if using Finnhub
]

def main():
    ok = True
    for s in SCRIPTS:
        print("==>", s)
        r = subprocess.run([sys.executable, f"scripts/{s}"])
        ok = ok and (r.returncode == 0)
    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()
