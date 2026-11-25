# Copied from Assignment 2, Task 5 and edited to fetch 8-K earning release filings
import re
import time
from io import StringIO
from pathlib import Path

import lxml.html
import pandas as pd
import requests

DATA = Path(__file__).parent / "data"

# edgar looks for a name + email in the header.
HEADERS = {"User-Agent": "Ege Guney Kiymac e.kiymac@student.uw.edu.pl"}
START = "2020-01-01"
SUBMISSIONS = "https://data.sec.gov/submissions"

def get(session: requests.Session, url: str) -> requests.Response:
    for _ in range(4):
        time.sleep(0.11)  # 10 req/s limit, plus margin
        r = session.get(url)
        if r.status_code < 500 and r.status_code != 429:
            break
    r.raise_for_status()
    return r


def ticker_ciks(session: requests.Session, tickers: list[str]) -> dict[str, int]:
    table = get(session, "https://www.sec.gov/files/company_tickers.json").json()
    lookup = {row["ticker"]: row["cik_str"] for row in table.values()}
    lookup["ROKU"] = 1428439  # Delisted in 2026-11, CIK manually added
    missing = set(tickers) - lookup.keys()
    if missing:
        raise KeyError(f"No CIK for {sorted(missing)}")
    return {t: lookup[t] for t in tickers}


def filings(session: requests.Session, cik: int) -> pd.DataFrame:
    sub = get(session, f"{SUBMISSIONS}/CIK{cik:010d}.json").json()["filings"]
    # "recent" holds the last ~1000 filings; Form 4s eat into that fast for large caps.
    pages = [sub["recent"]] + [
        get(session, f"{SUBMISSIONS}/{f['name']}").json()
        for f in sub["files"]
        if f["filingTo"] >= START
    ]
    fields = ["accessionNumber", "filingDate", "acceptanceDateTime", "form", "items"]
    return pd.concat([pd.DataFrame({k: p[k] for k in fields}) for p in pages])


def earnings_8ks(df: pd.DataFrame) -> pd.DataFrame:
    item_202 = df["items"].str.contains(r"(?:^|,)2\.02(?:,|$)")
    keep = (df["form"] == "8-K") & item_202 & (df["filingDate"] >= START)
    return df[keep].sort_values("filingDate").reset_index(drop=True)


def exhibit_url(session: requests.Session, cik: int, accession: str) -> str | None:
    folder = f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession.replace('-', '')}"
    html = get(session, f"{folder}/{accession}-index.htm").text
    docs = pd.read_html(StringIO(html), attrs={"class": "tableFile"})[0]
    ex99 = docs[docs["Type"].astype(str).str.startswith("EX-99")]
    if ex99.empty:
        return None
    return f"{folder}/{ex99['Document'].iloc[0].split()[0]}"


def lm_words() -> dict[str, set[str]]:
    d = pd.read_csv(DATA / "lm_dict.csv", keep_default_na=False)
    # Category columns hold the year a word was added; negative years mark removals.
    return {
        "words": set(d["Word"]),
        "pos": set(d.loc[d["Positive"] > 0, "Word"]),
        "neg": set(d.loc[d["Negative"] > 0, "Word"]),
        "unc": set(d.loc[d["Uncertainty"] > 0, "Word"]),
    }


def lm_counts(html: bytes, lm: dict[str, set[str]]) -> dict[str, int]:
    doc = lxml.html.fromstring(html)
    for el in doc.xpath("//table[not(ancestor::table)] | //script | //style"):
        el.drop_tree()
    text = " ".join(doc.itertext()).upper()
    words = [w for w in re.findall(r"[A-Z]+", text) if w in lm["words"]]

    negators = {"NO", "NOT", "NONE", "NEITHER", "NEVER", "NOBODY"}
    return {
        "n_words": len(words),
        "n_pos": sum(
            w in lm["pos"] and negators.isdisjoint(words[max(i - 3, 0) : i])
            for i, w in enumerate(words)
        ),
        "n_neg": sum(w in lm["neg"] for w in words),
        "n_unc": sum(w in lm["unc"] for w in words),
    }


def fetch_releases(
    session: requests.Session, ticker: str, cik: int, lm: dict[str, set[str]]
) -> list[dict]:
    rows = []
    for f in earnings_8ks(filings(session, cik)).itertuples():
        url = exhibit_url(session, cik, f.accessionNumber)
        counts = lm_counts(get(session, url).content, lm) if url else {}
        rows.append(
            {
                "ticker": ticker,
                "cik": cik,
                "accession": f.accessionNumber,
                "filing_date": f.filingDate,
                "acceptance": f.acceptanceDateTime,
                "items": f.items,
                "exhibit_url": url,
                **counts,
            }
        )
    return rows


def main() -> None:
    tickers = [
        "NVDA", "AMD", "MU", "INTC", "MRVL",
        "CRWD", "DDOG", "OKTA", "TWLO", "DOCU", "ZM",
        "META", "NFLX", "SNAP", "PINS", "ROKU",
        "TSLA", "AMZN", "ETSY", "CVNA", "PTON",
        "MRNA", "ENPH", "PYPL", "BA",     
    ]

    lm = lm_words()
    rows, failed = [], []

    with requests.Session() as session:
        session.headers.update(HEADERS)
        ciks = ticker_ciks(session, tickers)
        for i, (ticker, cik) in enumerate(ciks.items(), start=1):
            try:
                found = fetch_releases(session, ticker, cik, lm)
            except Exception as e:
                failed.append(ticker)
                print(f"[{i}/{len(ciks)}] {ticker} CIK{cik} FAILED: {e}")
            else:
                rows += found
                print(f"[{i}/{len(ciks)}] {ticker} CIK{cik}: {len(found)} releases")

    out = DATA / "releases.csv"
    pd.DataFrame(rows).to_csv(out, index=False)

    print(f"\n{len(rows)} item 2.02 filings -> {out.name}")
    print(f"{sum(r['exhibit_url'] is None for r in rows)} without an EX-99 exhibit")
    if failed:
        print(f"{len(failed)} failed: {failed}")


if __name__ == "__main__":
    main()
