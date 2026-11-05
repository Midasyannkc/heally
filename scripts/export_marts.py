"""Export the marts (and the typed raw tables) to CSV and parquet so the data can be opened without DuckDB."""
import os
import sys

import duckdb

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
db = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "out", "heally.duckdb")
out = os.path.join(ROOT, "data", "marts")
os.makedirs(out, exist_ok=True)
con = duckdb.connect(db, read_only=True)
tables = [r[0] for r in con.execute("select table_name from information_schema.tables where table_schema='marts' and table_name not like 'metricflow%' order by 1").fetchall()]
for t in tables:
    n = con.execute(f"select count(*) from marts.{t}").fetchone()[0]
    con.execute(f"copy (select * from marts.{t}) to '{out}/{t}.parquet' (format parquet, compression zstd)")
    con.execute(f"copy (select * from marts.{t}) to '{out}/{t}.csv' (header, delimiter ',')")
    print(f"{t}: {n} rows")
