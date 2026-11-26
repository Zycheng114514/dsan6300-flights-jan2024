# Runs the extra queries for the website charts and saves them in website/data/.
# Also copies the 8 result CSVs there so the website can show them.
# Usage: python scripts/make_chart_data.py <rds-endpoint>
import shutil
import sys
from getpass import getpass
from pathlib import Path

import pandas as pd
import pymysql

QUERIES = {
    # cancellations per day by reason (A = carrier, B = weather, C = National Air System)
    "daily": """
        SELECT FlightDate AS flight_date,
               SUM(CancellationCode = 'A') AS carrier,
               SUM(CancellationCode = 'B') AS weather,
               SUM(CancellationCode = 'C') AS nas
        FROM al_perf
        WHERE Cancelled = 1
        GROUP BY FlightDate
        ORDER BY FlightDate""",
    # cancellation rate and average delay per airline (delay: early = 0, departed flights only)
    "airlines": """
        SELECT p.Reporting_Airline AS code,
               a.Name AS airline_name,
               COUNT(*) AS flights,
               SUM(p.Cancelled = 1) AS cancelled,
               ROUND(100 * AVG(p.Cancelled = 1), 2) AS pct_cancelled,
               ROUND(AVG(CASE WHEN p.DepTime <> '' THEN GREATEST(p.DepDelay, 0) END), 2) AS avg_delay
        FROM al_perf p
        JOIN L_AIRLINE_ID a ON a.ID = p.DOT_ID_Reporting_Airline
        GROUP BY p.Reporting_Airline, a.Name
        ORDER BY flights DESC""",
    # share of flights that left 15+ minutes late, by scheduled departure hour
    "time_of_day": """
        SELECT DepTimeBlk AS time_block,
               COUNT(*) AS flights,
               ROUND(100 * AVG(DepDel15), 2) AS pct_late
        FROM al_perf
        WHERE DepTime <> ''
        GROUP BY DepTimeBlk
        ORDER BY DepTimeBlk""",
}

root = Path(__file__).resolve().parent.parent
out = root / "website" / "data"
conn = pymysql.connect(host=sys.argv[1], user="admin", password=getpass("RDS password: "),
                       database="FAA")

for name, sql in QUERIES.items():
    with conn.cursor() as cur:
        cur.execute(sql)
        df = pd.DataFrame(cur.fetchall(), columns=[c[0] for c in cur.description])
    df.to_csv(out / f"{name}.csv", index=False)
    print(name, len(df), "rows")

for f in (root / "results").glob("*.csv"):
    shutil.copy(f, out / f.name)
