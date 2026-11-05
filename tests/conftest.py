import csv
import os
import pytest

ROOT = os.path.dirname(os.path.dirname(__file__))
RAW = os.path.join(ROOT, "data", "raw")
HRRP = os.path.join(RAW, "FY_2026_Hospital_Readmissions_Reduction_Program_Hospital.csv")
HOSP = os.path.join(RAW, "Hospital_General_Information.csv")


@pytest.fixture
def db(tmp_path):
    return str(tmp_path / "heally.duckdb")


@pytest.fixture
def small_hrrp(tmp_path):
    """A 5 row slice of the real HRRP file with the real header, for fast tests."""
    out = tmp_path / "FY_2026_Hospital_Readmissions_Reduction_Program_Hospital.csv"
    with open(HRRP, newline="") as f, open(out, "w", newline="") as g:
        r = csv.reader(f)
        w = csv.writer(g, quoting=csv.QUOTE_MINIMAL)
        for i, row in enumerate(r):
            w.writerow(row)
            if i == 5:
                break
    return str(out)
