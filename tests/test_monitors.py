import csv
import datetime as dt

import duckdb

from heally import monitors, sync
from tests.conftest import HRRP


def results(db, **kw):
    return {(r["monitor"], r["source"]): r for r in monitors.run(db, **kw)}


def test_healthy_load_passes_every_monitor(db):
    sync.sync(db, "hrrp", HRRP)
    out = results(db, as_of=dt.datetime.now(dt.timezone.utc))
    assert all(r["status"] == "pass" for r in out.values()), out


def test_volume_drop_against_previous_load_fails(db, tmp_path):
    sync.sync(db, "hrrp", HRRP)
    rows = list(csv.reader(open(HRRP)))
    short = tmp_path / "FY_2026_Hospital_Readmissions_Reduction_Program_Hospital.csv"
    with open(short, "w", newline="") as g:
        csv.writer(g).writerows(rows[: len(rows) // 2])
    sync.sync(db, "hrrp", str(short))
    assert results(db)[("volume", "hrrp")]["status"] == "fail"


def test_stale_sync_fails_freshness(db):
    sync.sync(db, "hrrp", HRRP)
    late = dt.datetime.now(dt.timezone.utc) + dt.timedelta(days=10)
    assert results(db, as_of=late)[("freshness", "hrrp")]["status"] == "fail"


def test_null_key_fails_the_null_rate_monitor(db, small_hrrp, tmp_path):
    rows = list(csv.reader(open(small_hrrp)))
    rows[2][rows[0].index("Facility ID")] = ""
    bad = tmp_path / "FY_2026_Hospital_Readmissions_Reduction_Program_Hospital.csv"
    with open(bad, "w", newline="") as g:
        csv.writer(g).writerows(rows)
    sync.sync(db, "hrrp", str(bad))
    assert results(db)[("null_rate", "hrrp")]["status"] == "fail"


def test_results_are_persisted_for_trend_review(db):
    sync.sync(db, "hrrp", HRRP)
    monitors.run(db)
    con = duckdb.connect(db, read_only=True)
    assert con.execute("select count(*) from ops.monitor_results").fetchone()[0] >= 4
