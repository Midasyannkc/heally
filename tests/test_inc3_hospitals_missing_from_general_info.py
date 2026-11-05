"""20 of the 3,055 hospitals in the real HRRP file are absent from the Hospital General Information file. Their readmission rows must not vanish."""
from tests.dbt_helper import dbt, hosp_row, hrrp_row, query, warehouse


def build(tmp_path):
    return warehouse(
        tmp_path,
        [hrrp_row(), hrrp_row(**{"Facility ID": "999999", "Facility Name": "NOT IN GENERAL INFO", "State": "AL"})],
        [hosp_row()])


def test_every_staged_readmission_row_reaches_the_fact_table(tmp_path):
    db = build(tmp_path)
    assert dbt(db, "run", "--select", "+fct_hospital_readmissions").returncode == 0
    staged = query(db, "select count(*) from staging.stg_hrrp")[0][0]
    fact = query(db, "select count(*) from marts.fct_hospital_readmissions")[0][0]
    assert fact == staged == 2


def test_hospitals_missing_from_general_info_are_kept_and_flagged(tmp_path):
    db = build(tmp_path)
    dbt(db, "run", "--select", "+fct_hospital_readmissions")
    rows = dict(query(db, "select facility_id, in_general_info from marts.dim_hospital"))
    assert rows == {"010001": True, "999999": False}
