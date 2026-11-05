"""Run the real dbt project against a tiny warehouse built from fixture CSVs that use the real CMS headers."""
import csv
import os
import subprocess
import sys

import duckdb

from heally import sync
from tests.conftest import HRRP, HOSP, ROOT

PROJECT = os.path.join(ROOT, "dbt_heally")


def write_csv(real_path, out_path, rows):
    header = next(csv.reader(open(real_path, newline="")))
    with open(out_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        for r in rows:
            w.writerow([r.get(h, "") for h in header])
    return str(out_path)


def hrrp_row(**kw):
    base = {"Facility Name": "TEST HOSPITAL", "Facility ID": "010001", "State": "AL", "Measure Name": "READM-30-HF-HRRP",
            "Number of Discharges": "100", "Footnote": "", "Excess Readmission Ratio": "1.1000", "Predicted Readmission Rate": "22.0000",
            "Expected Readmission Rate": "20.0000", "Number of Readmissions": "22", "Start Date": "07/01/2021", "End Date": "06/30/2024"}
    base.update(kw)
    return base


def hosp_row(**kw):
    base = {"Facility ID": "010001", "Facility Name": "TEST HOSPITAL", "Address": "1 MAIN ST", "City/Town": "DOTHAN", "State": "AL", "ZIP Code": "36301",
            "County/Parish": "HOUSTON", "Telephone Number": "(334) 000-0000", "Hospital Type": "Acute Care Hospitals",
            "Hospital Ownership": "Proprietary", "Emergency Services": "Yes", "Meets criteria for birthing friendly designation": "Y",
            "Hospital overall rating": "4", "Count of READM Measures Worse": "0"}
    base.update(kw)
    return base


def warehouse(tmp_path, hrrp_rows, hosp_rows):
    db = str(tmp_path / "w.duckdb")
    sync.sync(db, "hrrp", write_csv(HRRP, tmp_path / "FY_2026_Hospital_Readmissions_Reduction_Program_Hospital.csv", hrrp_rows))
    sync.sync(db, "hospital_info", write_csv(HOSP, tmp_path / "Hospital_General_Information.csv", hosp_rows))
    return db


def dbt(db, *args):
    env = {**os.environ, "HEALLY_DB": db, "DBT_SEND_ANONYMOUS_USAGE_STATS": "False"}
    return subprocess.run([sys.executable, "-m", "dbt.cli.main", *args, "--project-dir", PROJECT, "--profiles-dir", PROJECT],
                          cwd=ROOT, env=env, capture_output=True, text=True)


def query(db, sql):
    con = duckdb.connect(db, read_only=True)
    try:
        return con.execute(sql).fetchall()
    finally:
        con.close()
