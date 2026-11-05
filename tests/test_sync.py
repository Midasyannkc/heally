import csv
import json

import duckdb
import pytest

from heally import sync
from tests.conftest import HRRP, HOSP


def q(db, sql):
    con = duckdb.connect(db, read_only=True)
    try:
        return con.execute(sql).fetchall()
    finally:
        con.close()


def test_real_files_load_every_row_as_text_with_lineage(db):
    a = sync.sync(db, "hrrp", HRRP)
    b = sync.sync(db, "hospital_info", HOSP)
    assert (a["status"], a["rows"]) == ("loaded", 18330)
    assert (b["status"], b["rows"]) == ("loaded", 5419)
    cols = {r[0]: r[1] for r in q(db, "select column_name, data_type from information_schema.columns where table_schema='raw' and table_name='hrrp'")}
    assert cols["facility_id"] == "VARCHAR" and cols["number_of_discharges"] == "VARCHAR"
    assert {"_source_file", "_file_sha256", "_row_hash", "_synced_at"} <= set(cols)


def test_leading_zeros_in_facility_id_survive(db):
    sync.sync(db, "hospital_info", HOSP)
    assert q(db, "select count(*) from raw.hospital_info where facility_id = '010001'")[0][0] == 1


def test_resync_of_an_unchanged_file_is_a_noop(db, small_hrrp):
    sync.sync(db, "hrrp", small_hrrp)
    again = sync.sync(db, "hrrp", small_hrrp)
    assert again["status"] == "skipped_unchanged"
    assert q(db, "select count(*) from raw.hrrp")[0][0] == 5
    assert q(db, "select count(*) from raw._sync_log where status='loaded'")[0][0] == 1


def test_a_changed_file_replaces_the_previous_snapshot(db, small_hrrp, tmp_path):
    sync.sync(db, "hrrp", small_hrrp)
    rows = list(csv.reader(open(small_hrrp)))
    changed = tmp_path / "FY_2026_Hospital_Readmissions_Reduction_Program_Hospital.csv"
    with open(changed, "w", newline="") as g:
        csv.writer(g).writerows(rows[:4])
    res = sync.sync(db, "hrrp", str(changed))
    assert res["status"] == "loaded" and res["rows"] == 3
    assert q(db, "select count(*) from raw.hrrp")[0][0] == 3


def test_renamed_source_column_blocks_the_load_and_is_logged(db, small_hrrp, tmp_path):
    sync.sync(db, "hrrp", small_hrrp)
    rows = list(csv.reader(open(small_hrrp)))
    rows[0][rows[0].index("Facility ID")] = "Provider ID"
    bad = tmp_path / "FY_2026_Hospital_Readmissions_Reduction_Program_Hospital.csv"
    with open(bad, "w", newline="") as g:
        csv.writer(g).writerows(rows)
    with pytest.raises(sync.SchemaDrift) as e:
        sync.sync(db, "hrrp", str(bad))
    assert "Facility ID" in str(e.value) and "Provider ID" in str(e.value)
    assert q(db, "select count(*) from raw.hrrp")[0][0] == 5
    status, details = q(db, "select status, details from raw._sync_log order by sync_id desc limit 1")[0]
    assert status == "blocked_schema_drift" and "Provider ID" in details


def test_an_added_source_column_is_loaded_and_logged(db, small_hrrp, tmp_path):
    rows = list(csv.reader(open(small_hrrp)))
    rows[0].append("New Metric")
    for r in rows[1:]:
        r.append("1")
    wide = tmp_path / "FY_2026_Hospital_Readmissions_Reduction_Program_Hospital.csv"
    with open(wide, "w", newline="") as g:
        csv.writer(g).writerows(rows)
    res = sync.sync(db, "hrrp", str(wide))
    assert res["status"] == "loaded" and res["added_columns"] == ["New Metric"]
    assert q(db, "select count(*) from information_schema.columns where table_name='hrrp' and column_name='new_metric'")[0][0] == 1


def test_row_hash_is_stable_across_loads(db, small_hrrp, tmp_path):
    sync.sync(db, "hrrp", small_hrrp)
    first = q(db, "select _row_hash from raw.hrrp order by 1")
    other = str(tmp_path / "again.duckdb")
    sync.sync(other, "hrrp", small_hrrp)
    assert q(other, "select _row_hash from raw.hrrp order by 1") == first
