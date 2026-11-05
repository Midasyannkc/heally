"""End to end on the real CMS files: sync, dbt build, monitors, reverse ETL. Slow, so one shared run."""
import csv
import json
import os
import shutil
import sqlite3

import duckdb
import pytest

from heally import pipeline
from tests.conftest import HRRP, HOSP, RAW


@pytest.fixture(scope="module")
def run1(tmp_path_factory):
    d = tmp_path_factory.mktemp("e2e")
    raw = d / "raw"
    shutil.copytree(RAW, raw)
    db, crm, manifest = str(d / "h.duckdb"), str(d / "crm.sqlite"), str(d / "manifest.json")
    result = pipeline.run(db=db, raw_dir=str(raw), crm_path=crm, manifest_path=manifest)
    return dict(d=d, raw=raw, db=db, crm=crm, manifest=manifest, result=result)


def test_first_run_passes_every_gate_and_writes_a_manifest(run1):
    m = json.load(open(run1["manifest"]))
    assert m["passed"] is True
    assert [s["step"] for s in m["steps"]] == ["sync", "dbt_build", "monitors", "reverse_etl"]
    assert m["dbt"]["errors"] == 0 and m["dbt"]["passed"] >= 40
    assert m["rows"]["hrrp"] == 18330 and m["rows"]["hospital_info"] == 5419


def test_crm_destination_matches_the_worklist_mart(run1):
    wl = duckdb.connect(run1["db"], read_only=True).execute("select count(*) from marts.mart_navigator_worklist").fetchone()[0]
    c = sqlite3.connect(run1["crm"])
    assert c.execute("select count(*) from navigator_worklist where status='active'").fetchone()[0] == wl == 4316


def test_second_run_is_a_noop_for_sync_and_reverse_etl(run1):
    again = pipeline.run(db=run1["db"], raw_dir=str(run1["raw"]), crm_path=run1["crm"], manifest_path=run1["manifest"])
    assert again["steps"][0]["detail"]["hrrp"] == "skipped_unchanged"
    rev = again["steps"][3]["detail"]
    assert (rev["inserted"], rev["updated"], rev["retired"]) == (0, 0, 0) and rev["unchanged"] == 4316


def test_schema_drift_stops_the_run_before_any_downstream_step(run1, tmp_path):
    raw = tmp_path / "raw"
    shutil.copytree(RAW, raw)
    f = raw / os.path.basename(HRRP)
    rows = list(csv.reader(open(f)))
    rows[0][rows[0].index("Excess Readmission Ratio")] = "ERR"
    csv.writer(open(f, "w", newline="")).writerows(rows)
    before = sqlite3.connect(run1["crm"]).execute("select count(*) from sync_log").fetchone()[0]
    with pytest.raises(pipeline.PipelineFailed) as e:
        pipeline.run(db=str(tmp_path / "x.duckdb"), raw_dir=str(raw), crm_path=run1["crm"], manifest_path=str(tmp_path / "m.json"))
    assert "schema drift" in str(e.value).lower()
    assert sqlite3.connect(run1["crm"]).execute("select count(*) from sync_log").fetchone()[0] == before
    m = json.load(open(tmp_path / "m.json"))
    assert m["passed"] is False and m["failed_step"] == "sync"


def test_semantic_layer_parses_and_its_measures_reproduce_the_marts(run1):
    """dbt parses the semantic models into semantic_manifest.json; applying each measure's expression to the fact table must equal the mart totals."""
    from tests.dbt_helper import dbt
    assert dbt(run1["db"], "parse").returncode == 0
    from tests.conftest import ROOT
    sm = json.load(open(os.path.join(ROOT, "out", "dbt_target", "semantic_manifest.json")))
    metrics = {m["name"] for m in sm["metrics"]}
    assert {"excess_readmissions", "total_discharges", "share_pairs_above_expected", "excess_readmissions_per_1000_discharges"} <= metrics
    measures = {m["name"]: m["expr"] for s in sm["semantic_models"] for m in s["measures"]}
    con = duckdb.connect(run1["db"], read_only=True)
    metric_total = con.execute(f"select sum({measures['excess_readmissions_positive']}) from marts.fct_hospital_readmissions").fetchone()[0]
    mart_total = con.execute("select sum(excess_readmissions) from marts.mart_state_exposure").fetchone()[0]
    assert abs(metric_total - mart_total) < 1
