# Heally: where should care navigators start after a hospital stay?

An analytics engineering project on **real CMS hospital readmission data**, built the way a care-navigation company's data team would need it: a tested ELT pipeline, a dbt model layer, governed metrics, a self-service dashboard and a worklist pushed to the tools navigators use. Built test first, with five pipeline-breaking incidents fixed through reproduce and fix commits.

**Data (click):** [HRRP, CMS 9n3s-kdb3](https://data.cms.gov/provider-data/dataset/9n3s-kdb3) and [Hospital General Information, CMS xubh-q36u](https://data.cms.gov/provider-data/dataset/xubh-q36u). The files are in `data/raw/`, the processed marts in `data/marts/` as CSV and parquet. How they were obtained and their limits: [SOURCE.md](SOURCE.md).

## The business problem

Care navigation companies such as Wellthy work with employers and health plans, and a hospital stay is the costliest moment in a family's care journey. Medicare penalizes hospitals that readmit patients more often than expected. For a navigator team the question is practical: **which hospital and condition pairs generate the most avoidable readmissions, so outreach goes there first?** For partner reviews and sales the question is: **how exposed is a partner's population, state by state?**

## Pipeline, end to end

```
CMS CSV files
   |  heally/sync.py   Fivetran-style load: text, lineage columns, idempotent, schema drift blocked, sync log
   |  heally/lambda_handler.py   S3 upload event triggers the same sync
   v
raw (DuckDB; Snowflake DDL written)
   |  dbt: staging (typed, suppression handled) -> intermediate (excess readmissions) -> marts
   |  dbt tests: 29 data tests, 3 unit tests, 4 singular reconciliations; semantic layer metrics
   v
marts: dim_hospital, dim_measure, fct_hospital_readmissions, mart_hospital_scorecard,
       mart_state_exposure, mart_navigator_worklist, mart_business_case, mart_savings_sensitivity
   |  heally/monitors.py   Metaplane-style: volume, freshness, null rate, schema drift
   |  heally/reverse_etl.py   Hightouch-style: only changed rows, refuses to wipe the destination
   v
CRM worklist (SQLite stand-in)  +  dashboard/index.html  +  notebooks/explore_readmissions.ipynb
```

`python -m heally.pipeline` runs it and **fails closed**: nothing downstream of a failed step runs, and `out/run_manifest.json` records the run.

## Results (real data)

| KPI | Value |
| --- | --- |
| Hospital-condition pairs with estimated excess readmissions | 4,316 |
| Pairs in tier A (smallest set reaching half the excess) | 457 (10.6% of pairs, 354 hospitals) |
| Share of excess readmissions in tier A | 50.0% |
| Excess readmissions per 1,000 discharges, tier A vs all pairs | 20 vs 11 |
| Estimated excess readmissions per year | about 4,082 |
| Scenario savings, tier A only, 10% averted at $15,000 each | about $3.1M per year |
| Average excess ratio by CMS star rating (sanity check) | 1 star 1.045, 3 stars 1.006, 5 stars 0.964 |
| Pipeline | 5 incidents, all gated by tests; second run is a no-op |

The savings figures are **scenarios, not findings**: the cost per readmission and the averted share are assumptions, shown as a grid in `mart_savings_sensitivity`. Excess readmissions are **estimated** from published rates, and only 8,037 of 18,330 rows allow it because CMS suppresses small cells. The data covers Medicare fee-for-service patients, not every member of a care program.

## Incidents

Incidents 1 to 3 happened on the real data. Incidents 4 and 5 are a simulated CMS refresh and a latent definition mismatch found in review; the real files do not trigger them. Each has a reproduce commit with a failing test, then a fix commit.

<!-- incidents:start -->
| # | Incident | Found by | Reproduce | Fix |
| --- | --- | --- | --- | --- |
| INC-1 | Source registry listed 14 of 38 hospital columns | first load of the real Hospital General Information file (real data) | `39e13ab` | `0e3dbec` |
| INC-2 | CMS suppression text crashed typed staging | profiling the real files, then the first dbt run (real data) | `f0326e6` | `6c68745` |
| INC-3 | 20 hospitals in HRRP are missing from General Information | profiling the real files (real data) | `12b18f5` | `7932789` |
| INC-4 | A new CMS condition code was silently dropped from the worklist | SIMULATED CMS refresh while reviewing joins; the current real files are not affected | `4f65aa4` | `e4abafa` |
| INC-5 | Governed metric disagreed with the marts | review of metric and mart definitions; LATENT, the current real files do not trigger it | `8fff0a5` | `0cd64f1` |
<!-- incidents:end -->

## Run it

```
pip install -r requirements.txt
make run          # sync, dbt build (models, tests, unit tests), monitors, reverse ETL
make test
make export dashboard notebook docs
```

## Honest limits

- DuckDB runs everything. The Snowflake DDL, Snowpipe and dbt target are written and reviewed, never run.
- Fivetran, Hightouch, Metaplane, Omni and DeepNote are represented by the same patterns built in code, not by the products. Snowplow is not covered. See [docs/coverage.md](docs/coverage.md).
- The MetricFlow command line could not load the semantic manifest (version mismatch); metrics parse in dbt and are tested against the marts.
- The Lambda handler is tested against a mocked S3, never deployed.
- No stakeholder was interviewed; [docs/requirements.md](docs/requirements.md) is a worked example.
- The CMS files came from a public GitHub mirror because the CMS site was not reachable from the build environment (see SOURCE.md).
