# DSAN 6300 Mini-Project: US flights in January 2024

547,271 domestic flights from the Bureau of Transportation Statistics, loaded into MySQL on AWS
RDS and analyzed with SQL.

Website: https://zycheng114514.github.io/dsan6300-flights-jan2024/

- `sql/00_CreateFactTable.sql`: creates the fact table al_perf (from the course)
- `sql/hw4_cheng_zhiyang_zc385.sql`: the 7 questions with row counts
- `results/`: one CSV per question
- `data/dimension/`: the 6 lookup table CSVs
- `scripts/make_chart_data.py`: runs the extra queries for the charts
- `website/`: Quarto site (`index.qmd`, `questions.qmd`, `viz.py`)

To rebuild the site: `MYSQL_PWD=<password> python scripts/make_chart_data.py <rds-endpoint>`,
then `cd website && quarto render`.
