"""SIMULATED CMS refresh: a new HRRP condition code appears. The worklist must still carry its readmissions, labeled as unlabeled, not drop them silently."""
from tests.dbt_helper import dbt, hosp_row, hrrp_row, query, warehouse


def build(tmp_path):
    db = warehouse(
        tmp_path,
        [hrrp_row(), hrrp_row(**{"Measure Name": "READM-30-NEWCOND-HRRP", "Predicted Readmission Rate": "30.0000", "Expected Readmission Rate": "20.0000"})],
        [hosp_row()])
    assert dbt(db, "seed").returncode == 0
    return db


def test_worklist_keeps_pairs_whose_measure_is_not_in_the_label_seed(tmp_path):
    db = build(tmp_path)
    assert dbt(db, "run", "--select", "+mart_navigator_worklist").returncode == 0
    rows = dict(query(db, "select measure_code, condition_label from marts.mart_navigator_worklist"))
    assert set(rows) == {"HF", "NEWCOND"}
    assert rows["NEWCOND"] == "Unlabeled measure"


def test_the_reconciliation_test_would_catch_a_dropped_pair(tmp_path):
    db = build(tmp_path)
    dbt(db, "run", "--select", "+mart_navigator_worklist")
    res = dbt(db, "test", "--select", "assert_worklist_reconciles_to_fact")
    assert res.returncode == 0, res.stdout[-500:]
