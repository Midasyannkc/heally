import sqlite3

import duckdb
import pytest

from heally import reverse_etl


def make_mart(path, rows):
    con = duckdb.connect(path)
    con.execute("create schema if not exists marts")
    con.execute("create or replace table marts.mart_navigator_worklist (facility_id varchar, measure_code varchar, priority_tier varchar, excess_readmissions double)")
    for r in rows:
        con.execute("insert into marts.mart_navigator_worklist values (?,?,?,?)", r)
    con.close()


def dest_rows(dest):
    c = sqlite3.connect(dest)
    try:
        return c.execute("select facility_id, measure_code, priority_tier, status from navigator_worklist order by 1,2").fetchall()
    finally:
        c.close()


ROWS = [("010001", "HF", "A", 12.5), ("010001", "AMI", "B", 3.0), ("020001", "PN", "A", 9.1)]


def test_first_sync_inserts_every_row(tmp_path):
    db, dest = str(tmp_path / "w.duckdb"), str(tmp_path / "crm.sqlite")
    make_mart(db, ROWS)
    r = reverse_etl.sync(db, dest)
    assert (r["inserted"], r["updated"], r["retired"]) == (3, 0, 0)
    assert len(dest_rows(dest)) == 3


def test_second_identical_sync_writes_nothing(tmp_path):
    db, dest = str(tmp_path / "w.duckdb"), str(tmp_path / "crm.sqlite")
    make_mart(db, ROWS)
    reverse_etl.sync(db, dest)
    r = reverse_etl.sync(db, dest)
    assert (r["inserted"], r["updated"], r["retired"], r["unchanged"]) == (0, 0, 0, 3)


def test_only_changed_rows_are_updated_and_dropped_rows_are_retired(tmp_path):
    db, dest = str(tmp_path / "w.duckdb"), str(tmp_path / "crm.sqlite")
    make_mart(db, ROWS)
    reverse_etl.sync(db, dest)
    make_mart(db, [("010001", "HF", "B", 12.5), ("010001", "AMI", "B", 3.0), ("030001", "COPD", "A", 7.0)])
    r = reverse_etl.sync(db, dest)
    assert (r["inserted"], r["updated"], r["retired"], r["unchanged"]) == (1, 1, 1, 1)
    status = {(a, b): s for a, b, _, s in dest_rows(dest)}
    assert status[("020001", "PN")] == "retired" and status[("010001", "HF")] == "active"


def test_an_empty_source_never_wipes_the_destination(tmp_path):
    db, dest = str(tmp_path / "w.duckdb"), str(tmp_path / "crm.sqlite")
    make_mart(db, ROWS)
    reverse_etl.sync(db, dest)
    make_mart(db, [])
    with pytest.raises(reverse_etl.UnsafeSync):
        reverse_etl.sync(db, dest)
    assert all(s == "active" for *_, s in dest_rows(dest))


def test_a_large_drop_is_refused_unless_forced(tmp_path):
    db, dest = str(tmp_path / "w.duckdb"), str(tmp_path / "crm.sqlite")
    make_mart(db, ROWS)
    reverse_etl.sync(db, dest)
    make_mart(db, ROWS[:1])
    with pytest.raises(reverse_etl.UnsafeSync):
        reverse_etl.sync(db, dest)
    assert reverse_etl.sync(db, dest, force=True)["retired"] == 2
