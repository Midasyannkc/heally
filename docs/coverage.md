# Coverage matrix: the Wellthy Analytics Engineer posting

Every row points at evidence in this repository. `tests/test_coverage_matrix.py` fails if a listed path does not exist.

| # | Responsibility in the posting | Evidence |
| --- | --- | --- |
| R1 | Build and maintain dbt transformations and enable self-service reporting and exploration | `dbt_heally/models/`, `dbt_heally/models/marts/semantic_layer.yml`, `dashboard/index.html`, `notebooks/explore_readmissions.ipynb` |
| R2 | Software engineering practices, efficient well-tested code, ELT performance and automation | `heally/pipeline.py`, `heally/sync.py`, `Makefile`, `.github/workflows/ci.yml` |
| R3 | Gather and translate data requirements with analysts, engineers and stakeholders | `docs/requirements.md` |
| R4 | Data quality, accessibility and governance | `docs/governance.md`, `docs/dbt_docs.html`, `dbt_heally/models/marts/schema.yml` |
| R5 | Write and maintain tests | `dbt_heally/tests/`, `dbt_heally/models/marts/unit_tests.yml`, `tests/` |
| R6 | Evaluate analytics tools | `docs/tool_evaluation.md` |
| R7 | Follow and contribute to best practices, workflows and documentation | `README.md`, `docs/adr/`, `docs/runbook.md` |
| R8 | Troubleshoot data issues, communicate findings, escalate | `docs/incidents.md`, `docs/runbook.md` |
| R9 | Work with senior team members on complex modeling and architecture | `docs/design_review.md` |

| Tool in the stack | Status | Evidence |
| --- | --- | --- |
| Fivetran | Pattern built: incremental, idempotent file sync with lineage, schema drift handling and a sync log. Not the product. | `heally/sync.py`, `tests/test_sync.py` |
| Snowflake | DDL, Snowpipe and a dbt target written, never run. All execution is on DuckDB. | `snowflake/01_raw_ddl.sql`, `dbt_heally/profiles.yml` |
| dbt | Built and run: models, tests, unit tests, docs, exposures, semantic layer. | `dbt_heally/dbt_project.yml` |
| Hightouch | Pattern built: diff-based reverse ETL with a fail-safe guard, to a SQLite stand-in for a CRM. Not the product. | `heally/reverse_etl.py`, `tests/test_reverse_etl.py` |
| Snowplow | Not built. No event data in this project; `docs/requirements.md` says where it would plug in. | none |
| DeepNote | Pattern built: an executed notebook over the marts. Not the product. | `notebooks/explore_readmissions.ipynb` |
| Metaplane | Pattern built: volume, freshness, null rate and schema drift monitors with stored results. Not the product. | `heally/monitors.py`, `tests/test_monitors.py` |
| Omni | Pattern built: governed metrics plus a filterable self-service dashboard. Not the product. | `dashboard/index.html`, `dbt_heally/models/marts/semantic_layer.yml` |
