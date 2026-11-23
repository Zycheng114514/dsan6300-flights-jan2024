# One Month, Two Shocks: US flights in January 2024

DSAN 6300 (Database Systems) mini-project. 547,271 domestic flights from the Bureau of
Transportation Statistics *Reporting Carrier On-Time Performance* table, loaded into MySQL on
AWS RDS and analyzed with SQL. The findings are written up as a Quarto website.

**Website:** https://zycheng114514.github.io/dsan6300-flights-jan2024/

## Repository layout

| Path | What it is |
|---|---|
| `sql/00_CreateFactTable.sql` | DDL for the fact table `al_perf` (provided by the course) |
| `sql/01_create_dimension_tables.sql` | DDL for the 6 lookup tables |
| `sql/hw4_cheng_zhiyang_zc385.sql` | The 7 graded queries with row counts |
| `sql/site_queries.sql` | Extra queries behind the website's charts |
| `results/` | One CSV per graded question |
| `data/dimension/` | The 6 dimension CSVs |
| `scripts/run_queries.py` | Runs the graded queries, writes `results/` and fills in row counts |
| `scripts/build_site_data.py` | Exports chart data to `website/data/` |
| `website/` | Quarto site source (`index.qmd`, `questions.qmd`, `methods.qmd`, `viz.py`) |

## Reproduce

1. Download January 2024 from [TranStats](https://www.transtats.bts.gov/) (Prezipped file) and save it
   as `data/raw/al_perf.csv`.
2. Create schema `FAA`, run the two DDL files, and load the data:
   ```bash
   mysqlimport --local --compress --user=admin -p --host=<rds-endpoint> \
     --fields-terminated-by=',' --fields-optionally-enclosed-by='"' --ignore-lines=1 FAA al_perf.csv
   ```
3. `python scripts/run_queries.py --host <rds-endpoint> --user admin` (password from `MYSQL_PWD`)
4. `python scripts/build_site_data.py --host <rds-endpoint> --user admin`
5. `cd website && quarto render`

Requires Python 3 with `pymysql`, `pandas`, `plotly`, `tabulate`, and Quarto.
