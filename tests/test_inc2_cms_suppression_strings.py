"""CMS suppresses small cells with text ('N/A', 'Too Few to Report', 'Not Available') inside numeric columns. Staging must null them, not crash."""
from tests.dbt_helper import dbt, hosp_row, hrrp_row, query, warehouse


def build(tmp_path):
    db = warehouse(
        tmp_path,
        [hrrp_row(**{"Number of Discharges": "N/A", "Number of Readmissions": "Too Few to Report", "Footnote": "1"}),
         hrrp_row(**{"Measure Name": "READM-30-AMI-HRRP", "Excess Readmission Ratio": "N/A", "Predicted Readmission Rate": "N/A",
                     "Expected Readmission Rate": "N/A", "Number of Readmissions": "N/A", "Footnote": "5"}),
         hrrp_row(**{"Measure Name": "READM-30-PN-HRRP"})],
        [hosp_row(**{"Hospital overall rating": "Not Available"})])
    return db


def test_dbt_builds_when_numeric_columns_hold_cms_suppression_text(tmp_path):
    db = build(tmp_path)
    run = dbt(db, "run", "--select", "stg_hrrp", "stg_hospital_info", "dim_hospital")
    assert run.returncode == 0, run.stdout[-600:]


def test_suppressed_values_become_null_and_keep_their_reason(tmp_path):
    db = build(tmp_path)
    dbt(db, "run", "--select", "stg_hrrp", "stg_hospital_info")
    rows = {m: (d, r, e, f) for m, d, r, e, f in query(
        db, "select measure_code, discharges, readmissions, excess_readmission_ratio, footnote_code from staging.stg_hrrp")}
    assert rows["HF"] == (None, None, 1.1, "1")
    assert rows["AMI"] == (100, None, None, "5")
    assert rows["PN"] == (100, 22, 1.1, None)
    assert query(db, "select overall_star_rating from staging.stg_hospital_info")[0][0] is None
