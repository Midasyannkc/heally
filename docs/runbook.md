# Runbook: when the pipeline breaks

| Symptom | Likely cause | First action | Escalate when |
| --- | --- | --- | --- |
| `PipelineFailed` at sync, message "schema drift" | CMS renamed or removed a column | Read the `details` of the latest row in `raw._sync_log`, compare with `heally/config.py`, decide rename mapping or contract change | The change removes a column the marts depend on, or CMS announces a new format |
| dbt build fails on a cast | New suppression text in a numeric column | Inspect the failing value, extend the staging `try_cast`, add a reproduce test (see INC-2) | More than one source column is affected |
| `relationships` test fails on `dim_hospital` | A hospital in HRRP is missing from General Information | Confirm `in_general_info` is false for it (INC-3) | The count grows beyond a few dozen hospitals |
| Monitor `volume` fails | Source file lost rows | Compare row counts in `raw._sync_log`, re-download the file | CMS republished with fewer hospitals and no notice |
| `UnsafeSync` from reverse ETL | Worklist is empty or shrank by more than 50% | Look at upstream monitors first, never force without a reason | A force is needed more than once |
| Metric on the dashboard differs from the mart | Definition drift (INC-5) | Run `tests/test_inc5_metric_matches_mart.py` and the singular reconciliation tests | The definition itself is disputed, which is a business decision |

## How to communicate it

State what broke, which numbers are affected, whether anything wrong reached the CRM (the pipeline fails closed, so normally nothing did), what the fix is and when the next run will confirm it. Link the incident entry.
