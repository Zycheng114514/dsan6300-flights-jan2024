"""Run every problem in the HW4 SQL file, save one CSV per problem, and fill in row counts.

Usage (local test server):
    python scripts/run_queries.py --host 127.0.0.1 --port 3399 --user root

Usage (your AWS RDS database; the password is read from the MYSQL_PWD environment variable):
    export MYSQL_PWD='...'
    python scripts/run_queries.py --host <your-db>.rds.amazonaws.com --user admin

The SQL file keeps "# rows returned: __Q1__" style placeholders in sql/hw4_..._template.sql;
the filled-in copy is written to sql/hw4_cheng_zhiyang_zc385.sql.
"""
import argparse
import csv
import os
import re
from pathlib import Path

import pymysql

ROOT = Path(__file__).resolve().parent.parent
SQL_TEMPLATE = ROOT / "sql" / "hw4_cheng_zhiyang_zc385_template.sql"
SQL_OUT = ROOT / "sql" / "hw4_cheng_zhiyang_zc385.sql"
RESULTS = ROOT / "results"
PREFIX = "hw4_cheng_zhiyang_zc385"


def split_problems(text):
    """Return [(label, query)] for each '# Problem X' block."""
    blocks = re.split(r"^# Problem (\S+)\s*$", text, flags=re.M)
    out = []
    for label, body in zip(blocks[1::2], blocks[2::2]):
        code = "\n".join(l for l in body.splitlines() if not l.lstrip().startswith("#"))
        query = code.split(";")[0].strip()
        out.append((label, query))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=3306)
    ap.add_argument("--user", default="admin")
    ap.add_argument("--db", default="FAA")
    args = ap.parse_args()

    conn = pymysql.connect(host=args.host, port=args.port, user=args.user,
                           password=os.environ.get("MYSQL_PWD", ""), database=args.db)
    template = SQL_TEMPLATE.read_text()
    filled = template
    RESULTS.mkdir(exist_ok=True)
    with conn.cursor() as cur:
        for label, query in split_problems(template):
            cur.execute(query)
            rows = cur.fetchall()
            cols = [d[0] for d in cur.description]
            name = f"{PREFIX}_problem{label.lower()}.csv"
            with open(RESULTS / name, "w", newline="") as f:
                w = csv.writer(f)
                w.writerow(cols)
                w.writerows(rows)
            filled = filled.replace(f"__Q{label.upper()}__", str(len(rows)))
            print(f"Problem {label}: {len(rows)} rows -> results/{name}")
    SQL_OUT.write_text(filled)
    print(f"Wrote {SQL_OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
