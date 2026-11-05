"""LATENT defect, found by comparing metric and mart definitions (the current CMS vintage has no sub-volume pair with a computed excess,
so the real file does not trigger it). The governed 'excess readmissions' metric must equal the marts, which count reportable volume only."""
import json
import os

import duckdb

from tests.conftest import ROOT
from tests.dbt_helper import dbt, hosp_row, hrrp_row, warehouse


def test_semantic_measure_equals_the_state_mart_total_when_a_small_hospital_has_a_ratio(tmp_path):
    db = warehouse(
        tmp_path,
        [hrrp_row(**{"Number of Discharges": "100"}),
         hrrp_row(**{"Facility ID": "020001", "Number of Discharges": "10", "Predicted Readmission Rate": "30.0000", "Expected Readmission Rate": "20.0000"})],
        [hosp_row(), hosp_row(**{"Facility ID": "020001"})])
    assert dbt(db, "run", "--select", "+mart_state_exposure").returncode == 0
    assert dbt(db, "parse").returncode == 0
    sm = json.load(open(os.path.join(ROOT, "out", "dbt_target", "semantic_manifest.json")))
    expr = next(m["expr"] for s in sm["semantic_models"] for m in s["measures"] if m["name"] == "excess_readmissions_positive")
    con = duckdb.connect(db, read_only=True)
    metric_total = con.execute(f"select sum({expr}) from marts.fct_hospital_readmissions").fetchone()[0]
    mart_total = con.execute("select sum(excess_readmissions) from marts.mart_state_exposure").fetchone()[0]
    assert abs(metric_total - mart_total) < 0.01, (metric_total, mart_total)
