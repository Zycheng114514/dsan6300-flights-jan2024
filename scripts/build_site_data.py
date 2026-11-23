"""Export the website's chart data and copy the graded result CSVs into website/data/.

    python scripts/build_site_data.py --host 127.0.0.1 --port 3399 --user root
(password, if any, from the MYSQL_PWD environment variable)
"""
import argparse
import csv
import os
import re
import shutil
from pathlib import Path

import pymysql

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "website" / "data"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=3306)
    ap.add_argument("--user", default="admin")
    ap.add_argument("--db", default="FAA")
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)

    text = (ROOT / "sql" / "site_queries.sql").read_text()
    blocks = re.split(r"^-- @name (\S+)\s*$", text, flags=re.M)
    conn = pymysql.connect(host=args.host, port=args.port, user=args.user,
                           password=os.environ.get("MYSQL_PWD", ""), database=args.db)
    with conn.cursor() as cur:
        for name, body in zip(blocks[1::2], blocks[2::2]):
            code = "\n".join(l for l in body.splitlines() if not l.lstrip().startswith("--"))
            cur.execute(code.strip().rstrip(";"))
            rows = cur.fetchall()
            with open(OUT / f"{name}.csv", "w", newline="") as f:
                w = csv.writer(f)
                w.writerow([d[0] for d in cur.description])
                w.writerows(rows)
            print(f"{name}: {len(rows)} rows")

    for f in sorted((ROOT / "results").glob("*.csv")):
        shutil.copy(f, OUT / f.name)
    shutil.copy(ROOT / "sql" / "hw4_cheng_zhiyang_zc385.sql", OUT / "hw4_cheng_zhiyang_zc385.sql")
    print("copied graded results + SQL into website/data/")


if __name__ == "__main__":
    main()
