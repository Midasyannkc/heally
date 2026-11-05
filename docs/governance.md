# Data governance

| Area | Practice | Where |
| --- | --- | --- |
| Ownership | Every model has a description; the dashboard is declared as a dbt exposure with an owner | `dbt_heally/models/marts/schema.yml` |
| Classification | Public CMS data, no member or patient data. Nothing here is PHI. | `SOURCE.md` |
| Contracts | Source registry: a renamed or missing column blocks the load and is logged; added columns are loaded and logged | `heally/config.py`, `heally/sync.py` |
| Quality | 29 data tests, 3 unit tests, 4 singular reconciliation tests, 4 observability monitors | `dbt_heally/tests/`, `heally/monitors.py` |
| Access | Snowflake roles: TRANSFORMER writes, ANALYST reads marts only (written, not run) | `snowflake/02_stage_and_pipe.sql` |
| Freshness | dbt source freshness warns at 2 days and errors at 7 days | `dbt_heally/models/staging/sources.yml` |
| Discoverability | Static dbt docs site with lineage, a metric dictionary in the semantic layer, and a data notebook | `docs/dbt_docs.html`, `notebooks/explore_readmissions.ipynb` |
| Change control | Every incident has two commits, a failing test and then the fix; assumptions live in `dbt_project.yml` vars | `docs/incidents.md` |
| Assumptions | Cost per readmission and avertable share are not CMS data and are labeled as assumptions everywhere they appear | `dbt_heally/dbt_project.yml` |

## Pull request checklist

- New model has a description, a grain, a unique test on the grain and a relationship test to its dimension.
- Any number shown to a stakeholder reconciles to the fact table with a singular test.
- Assumptions are variables, not literals.
- A defect found in production gets a reproduce commit before the fix.
