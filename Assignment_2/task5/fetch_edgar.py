import time
from pathlib import Path

import pandas as pd
import requests

DATA = Path(__file__).parent.parent / "data" / "task5"

# edgar looks for a name + email in the header.
HEADERS = {"User-Agent": "Ege Guney Kiymac e.kiymac@student.uw.edu.pl"}
SECTOR = "Information Technology"

TAGS = {
    "us-gaap": [
        "NetIncomeLoss",
        "ProfitLoss",
        "OperatingIncomeLoss",
        "StockholdersEquity",
        "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest",
        "CashAndCashEquivalentsAtCarryingValue",
        "ShortTermInvestments",
        "MarketableSecurities",
        "MarketableSecuritiesCurrent",
        "AvailableForSaleSecuritiesCurrent",
        "AvailableForSaleSecuritiesDebtSecuritiesCurrent",
        "DebtSecuritiesAvailableForSaleExcludingAccruedInterestCurrent",
        "OtherShortTermInvestments",
        "HeldToMaturitySecuritiesCurrent",
        "LongTermDebt",
        "LongTermDebtNoncurrent",
        "LongTermDebtCurrent",
        "DebtCurrent",
        "CommonStockSharesOutstanding",
        "WeightedAverageNumberOfDilutedSharesOutstanding",
    ],
    "dei": ["EntityCommonStockSharesOutstanding"],
}
END_MIN, FILED_MAX = "2021-07-01", "2026-10-01"
KEEP = ("start", "end", "val", "filed", "form", "fy", "fp", "accn")


def universe_ciks() -> dict[str, str]:
    if not (DATA / "constituents_pit.csv").exists():
        raise FileNotFoundError(
            f"Run fetch_constituents.py first to get {DATA / 'constituents_pit.csv'}"
        )
    members = pd.read_csv(DATA / "constituents_pit.csv")
    it = members.loc[members["sector"] == SECTOR]
    latest = it.sort_values("snapshot").groupby("ticker")["cik"].last()
    return {str(ticker): f"{int(cik):010d}" for ticker, cik in latest.items()}


def fetch_facts(session: requests.Session, cik: str) -> dict:
    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
    r = session.get(url)
    r.raise_for_status()
    return r.json()


def flatten(ticker: str, facts: dict) -> list[dict]:
    rows = []
    for ns, tags in TAGS.items():
        block = facts.get("facts", {}).get(ns, {})
        for tag in tags:
            for unit, recs in block.get(tag, {}).get("units", {}).items():
                for r in recs:
                    if r["end"] >= END_MIN and r["filed"] <= FILED_MAX:
                        rows.append(
                            {
                                "ticker": ticker,
                                "ns": ns,
                                "tag": tag,
                                "unit": unit,
                                **{k: r.get(k) for k in KEEP},
                            }
                        )
    return rows


def main() -> None:
    DATA.mkdir(exist_ok=True)
    ciks = universe_ciks()
    rows, failed = [], []

    with requests.Session() as session:
        session.headers.update(HEADERS)
        for i, (ticker, cik) in enumerate(ciks.items(), start=1):
            try:
                facts = fetch_facts(session, cik)
            except Exception as e:
                failed.append((ticker, cik, str(e)))
                print(f"[{i}/{len(ciks)}] {ticker} CIK{cik} FAILED: {e}")
            else:
                rows += flatten(ticker, facts)
                print(f"[{i}/{len(ciks)}] {ticker} CIK{cik}")
            time.sleep(0.2)  # 10 req/s limit, plus margin

    out = DATA / "edgar_facts_trimmed.csv"
    pd.DataFrame(rows).to_csv(out, index=False)

    print(f"\n{len(ciks) - len(failed)} filers, {len(rows)} fact rows -> {out.name}")
    if failed:
        print(f"{len(failed)} failed: {[t for t, _, _ in failed]}")


if __name__ == "__main__":
    main()
