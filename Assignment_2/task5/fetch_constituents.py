import time
from io import StringIO
from pathlib import Path

import pandas as pd
import requests

DATA = Path(__file__).parent / "data"  # guard write-at-root
API = "https://en.wikipedia.org/w/api.php"
INDEX = "https://en.wikipedia.org/w/index.php"
HEADERS = {"User-Agent": "WikiRevisionResearch/1.0 (e.kiymac@student.uw.edu.pl)"}

SNAPSHOT_START, SNAPSHOT_END = "2022-09-01", "2026-10-01"
COL_MAP = {
    "Symbol": "ticker",
    "Security": "name",
    "GICS Sector": "sector",
    "GICS Sub-Industry": "sub_industry",
    "CIK": "cik",
}


def revid_as_of(session: requests.Session, timestamp: str) -> int:
    r = session.get(
        API,
        params={
            "action": "query",
            "prop": "revisions",
            "titles": "List of S&P 500 companies",
            "rvstart": timestamp,
            "rvdir": "older",
            "rvlimit": 1,
            "rvprop": "ids|timestamp",
            "format": "json",
        },
    ).json()
    page = next(iter(r["query"]["pages"].values()))
    return page["revisions"][0]["revid"]


def constituents_at(session: requests.Session, revid: int) -> pd.DataFrame:
    html = session.get(INDEX, params={"oldid": revid}).text
    tbl = pd.read_html(StringIO(html), header=0, attrs={"id": "constituents"})[0]
    assert (
        480 <= len(tbl) <= 520
    ), f"rev {revid}: {len(tbl)} rows"  # guard malformed table fetches
    assert set(COL_MAP) <= set(tbl.columns), f"rev {revid}: columns {list(tbl.columns)}"

    tbl = tbl[list(COL_MAP)].rename(columns=COL_MAP)
    tbl["ticker"] = tbl["ticker"].str.replace(".", "-", regex=False)
    # There are 'TBD'-s in the column, script crashes without coercion.
    tbl["cik"] = pd.to_numeric(tbl["cik"], errors="coerce").astype("Int64")
    return tbl


def fetch_snapshots(session: requests.Session) -> pd.DataFrame:
    frames = []
    for date in pd.date_range(SNAPSHOT_START, SNAPSHOT_END, freq="MS"):
        revid = revid_as_of(session, date.strftime("%Y-%m-%dT00:00:00Z"))
        tbl = constituents_at(session, revid)
        tbl.insert(0, "snapshot", date)
        tbl.insert(1, "revid", revid)
        frames.append(tbl)
        print(f"{date:%Y-%m}  rev {revid}  {len(tbl)} names")
        time.sleep(0.2)
    return pd.concat(frames, ignore_index=True)


def main() -> None:
    DATA.mkdir(exist_ok=True)
    with requests.Session() as session:
        session.headers.update(HEADERS)
        fetch_snapshots(session).to_csv(DATA / "constituents_pit.csv", index=False)


if __name__ == "__main__":
    main()
